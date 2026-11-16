#!/usr/bin/env python3
"""Architecture-aware structured pruning for Phi-3 FFN intermediate channels."""

import re
from dataclasses import dataclass

import torch
from torch import nn


@dataclass
class FFNSpec:
    name: str
    module: nn.Module
    mode: str
    old_size: int


def find_language_ffns(model):
    specs = []
    for name, module in model.named_modules():
        if not name.endswith(".mlp") or "lang_model" not in name:
            continue
        if hasattr(module, "gate_up_proj") and hasattr(module, "down_proj"):
            old = module.down_proj.in_features
            if module.gate_up_proj.out_features != old * 2:
                raise ValueError(f"Unexpected fused gate/up shape at {name}")
            specs.append(FFNSpec(name, module, "fused", old))
        elif all(hasattr(module, attr) for attr in ("gate_proj", "up_proj", "down_proj")):
            old = module.down_proj.in_features
            if module.gate_proj.out_features != old or module.up_proj.out_features != old:
                raise ValueError(f"Unexpected split gate/up shape at {name}")
            specs.append(FFNSpec(name, module, "split", old))
    specs.sort(key=lambda item: (int(re.search(r"layers\.(\d+)", item.name).group(1)) if re.search(r"layers\.(\d+)", item.name) else 9999, item.name))
    if not specs:
        raise RuntimeError("No language-model FFN modules found; inspect model.named_modules() on Vast.ai")
    sizes = {spec.old_size for spec in specs}
    if len(sizes) != 1:
        raise ValueError(f"FFN widths differ across layers: {sorted(sizes)}")
    return specs


def _tensor_mean_abs(output):
    if isinstance(output, (tuple, list)):
        output = output[0]
    return output.detach().float().abs().mean(dim=tuple(range(output.ndim - 1))).cpu()


def collect_activation_importance(model, specs, rows, infer_fn):
    stats = {spec.name: torch.zeros(spec.old_size, dtype=torch.float64) for spec in specs}
    hooks = []

    for spec in specs:
        if spec.mode == "fused":
            def hook(output, key=spec.name, width=spec.old_size):
                values = _tensor_mean_abs(output)
                if values.numel() != width * 2:
                    raise ValueError(f"Unexpected activation width for {key}: {values.numel()}")
                stats[key] += 0.5 * (values[:width].double() + values[width:].double())
            hooks.append(spec.module.gate_up_proj.register_forward_hook(lambda _m, _i, o, fn=hook: fn(o)))
        else:
            def gate_hook(output, key=spec.name):
                stats[key] += _tensor_mean_abs(output).double()
            def up_hook(output, key=spec.name):
                stats[key] += _tensor_mean_abs(output).double()
            hooks.append(spec.module.gate_proj.register_forward_hook(lambda _m, _i, o, fn=gate_hook: fn(o)))
            hooks.append(spec.module.up_proj.register_forward_hook(lambda _m, _i, o, fn=up_hook: fn(o)))

    try:
        for index, row in enumerate(rows, 1):
            infer_fn(row, timed=False)
            if index % 25 == 0:
                print(f"calibration {index}/{len(rows)}", flush=True)
    finally:
        for hook in hooks:
            hook.remove()

    return {name: (values / max(1, len(rows))).float() for name, values in stats.items()}


def _new_linear(old, in_features, out_features):
    return nn.Linear(
        in_features,
        out_features,
        bias=old.bias is not None,
        device=old.weight.device,
        dtype=old.weight.dtype,
    )


def _copy_bias(new, old, indices):
    if new.bias is not None:
        new.bias.data.copy_(old.bias.data[indices])


def activation_times_weight_norm(spec, activation):
    """Combine calibration activation magnitude with outgoing FFN weight norm."""
    if spec.mode == "fused":
        weight = spec.module.gate_up_proj.weight.detach().float()
        width = spec.old_size
        weight_norm = 0.5 * (weight[:width].norm(dim=1) + weight[width:].norm(dim=1))
    else:
        gate_norm = spec.module.gate_proj.weight.detach().float().norm(dim=1)
        up_norm = spec.module.up_proj.weight.detach().float().norm(dim=1)
        weight_norm = 0.5 * (gate_norm + up_norm)
    return activation.float() * weight_norm.cpu()


def prune_ffns(specs, importance, fraction):
    if not 0 < fraction < 1:
        raise ValueError("fraction must be between 0 and 1")
    records = []
    new_widths = set()
    with torch.no_grad():
        for spec in specs:
            k = max(1, int(round(spec.old_size * (1.0 - fraction))))
            score = activation_times_weight_norm(spec, importance[spec.name])
            keep = torch.topk(score, k=k, largest=True).indices.sort().values.to(spec.module.down_proj.weight.device)
            old_down = spec.module.down_proj
            new_down = _new_linear(old_down, k, old_down.out_features)
            new_down.weight.copy_(old_down.weight[:, keep])
            _copy_bias(new_down, old_down, torch.arange(old_down.out_features, device=keep.device))
            spec.module.down_proj = new_down
            if spec.mode == "fused":
                old_gate_up = spec.module.gate_up_proj
                fused_keep = torch.cat([keep, keep + spec.old_size])
                new_gate_up = _new_linear(old_gate_up, old_gate_up.in_features, 2 * k)
                new_gate_up.weight.copy_(old_gate_up.weight[fused_keep])
                _copy_bias(new_gate_up, old_gate_up, fused_keep)
                spec.module.gate_up_proj = new_gate_up
            else:
                for attr in ("gate_proj", "up_proj"):
                    old_proj = getattr(spec.module, attr)
                    new_proj = _new_linear(old_proj, old_proj.in_features, k)
                    new_proj.weight.copy_(old_proj.weight[keep])
                    _copy_bias(new_proj, old_proj, keep)
                    setattr(spec.module, attr, new_proj)
            new_widths.add(k)
            records.append({"layer": spec.name, "old_units": spec.old_size, "new_units": k, "removed_fraction": 1.0 - k / spec.old_size})
    if len(new_widths) != 1:
        raise ValueError(f"Unexpected new FFN widths: {sorted(new_widths)}")
    return records, next(iter(new_widths))


def update_intermediate_size(model, new_width):
    updated = []
    objects = [model, getattr(model, "config", None)]
    if hasattr(model, "vlm"):
        objects.extend([model.vlm, getattr(model.vlm, "config", None), getattr(model.vlm, "lang_model", None)])
        if hasattr(model.vlm, "lang_model"):
            objects.append(getattr(model.vlm.lang_model, "config", None))
    for obj in objects:
        if obj is not None and hasattr(obj, "intermediate_size"):
            obj.intermediate_size = new_width
            updated.append(type(obj).__name__)
        if obj is not None and hasattr(obj, "text_config") and hasattr(obj.text_config, "intermediate_size"):
            obj.text_config.intermediate_size = new_width
            updated.append(type(obj.text_config).__name__)
    return sorted(set(updated))

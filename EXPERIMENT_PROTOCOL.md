# Cost-efficient compression experiment protocol

The baseline is complete. The compression runs should start from the same original BLIP-3 checkpoint and should not depend on temporary pruned checkpoints from earlier runs.

## Data partitions

Keep the partitions frozen and record their question IDs:

- calibration: 256 questions, used only to estimate pruning importance;
- pilot: 100 questions, used as an early validation gate;
- evaluation: 5,040 questions, used for final VQAv2 accuracy;
- timing: 500 questions from the evaluation protocol, used for three timed passes.

The calibration questions must not be used to calculate reported accuracy. The same prompt, decoding settings, and seed must be used for every configuration.

## Per-configuration workflow

The worker must perform the following in one server session:

1. Load the original baseline model.
2. Apply pruning and/or quantization in memory.
3. Save a temporary checkpoint only if required for the reload test.
4. Reload the temporary checkpoint and run one smoke-test inference.
5. Run the 100-question pilot.
6. If the pilot completes, run the 5,040-question evaluation.
7. Run ten warm-ups and three timing passes over the fixed timing subset.
8. Save predictions, metrics, logs, and completion status.
9. Delete the temporary model and clear GPU memory.
10. Continue to the next configuration.

Temporary checkpoints are not retained by default. The original model is the only model that must remain on persistent storage. A final selected model may be exported after the experiment is complete.

## Required output

Each configuration gets its own directory:

```text
outputs/experiments/<experiment_id>/
├── config.json
├── environment.json
├── predictions.jsonl
├── accuracy_metrics.json
├── efficiency_metrics.json
├── failures.jsonl
├── run.log
└── completion.json
```

`completion.json` is written only after every required stage succeeds. The grid runner uses it to skip completed configurations after a reconnect or server restart.

## Gating

Do not run the full evaluation for a configuration that failed to construct, save, reload, generate one answer, or complete the pilot. Preserve the error and mark the configuration as failed.

The final thesis grid contains fourteen compressed configurations: nine component-level runs (three components at 10%, 20%, and 30%), three full-model runs, one INT8 run, and one combined full-model-30%-plus-INT8 run. The repository initially enables only `prune_lm_10` because the current worker validates language-model FFN pruning first. Enable the other language-model levels after the first pilot passes, then implement and validate the visual-encoder, connector, and full-model workers before enabling their configurations.

## Vast.ai lifecycle

Use a persistent volume for the original model, data, source checkout, and outputs. Run the grid inside `tmux`. After each completed configuration, copy `outputs/` to local storage. Stop or delete the instance only after the output backup has been checked.

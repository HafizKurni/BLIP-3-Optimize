#!/usr/bin/env python3
"""Copy only the COCO images referenced by a VQAv2 question subset.

This script deliberately does not open or decode image contents. It reads the
question/annotation JSON files, checks source filenames with filesystem
metadata, and copies the required files only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--source-images", type=Path, required=True)
    p.add_argument("--dataset-dir", type=Path, required=True)
    p.add_argument("--questions", type=Path, required=True)
    p.add_argument("--annotations", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, default=None)
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def load_records(path: Path, key: str) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    records = data.get(key)
    if not isinstance(records, list):
        raise ValueError(f"{path} does not contain a list named {key!r}")
    return records


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    args = parse_args()
    questions = load_records(args.questions, "questions")
    annotations = load_records(args.annotations, "annotations")

    question_ids = {r["question_id"] for r in questions}
    annotation_ids = {r["question_id"] for r in annotations}
    if question_ids != annotation_ids:
        raise ValueError(
            f"Question/annotation IDs differ: questions-only={len(question_ids - annotation_ids)}, "
            f"annotations-only={len(annotation_ids - question_ids)}"
        )

    question_images = {r["question_id"]: r["image_id"] for r in questions}
    annotation_images = {r["question_id"]: r["image_id"] for r in annotations}
    mismatches = [qid for qid in question_ids if question_images[qid] != annotation_images[qid]]
    if mismatches:
        raise ValueError(f"Question/annotation image_id mismatch for {len(mismatches)} records")

    image_ids = sorted(set(question_images.values()))
    output_dir = args.output_dir or args.dataset_dir / "images" / "val2014"
    manifest_path = args.dataset_dir / "selected_image_manifest.jsonl"
    missing: list[int] = []
    entries: list[dict] = []

    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    for image_id in image_ids:
        filename = f"COCO_val2014_{image_id:012d}.jpg"
        source = args.source_images / filename
        destination = output_dir / filename
        if not source.is_file():
            missing.append(image_id)
            continue

        stat = source.stat()  # metadata only; image is not decoded
        entry = {
            "image_id": image_id,
            "filename": filename,
            "source": str(source),
            "destination": str(destination),
            "source_bytes": stat.st_size,
            "source_mtime_ns": stat.st_mtime_ns,
        }
        if not args.dry_run:
            shutil.copy2(source, destination)
            entry["sha256"] = sha256_file(destination)
        entries.append(entry)

    if missing:
        raise FileNotFoundError(
            f"{len(missing)} of {len(image_ids)} required images are missing. "
            f"First IDs: {missing[:10]}"
        )

    if not args.dry_run:
        with manifest_path.open("w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Questions: {len(questions)}")
    print(f"Unique images: {len(image_ids)}")
    print(f"Images copied: {0 if args.dry_run else len(entries)}")
    print(f"Output directory: {output_dir}")
    if not args.dry_run:
        print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()

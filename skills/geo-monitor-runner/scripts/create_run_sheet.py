#!/usr/bin/env python3
"""Create a manual ChatGPT GEO monitoring run sheet from a prompt set."""

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


COLUMNS = [
    "run_id",
    "response_id",
    "row_id",
    "run_iteration",
    "topic_id",
    "topic",
    "prompt_id",
    "prompt",
    "platform",
    "market",
    "language",
    "persona",
    "brand_type",
    "intent_stage",
    "run_mode",
    "model_or_surface",
    "account_context",
    "run_status",
    "raw_answer",
    "answer_url",
    "screenshot_path",
    "operator",
    "run_timestamp",
    "notes",
]


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_platform(value):
    raw = (value or "").strip()
    lowered = raw.lower().replace("-", " ")
    aliases = {"gpt", "chat gpt", "chatgpt", "openai chatgpt", "openai"}
    if not raw:
        return "ChatGPT"
    if lowered in aliases:
        return "ChatGPT"
    raise ValueError(f"Only ChatGPT is supported by this MVP, got: {raw}")


def field_value(intake, name, default=None):
    if not isinstance(intake, dict):
        return default
    client_intake = intake.get("client_intake", intake)
    item = client_intake.get(name) if isinstance(client_intake, dict) else None
    if isinstance(item, dict):
        value = item.get("value")
    else:
        value = item
    if value in (None, "", []):
        return default
    if isinstance(value, list):
        return value[0] if value else default
    return value


def slug(text):
    text = (text or "geo").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "geo"


def first_prompt_default(prompts, key, default=""):
    for prompt in prompts:
        value = prompt.get(key)
        if value:
            return value
    return default


def flatten_prompts(prompt_set):
    prompts = []
    groups = prompt_set.get("prompt_groups", [])
    for group_index, group in enumerate(groups, start=1):
        topic_id = group.get("topic_id") or f"T{group_index:02d}"
        topic = group.get("topic", "")
        for prompt_index, item in enumerate(group.get("prompts", []), start=1):
            prompt_text = item.get("prompt", "")
            if not prompt_text:
                continue
            prompt_id = item.get("prompt_id") or f"P{len(prompts) + 1:03d}"
            prompts.append(
                {
                    "topic_id": item.get("topic_id") or topic_id,
                    "topic": item.get("topic") or topic,
                    "prompt_id": prompt_id,
                    "prompt": prompt_text,
                    "platform": item.get("platform", ""),
                    "market": item.get("market", ""),
                    "language": item.get("language", ""),
                    "persona": item.get("persona", ""),
                    "brand_type": item.get("brand_type", ""),
                    "intent_stage": item.get("intent_stage", ""),
                }
            )
    if not prompts and isinstance(prompt_set.get("prompts"), list):
        for item in prompt_set["prompts"]:
            prompt_text = item.get("prompt", "") if isinstance(item, dict) else ""
            if prompt_text:
                prompts.append(
                    {
                        "topic_id": item.get("topic_id", ""),
                        "topic": item.get("topic", ""),
                        "prompt_id": item.get("prompt_id") or f"P{len(prompts) + 1:03d}",
                        "prompt": prompt_text,
                        "platform": item.get("platform", ""),
                        "market": item.get("market", ""),
                        "language": item.get("language", ""),
                        "persona": item.get("persona", ""),
                        "brand_type": item.get("brand_type", ""),
                        "intent_stage": item.get("intent_stage", ""),
                    }
                )
    return prompts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-set", required=True, help="Path to prompt_set.json")
    parser.add_argument("--client-intake", help="Optional path to client_intake.json")
    parser.add_argument("--run-config", help="Optional path to run_config.json")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    parser.add_argument("--run-id", help="Override run_id")
    args = parser.parse_args()

    prompt_set = load_json(args.prompt_set)
    client_intake = load_json(args.client_intake) if args.client_intake else {}
    run_config = load_json(args.run_config) if args.run_config else {}
    prompts = flatten_prompts(prompt_set)
    if not prompts:
        print("No prompts found in prompt set.", file=sys.stderr)
        return 1

    platform = normalize_platform(run_config.get("platform") or first_prompt_default(prompts, "platform", "ChatGPT"))
    for prompt in prompts:
        if prompt.get("platform"):
            normalize_platform(prompt["platform"])

    market = (
        run_config.get("market")
        or field_value(client_intake, "target_countries_or_regions")
        or first_prompt_default(prompts, "market")
    )
    language = (
        run_config.get("language")
        or field_value(client_intake, "languages")
        or first_prompt_default(prompts, "language")
    )
    brand_name = field_value(client_intake, "brand_name", "")
    website_domain = field_value(client_intake, "website_domain", "")
    model_or_surface = run_config.get("model_or_surface", "ChatGPT default")
    account_context = run_config.get("account_context", "")
    operator = run_config.get("operator", "")
    runs_per_prompt = int(run_config.get("runs_per_prompt", 1))
    if runs_per_prompt < 1:
        raise ValueError("runs_per_prompt must be >= 1")

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    run_id = args.run_id or run_config.get("run_id")
    if not run_id:
        run_id = f"{slug(brand_name)}-{slug(platform)}-{slug(market)}-{today}"

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    run_sheet_path = output_dir / "run_sheet.csv"
    manifest_path = output_dir / "run_manifest.json"

    rows = []
    response_counter = 1
    for prompt in prompts:
        for iteration in range(1, runs_per_prompt + 1):
            row_id = f"ROW{response_counter:04d}"
            rows.append(
                {
                    "run_id": run_id,
                    "response_id": f"R{response_counter:04d}",
                    "row_id": row_id,
                    "run_iteration": iteration,
                    "topic_id": prompt.get("topic_id", ""),
                    "topic": prompt.get("topic", ""),
                    "prompt_id": prompt.get("prompt_id", ""),
                    "prompt": prompt.get("prompt", ""),
                    "platform": platform,
                    "market": prompt.get("market") or market or "",
                    "language": prompt.get("language") or language or "",
                    "persona": prompt.get("persona", ""),
                    "brand_type": prompt.get("brand_type", ""),
                    "intent_stage": prompt.get("intent_stage", ""),
                    "run_mode": "manual_sheet",
                    "model_or_surface": model_or_surface,
                    "account_context": account_context,
                    "run_status": "pending",
                    "raw_answer": "",
                    "answer_url": "",
                    "screenshot_path": "",
                    "operator": operator,
                    "run_timestamp": "",
                    "notes": "",
                }
            )
            response_counter += 1

    with run_sheet_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "client": {"brand_name": brand_name or "", "website_domain": website_domain or ""},
        "platform": platform,
        "market": market or "",
        "language": language or "",
        "run_mode": "manual_sheet",
        "runs_per_prompt": runs_per_prompt,
        "prompt_count": len(prompts),
        "expected_response_count": len(rows),
        "model_or_surface": model_or_surface,
        "account_context": account_context,
        "operator": operator,
        "input_files": [str(Path(args.prompt_set))] + ([str(Path(args.client_intake))] if args.client_intake else []),
        "output_files": [str(run_sheet_path), str(manifest_path)],
        "quality_rules": [
            "Run every row in ChatGPT only.",
            "Do not modify prompts.",
            "Paste raw ChatGPT answers exactly into raw_answer.",
            "Set failed/skipped/needs_retry rows with notes.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"run_sheet": str(run_sheet_path), "run_manifest": str(manifest_path), "rows": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

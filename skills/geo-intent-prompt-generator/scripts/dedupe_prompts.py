#!/usr/bin/env python3
"""Deduplicate prompt-set JSON from stdin or a file path.

The script preserves the first occurrence of each near-duplicate prompt.
It accepts either the full output schema or a plain list of prompt objects.
"""

import json
import re
import sys
from difflib import SequenceMatcher


def normalize(text):
    text = (text or "").lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\b(the|a|an|for|to|of|and|or|in|on|with)\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def iter_prompt_objects(data):
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "prompt" in item:
                yield item
        return
    for group in data.get("prompt_groups", []) if isinstance(data, dict) else []:
        for item in group.get("prompts", []) if isinstance(group, dict) else []:
            if isinstance(item, dict):
                yield item


def is_duplicate(norm, seen, threshold=0.92):
    if not norm:
        return False
    if norm in seen:
        return True
    return any(SequenceMatcher(None, norm, old).ratio() >= threshold for old in seen)


def dedupe(data):
    seen = []
    removed = []
    if isinstance(data, list):
        kept = []
        for item in data:
            norm = normalize(item.get("prompt") if isinstance(item, dict) else "")
            if is_duplicate(norm, seen):
                removed.append(item)
            else:
                seen.append(norm)
                kept.append(item)
        return {"prompts": kept, "removed": removed}

    for group in data.get("prompt_groups", []) if isinstance(data, dict) else []:
        prompts = group.get("prompts", []) if isinstance(group, dict) else []
        kept = []
        for item in prompts:
            norm = normalize(item.get("prompt") if isinstance(item, dict) else "")
            if is_duplicate(norm, seen):
                removed.append(item)
            else:
                seen.append(norm)
                kept.append(item)
        group["prompts"] = kept
    if isinstance(data, dict):
        data.setdefault("qa_report", {})["dedupe_removed_count"] = len(removed)
        data.setdefault("qa_report", {})["dedupe_removed_prompts"] = [
            x.get("prompt", "") for x in removed if isinstance(x, dict)
        ]
    return data


def main():
    raw = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    data = json.loads(raw)
    print(json.dumps(dedupe(data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

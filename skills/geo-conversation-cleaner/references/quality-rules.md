# Quality Rules

Assign one `answer_quality_status` per record and zero or more `quality_flags`.

## Status Values

- `analyzable`: normal answer that can enter downstream analysis.
- `empty_answer`: completed run but answer is empty.
- `failed_run`: upstream run status is failed.
- `skipped_run`: upstream run status is skipped.
- `needs_retry`: upstream run status is pending or needs_retry.
- `refusal_or_cannot_answer`: answer clearly refuses or says it cannot answer.
- `non_answer`: answer is login, access, network, system, or other non-content output.
- `too_short`: completed answer is too short for reliable analysis.
- `duplicate_answer`: exact duplicate of a prior analyzable answer.
- `unsupported_platform`: platform is not ChatGPT.

## Flags

Common flags:

- `missing_raw_answer`
- `failed_status`
- `skipped_status`
- `pending_status`
- `login_or_access_issue`
- `network_or_system_error`
- `possible_refusal`
- `too_short`
- `duplicate_text`
- `unsupported_platform`
- `missing_prompt_id`
- `missing_topic_id`
- `missing_timestamp`

## MVP Decision Rules

Apply in this order:

1. Non-ChatGPT platform -> `unsupported_platform`, not analyzable.
2. `failed` -> `failed_run`, not analyzable.
3. `skipped` -> `skipped_run`, not analyzable.
4. `pending` or `needs_retry` -> `needs_retry`, not analyzable.
5. Completed but empty -> `empty_answer`, not analyzable.
6. Login/access/system/network error -> `non_answer`, not analyzable.
7. Clear refusal/cannot-answer pattern -> `refusal_or_cannot_answer`, not analyzable.
8. Completed answer below 80 characters -> `too_short`, not analyzable.
9. Later exact duplicate of an analyzable answer -> `duplicate_answer`, not analyzable.
10. Otherwise -> `analyzable`.

The first exact duplicate in a group remains analyzable. Later duplicates are excluded from analysis in the MVP.

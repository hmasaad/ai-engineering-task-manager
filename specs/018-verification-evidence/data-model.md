# Data Model: Verification Evidence and Trace Gaps

## Criterion evidence

One row for the current verification of one acceptance criterion. The row exists only while that verification is current.

| Field | Rule |
|---|---|
| `criterion_id` | Primary key. References `acceptance_criterion(id)` with `ON DELETE CASCADE`. |
| `method` | Not null. `length(trim(method)) > 0`. Stored after surrounding spaces are removed. |
| `run_identifier` | Not null. `length(trim(run_identifier)) > 0`. Stored after surrounding spaces are removed. |

No second row for the same criterion. A later verification replaces the method and the identifier. `clear_verification` deletes the row. Removing the criterion deletes the row through the foreign key.

The task criterion payload adds `method` and `run_identifier`. Both are null when the criterion is Unverified or when no evidence row exists. While Verified and the row exists, both are the stored text.

## Trace gaps

Not stored. Derived when the gap analysis is read.

`tasks_without_requirement`: every task with no `requirement_task` row, ordered by task id. Each item has `id`, `title`, and `status`.

`criteria_without_verification`: every acceptance criterion that is not Verified under the existing rule, ordered by criterion id. Each item has `id`, `task_id`, `task_title`, and `text`.

Reading either list does not insert, update, or delete a row.

## Unchanged

`acceptance_criterion` keeps its verification columns. `requirement`, `requirement_task`, `requirement_criterion`, `requirement_check`, and `verification_run` are unchanged. A requirement's `missing` phrases stay the phrases already defined.

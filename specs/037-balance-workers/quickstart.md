# Quickstart: Work Stealing, Backpressure, and Load Balancing

From the repository root:

```bash
.venv/bin/pytest tests/unit/test_balance_workers.py tests/contract/test_balance_workers_api.py
.venv/bin/pytest
```

The first command covers a balanced placement, a full queue, a rolled-back placement, a steal, a rolled-back steal, and the page. The second command confirms the existing suite stays green.

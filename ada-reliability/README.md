# ada-reliability

Phase-1 reliability layer for Ada. Models propose. This code authorizes. Independent validators prove live state.

Run tests:

```bash
cd ada-reliability
python3 -m pytest tests -v
```

MariaDB migrations live in `sql/mariadb/` and are additive `ada_*` tables. Do not apply them without the migration runbook and a tested backup.

Agiflow projection (`agiflow_steward.py`, AAX-12) is a coordination outbox. It does not own jobs, schedules or leases. Review/Done require HMAC-issued evidence and a one-time human close grant; caller-constructed proof is rejected.


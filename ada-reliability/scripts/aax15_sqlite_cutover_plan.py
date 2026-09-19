#!/usr/bin/env python3
"""Build a READ-ONLY AAX-15 SQLite -> MariaDB cutover plan.\n\nThis does not apply SQL, mutate the SQLite source, stop services, or switch\nruntime authority. It refuses an unsafe snapshot (inflight/retryable/queued or\nunknown lifecycle rows) so operators cannot accidentally plan a dual-authority\ncutover while replay work is active.\n"""

#!/usr/bin/env python3
import os
raise SystemExit(0 if os.environ.get("TELEGRAM_BOT_TOKEN","").strip() else 1)

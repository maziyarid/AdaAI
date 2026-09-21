# AdaLLMbot VPS Runtime

Repository-owned source for Ada's bounded Telegram interface.

## Authority boundaries

- Telegram is transport, never runtime truth.
- Git is code truth.
- Agiflow is durable coordination memory, not scheduler authority.
- VPS/DB/queues are runtime truth.
- Ordinary chat has no shell, SQL, deployment, database, or arbitrary MCP execution authority.
- /tasks and /blocked use a loopback-only, hard-coded read path in the existing Mistral worker; the Telegram process never receives the Agiflow API key.
- Raw Telegram history is not training data. Only explicit /feedback enters the review queue.

## Production layout

- /opt/ada-telegram-bot
- /var/lib/ada-telegram-bot
- /etc/ada-telegram-bot.env
- ada-telegram-bot.service
- ada-bot-health
- ada-send-alert
- ada-botctl
- ada-bot-set-token

The BotFather token must be rotated and entered through the hidden-input installer on an operator-controlled terminal. Never put it in Git, Agiflow, prompts, logs, or an AI tool call.

## Qalam release

The deployed runtime includes qalam-release.json copied from skills/qalam/RELEASE.json at build/deploy time. Feedback records bind to the resolved router + Bible release label. The bot must not maintain an independent hard-coded Qalam version.

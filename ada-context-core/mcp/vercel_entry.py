"""Draft internal-only ASGI export. Public MCP authentication is not configured."""
from server import mcp

# Separate entrypoint leaves the existing standalone run() transport unchanged.
app = mcp.http_app(path='/mcp', stateless_http=True)

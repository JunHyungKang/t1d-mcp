import asyncio
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
from mcp.server.sse import SseServerTransport
from mcp.server import Server
from contextlib import asynccontextmanager

# Import the initialized FastMCP instance
from src.main import mcp

# Create a standard MCP Server instance to bridge FastMCP tools?
# Or uses FastMCP capabilities?
# FastMCP usually manages its own Server.
# We will create a robust adapter here.

async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp.run_session(streams[0], streams[1])

async def handle_messages(request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

# For now, simplistic approach:
# If FastMCP doesn't support run_session easily available externally, 
# we might need to rely on its internal server or create a new server and register tools.
# Let's assume for this competition that we can use mcp._server or similar 
# IF FastMCP is wrapper. 
# BUT, simplest is to re-define tools if FastMCP is opaque. 
# Let's check main.py imports.

# Strategy: FastMCP is high level. Let's make src/sse.py the app entry point.
# We will define a Starlette app.

sse = SseServerTransport("/messages")

async def sse_endpoint(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        # We need to run the MCP server session here.
        # FastMCP usually has method to run with streams.
        # Let's assume mcp._server is the underlying Server object provided by mcp SDK
        # This is a safe bet for python SDK structure.
        await mcp._server.run(streams[0], streams[1], mcp._server.create_initialization_options())

async def messages_endpoint(request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

routes = [
    Route("/sse", endpoint=sse_endpoint),
    Route("/messages", endpoint=messages_endpoint, methods=["POST"]),
]

app = Starlette(routes=routes)

# mcp-dataset-scalyr

mcp-dataset-scalyr is a Model Context Protocol (MCP) for dataset scalyr log.

It created based on kmcp frameworks.

## Project Structure

```
src/
├── tools/              # Tool implementations (one file per tool)
│   ├── echo.py         # Example echo tool
│   └── __init__.py     # Auto-generated tool registry
├── core/               # Dynamic loading framework
│   ├── server.py       # Dynamic MCP server
│   └── utils.py        # Shared utilities
└── main.py             # Entry point
kmcp.yaml               # Configuration file
tests/                  # Generated tests
```

## Quick Start

### Option 1: Local Development (with Python/uv)

1. **Install Dependencies**:
   ```bash
   uv sync
   ```

2. **Run the Server**:
   ```bash
   # Stdio mode (default MCP transport)
   uv run python src/main.py
   
   # HTTP mode with WebSocket MCP endpoint
   uv run python src/main.py --transport http
   
   # HTTP mode with custom host/port
   uv run python src/main.py --transport http --host 0.0.0.0 --port 8080
   ```

3. **Using uv Scripts**:
   ```bash
   # Development mode (HTTP on port 3000)
   uv run dev
   
   # HTTP mode
   uv run dev-http
   
   # Stdio mode
   uv run start
   ```

4. **Add New Tools**:
   ```bash
   # Create a new tool (no tool types needed!)
   kmcp add-tool weather
   
   # The tool file will be created at src/tools/weather.py
   # Edit it to implement your tool logic
   ```

### Option 2: Docker-Only Development (no local Python/uv required)

1. **Build Docker Image**:
   ```bash
   kmcp build --verbose
   ```

2. **Run in Container**:
   ```bash
   docker run -i mcp-dataset-scalyr:latest
   ```

3. **Deploy to Kubernetes**:
   ```bash
   kmcp deploy mcp --apply
   ```

4. **Add New Tools**:
   ```bash
   # Create a new tool
   kmcp add-tool weather
   
   # Edit the tool file, then rebuild
   kmcp build
   ```

## HTTP Transport Mode

The server supports running in HTTP mode for development and integration purposes.

### Starting in HTTP Mode

```bash
# Command line flag
python src/main.py --transport http

# Environment variable
MCP_TRANSPORT_MODE=http python src/main.py

# Custom host and port
python src/main.py --transport http --host localhost --port 8080
```
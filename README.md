# Senso API MCP Server

A Model Context Protocol (MCP) server implementation for the Senso API, allowing Claude to interact with your Senso knowledge base through Claude Desktop.

This server enables Claude to:
- Add raw content to your knowledge base
- Search existing content
- Generate new content based on your knowledge base

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
- Claude Desktop application

## Installation

1. Clone this repository:
   ```bash
   git clone git@github.com:AI-Template-SDK/api-mcp-server.git
   cd api-mcp-server
   ```

2. Create a virtual environment and install dependencies using `uv`:

   ```bash
   # Create and activate virtual environment
   uv venv
   
   # On macOS/Linux
   source .venv/bin/activate
   
   # On Windows
   .venv\Scripts\activate
   
   # Install dependencies from pyproject.toml
   uv pip install -e .
   ```

## Configuration

### API Key

The server uses a Senso API key for authentication. You need to edit the API key in the `server.py` file:

1. Open `server.py` in your text editor
2. Locate the line: `API_KEY = "tgr_YOUR_API_KEY"`
3. Replace it with your own Senso API key

### Claude Desktop Configuration

To use this MCP server with Claude Desktop, you need to add it to Claude's configuration:

1. Locate or create the Claude Desktop configuration file:

   - On macOS:
     ```bash
     mkdir -p ~/Library/Application\ Support/Claude
     code ~/Library/Application\ Support/Claude/claude_desktop_config.json
     ```

   - On Windows:
     ```powershell
     if (-not (Test-Path $env:AppData\Claude)) { mkdir $env:AppData\Claude }
     code $env:AppData\Claude\claude_desktop_config.json
     ```

2. Add the Senso MCP server configuration to the file:

   ```json
   {
       "mcpServers": {
           "senso": {
               "command": "uv",
               "args": [
                   "--directory",
                   "/ABSOLUTE/PATH/TO/api-mcp-server",
                   "run",
                   "server.py"
               ]
           }
       }
   }
   ```

   For Windows, use the appropriate path format:
   ```json
   {
       "mcpServers": {
           "senso": {
               "command": "uv",
               "args": [
                   "--directory",
                   "C:\\ABSOLUTE\\PATH\\TO\\api-mcp-server",
                   "run",
                   "server.py"
               ]
           }
       }
   }
   ```

   > ⚠️ **Important**: Replace the path with the absolute path to your cloned repository.

3. Restart Claude Desktop to apply the changes.

## Using the MCP Tools with Claude

After setting up the server and configuring Claude Desktop, you can use the tools through natural language interaction:

### Adding Content

Ask Claude:
```
Please add this information to my knowledge base:
Title: Introduction to MCP
Summary: A brief overview of the Model Context Protocol
Text: The Model Context Protocol (MCP) allows large language models to interact with external tools and data sources. It enables Claude to perform actions like retrieving information, accessing files, and executing operations through a standardized interface.
```

### Searching Content

Ask Claude:
```
Can you search my knowledge base for information about "MCP"?
```

### Generating Content

Ask Claude:
```
Using my knowledge base, please generate a tutorial about AI assistants and save it to my knowledge base.
```

## Troubleshooting

### Checking Logs

If you encounter issues, check Claude Desktop logs:

- macOS: `~/Library/Logs/Claude/mcp-server-senso.log`
- Windows: `%APPDATA%\Claude\Logs\mcp-server-senso.log`

### Common Issues

- **No tools showing in Claude**: Make sure Claude Desktop has been restarted and the configuration file is properly formatted.
- **API Key Issues**: If you need to update your API key, edit it directly in the `server.py` file.
- **Path Problems**: Ensure you've used absolute paths in the Claude configuration, not relative paths.

### Updating uv

If you encounter issues with `uv`, make sure you have the latest version:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

---

Made for integration with [Senso API](https://sdk.senso.ai)
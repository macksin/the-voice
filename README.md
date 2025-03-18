# the-voice
A simple application for TTS and utilities

![Application Interface](docs/app-interface.png)

## Main Features

1. **Voice Selection** (Left Panel)
   - Multiple TTS voices available
   - Quick access to default Ava voice
   - Priority sorting for pt-BR and en-US voices

2. **Text Input and Processing** (Center Panel)
   - Large text input area
   - Text cleanup utilities:
     - Fix Line Breaks: Removes unnecessary line breaks, perfect for cleaning up text copied from PDFs or emails.
     - Fix Hyphenation: Fixes hyphenated words split across lines, ensuring smooth reading.
     - Fix Spaces: Normalizes spacing, removing extra spaces and ensuring consistent formatting.
     - Fix All: Applies all fixes in one go, saving time and effort.
     - Fix Selected: Applies fixes to selected text only, giving you precise control over text formatting.
   - Real-time audio preview
   - Download option for generated audio
   - Subtitle display

3. **History** (Right Panel)
   - Keeps track of previous conversions
   - Quick access to past audio files
   - Download option for each entry

4. **Processing Feedback**
   - Visual loading indicators
   - Progress overlay during conversion
   - Error handling with user notifications

## Requirements
- Python 3.8+
- pip

## Installation and Running

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/the-voice.git
    cd the-voice
    ```

2. Create and activate a virtual environment (recommended):
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # or
    .\venv\Scripts\activate  # On Windows
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Run the application:
    ```sh
    python app.py
    ```

The application will open in your default web browser. If it doesn't open automatically, navigate to `http://localhost:5000`.

### Troubleshooting

- If you get permission errors, try running pip with sudo: `sudo pip install -r requirements.txt`
- Make sure you have Python 3.8 or higher installed: `python --version`
- For audio playback issues, ensure your system's audio output is properly configured


Here’s a step-by-step guide to create a simple Proof of Concept (PoC) using Anthropic’s Model Context Protocol (MCP) with your own API and tools, even without access to Claude Desktop. Since you have your own API with tools, we’ll leverage MCP to expose those tools and integrate them with Anthropic’s Claude model via the API. The solution involves setting up an MCP server and writing a basic script to simulate the client functionality that Claude Desktop would normally provide.

---

## Overview
MCP is an open protocol from Anthropic that standardizes how AI applications connect to external data sources and tools. Normally, Claude Desktop acts as an MCP client, but since you don’t have access to it, we’ll create a simple workaround. You’ll:
1. Build an MCP server to expose your API’s tools.
2. Write a Python script to interact with the Claude API and communicate with your MCP server.

This PoC will demonstrate how Claude can use your API tools through MCP.

---

## Requirements
- **Anthropic API Key**: You’ll need this to access Claude via the API.
- **Python**: For both the MCP server and the client script.
- **Libraries**: Install the Anthropic SDK (`anthropic`), the Anthropic MCP SDK (if available separately), and `websockets` for WebSocket communication.

Run this to install the necessary libraries:
```bash
pip install anthropic websockets
```

---

## Step-by-Step Guide

### 1. Set Up an MCP Server
The MCP server will wrap your API tools and make them accessible via the MCP protocol.

#### What You’ll Do
- Use Anthropic’s Python SDK (or a reference MCP server example) to create a server.
- Define your API tools in MCP format (name, description, input schema).
- Configure the server to use WebSocket transport for easy communication.

#### Example MCP Server Code
Here’s a basic example (adapt it to your API):

```python
import json
import asyncio
import websockets
from your_api_module import fetch_data  # Replace with your API logic

# Define your tools
TOOLS = [
    {
        "name": "get_data",
        "description": "Fetch data from my company API",
        "input_schema": {
            "type": "object",
            "properties": {
                "param": {"type": "string", "description": "Parameter for the API"}
            },
            "required": ["param"]
        }
    }
]

# Handle tool invocation
async def handle_tool(websocket, request):
    method = request.get("method")
    if method == "invokeTool":
        tool_name = request["params"]["name"]
        args = request["params"]["arguments"]
        
        if tool_name == "get_data":
            # Call your API
            result = fetch_data(args["param"])  # Replace with your API call
            response = {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": result
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": request["id"],
                "error": {"code": -32601, "message": "Tool not found"}
            }
        
        await websocket.send(json.dumps(response))

# WebSocket server
async def mcp_server(websocket, path):
    async for message in websocket:
        request = json.loads(message)
        await handle_tool(websocket, request)

# Start the server
start_server = websockets.serve(mcp_server, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
print("MCP Server running on ws://localhost:8765")
asyncio.get_event_loop().run_forever()
```

#### Notes
- Replace `fetch_data` with your actual API call logic.
- This server listens on `ws://localhost:8765`. Adjust the port if needed.
- Run this script in a separate terminal or process.

### 2. Create a Client Script
Since you don’t have Claude Desktop, this script will act as the MCP client, bridging the Claude API and your MCP server.

#### What You’ll Do
- Use the Anthropic SDK to send user queries to Claude.
- Define the same tools in the API request as in your MCP server.
- Handle tool use requests by sending JSON-RPC messages to the MCP server via WebSocket.
- Send tool results back to Claude and display the response.

#### Example Client Script
```python
import asyncio
import json
import websockets
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

# Initialize Anthropic client
client = Anthropic(api_key="your-anthropic-api-key")  # Replace with your API key

# Define tools (must match MCP server)
TOOLS = [
    {
        "name": "get_data",
        "description": "Fetch data from my company API",
        "input_schema": {
            "type": "object",
            "properties": {
                "param": {"type": "string"}
            },
            "required": ["param"]
        }
    }
]

# Function to call MCP server
async def call_mcp_tool(tool_name, tool_args):
    async with websockets.connect("ws://localhost:8765") as websocket:
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "invokeTool",
            "params": {"name": tool_name, "arguments": tool_args}
        }
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        return json.loads(response)["result"]

# Main PoC function
async def run_poc():
    user_input = "Get the latest data for 'example_param'"  # Hardcoded for simplicity
    print(f"User: {user_input}")

    # Initial message to Claude
    message = client.messages.create(
        model="claude-3-opus-20240229",  # Or another Claude model
        max_tokens=1000,
        tools=TOOLS,
        messages=[
            {"role": "user", "content": f"{HUMAN_PROMPT}{user_input}{AI_PROMPT}"}
        ]
    )

    # Check if Claude wants to use a tool
    for content in message.content:
        if content.type == "tool_use":
            tool_name = content.name
            tool_args = content.input
            print(f"Claude wants to use tool: {tool_name} with args: {tool_args}")

            # Call the MCP server
            tool_result = await call_mcp_tool(tool_name, tool_args)
            print(f"Tool result: {tool_result}")

            # Send tool result back to Claude
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                tools=TOOLS,
                messages=[
                    {"role": "user", "content": f"{HUMAN_PROMPT}{user_input}{AI_PROMPT}"},
                    {"role": "assistant", "content": message.content},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": str(tool_result)
                            }
                        ]
                    }
                ]
            )
            final_response = response.content[0].text
            print(f"Claude: {final_response}")
            return

    # If no tool use, print the response directly
    print(f"Claude: {message.content[0].text}")

# Run the PoC
asyncio.run(run_poc())
```

#### Notes
- Replace `"your-anthropic-api-key"` with your actual key.
- The script assumes Claude returns a `tool_use` response. Adjust based on your API’s behavior.
- For simplicity, the user input is hardcoded. You can modify it to accept live input with a loop.

### 3. Run the PoC
1. Start the MCP server:
   ```bash
   python mcp_server.py
   ```
2. Run the client script in another terminal:
   ```bash
   python client_script.py
   ```
3. Observe the output, which should show:
   - The user query.
   - Claude requesting a tool (if applicable).
   - The tool result from your API via the MCP server.
   - Claude’s final response.

---

## How It Works
- **User Query**: You send a query like "Get the latest data for 'example_param'".
- **Claude API**: Claude decides if a tool is needed and returns a `tool_use` request.
- **MCP Interaction**: The script sends an `invokeTool` request to the MCP server, which calls your API and returns the result.
- **Response**: The script sends the result back to Claude, which generates a final response.

---

## Simplifications for the PoC
- **Hardcoded Query**: The example uses a fixed query to trigger tool use. For a live demo, replace it with `input("Enter your query: ")`.
- **Single Tool**: The example assumes one tool (`get_data`). Add more tools as needed.
- **Local Setup**: Everything runs locally, which is fine for a PoC.

---

## Considerations
- **Security**: If your API handles sensitive data, secure the MCP server (e.g., with authentication), though this can be skipped for a basic PoC.
- **Error Handling**: Add basic error checks (e.g., WebSocket connection failures) for robustness.
- **Scalability**: This is a local PoC. For production, consider hosting the MCP server and adding proper client integration.

---

## Output Example
For a query like "Get the latest data for 'example_param'":
```
User: Get the latest data for 'example_param'
Claude wants to use tool: get_data with args: {'param': 'example_param'}
Tool result: {"data": "Sample data from your API"}
Claude: The latest data for 'example_param' is: Sample data from your API.
```

---

This PoC demonstrates how MCP can connect your API tools to Claude without Claude Desktop. You can expand it by adding more tools or refining the client script for a more interactive experience. Let me know if you need help adapting it to your specific API!

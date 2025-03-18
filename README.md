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


Let me clarify your questions about the **MCP SDK** and whether you need it for your Proof of Concept (PoC). I’ll break this down step by step to make it as clear as possible.

---

### What is the MCP SDK?
The **Model Context Protocol (MCP)** is a standard way for Anthropic’s AI model, Claude, to communicate with external tools or APIs (like the ones you have). It uses **WebSockets** and **JSON-RPC** to send and receive messages. Think of MCP as a set of rules for how this communication happens—it’s a protocol, not a specific piece of software or SDK.

An **SDK (Software Development Kit)**, on the other hand, is a ready-made set of tools or libraries that makes it easier to follow those rules. So, an "MCP SDK" would be a library provided by Anthropic to simplify implementing the MCP protocol.

---

### Where is the MCP SDK?
As of now, Anthropic has **open-sourced the MCP protocol**, meaning they’ve shared the details of how it works publicly. However, based on available information, they **do not appear to provide a specific MCP SDK** for implementing the protocol (e.g., for setting up an MCP server to expose your tools). Instead:

- Anthropic provides an **SDK for interacting with Claude via their API** (e.g., the `anthropic` Python package), but this is for sending queries to Claude, not for building the MCP server that connects your tools.
- For the MCP server part (exposing your API tools), you’re expected to implement the protocol yourself based on its specification, unless Anthropic releases an MCP-specific SDK in the future.

So, to answer your question directly: **There doesn’t seem to be an official MCP SDK available from Anthropic right now**. You can check their [official documentation](https://docs.anthropic.com) or GitHub repositories for updates, but currently, you’ll need to work with the protocol manually.

---

### Do You Need the MCP SDK?
**No, you don’t strictly need an MCP SDK** to create your PoC. Here’s why:

- **Manual Implementation Works**: You can build an MCP server yourself using standard tools like Python’s `websockets` library (for WebSocket communication) and JSON (for handling RPC requests). This server will let Claude interact with your API tools by following the MCP protocol rules.
- **You Already Have Tools**: Since you mentioned you have your own API with tools, you can expose those tools through this manually built MCP server. Claude can then use them via the Anthropic API.
- **Anthropic SDK for Claude**: You’ll still use Anthropic’s existing SDK (e.g., `anthropic` in Python) to send queries to Claude and handle responses, but this is separate from implementing MCP for your tools.

If Anthropic did provide an MCP SDK, it might make setting up the server faster or easier by handling the protocol details for you. But without it, you can still achieve your goal with a manual approach.

---

### How to Do This Simply Without an MCP SDK
Since you don’t have access to Claude Desktop, here’s a straightforward way to create your PoC:

1. **Create an MCP Server**:
   - Use Python with the `websockets` library to set up a WebSocket server.
   - Implement the MCP protocol by handling JSON-RPC requests (e.g., when Claude asks to use your tools, the server runs the tool and sends back the result).
   - Connect your existing API tools to this server so Claude can call them.

2. **Write a Client Script**:
   - Use Anthropic’s Python SDK (`anthropic`) to send user queries to Claude via their API.
   - When Claude needs to use a tool, this script will pass the request to your MCP server (over WebSockets) and send the tool’s response back to Claude.

3. **Test the Integration**:
   - Run your MCP server and client script together.
   - Send a test query to Claude through the script, and ensure it can use your tools via the MCP server.

Here’s a simplified example of what this might look like in Python:

#### MCP Server (exposing your tools)
```python
import asyncio
import websockets
import json

async def handle_connection(websocket, path):
    async for message in websocket:
        request = json.loads(message)
        # Example: Claude asks to use a tool
        if request["method"] == "your_tool_name":
            result = your_api_tool_function(request["params"])  # Call your API tool
            response = {"id": request["id"], "result": result}
            await websocket.send(json.dumps(response))

start_server = websockets.serve(handle_connection, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

#### Client Script (interacting with Claude)
```python
import anthropic

client = anthropic.Anthropic(api_key="your_api_key")
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Use my tool to do X"}],
    tools=[{"name": "your_tool_name", "endpoint": "ws://localhost:8765"}]
)
print(response.content)
```

This is a basic setup—you’d need to flesh it out with your specific tools and error handling, but it shows how you can connect Claude to your API without an MCP SDK.

---

### Key Takeaways
- **No MCP SDK Needed**: You can implement the MCP protocol manually with Python tools like `websockets` and JSON-RPC, so you don’t need a specific MCP SDK for your PoC.
- **Where It Is**: There’s no official MCP SDK from Anthropic yet—just the protocol spec and their Claude API SDK.
- **Simple Approach**: Build an MCP server for your tools and a client script to talk to Claude, as shown above.

If you’re still unsure or want help with the code, feel free to ask—I’m happy to assist further!

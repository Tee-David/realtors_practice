# Playwright MCP Server Setup Guide

## What is Playwright MCP?

Playwright MCP (Model Context Protocol) server gives Claude enhanced visual debugging capabilities:
- Take screenshots of web pages
- Navigate and interact with websites visually
- Extract data while seeing what the scraper sees
- Debug JavaScript-rendered content

## Installation

You've already installed it with:
```bash
npx @playwright/mcp@latest
```

## Configuration for Claude Desktop

### Windows Configuration

1. **Locate Claude Desktop config file:**
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Edit the config file** (create if it doesn't exist):
   ```json
   {
     "mcpServers": {
       "playwright": {
         "command": "npx",
         "args": [
           "-y",
           "@playwright/mcp@latest"
         ]
       }
     }
   }
   ```

3. **Restart Claude Desktop** - Close completely and reopen

4. **Verify it's working** - Look for MCP icon in Claude Desktop interface

### Alternative: Local Installation

For faster startup, install globally:

```bash
# Install globally
npm install -g @playwright/mcp

# Install Playwright browsers
npx playwright install
```

Then update config:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "playwright-mcp",
      "args": []
    }
  }
}
```

## Usage in Claude Desktop

Once configured, Claude Desktop will have access to these tools:

### Available Tools

1. **playwright_navigate** - Navigate to URL
   ```
   Navigate to https://nigeriapropertycentre.com/
   ```

2. **playwright_screenshot** - Take screenshot
   ```
   Take a screenshot of the current page
   ```

3. **playwright_click** - Click elements
   ```
   Click the "Next" button
   ```

4. **playwright_fill** - Fill form fields
   ```
   Fill search box with "Lagos"
   ```

5. **playwright_evaluate** - Run JavaScript
   ```
   Evaluate: document.querySelectorAll('.property').length
   ```

## Example Debugging Session

**Without MCP (Current):**
```
You: "Debug the NPC scraper"
Claude: *runs Python script, shows text output*
```

**With MCP (Enhanced):**
```
You: "Debug the NPC scraper"
Claude:
  1. *navigates to NPC homepage*
  2. *takes screenshot - shows you the page*
  3. *highlights property elements visually*
  4. *shows what selector matches*
  5. *extracts and compares results*
```

## Benefits for This Project

### 1. Visual Property Verification
See exactly which elements are being matched:
```
Claude: "Let me navigate to NPC and show you what we're matching..."
[Screenshot showing highlighted .property elements]
```

### 2. Selector Development
Iteratively test selectors with visual feedback:
```
Claude: "Trying selector .property..."
[Screenshot with elements highlighted]
Claude: "Found 4 matches - these look correct!"
```

### 3. Pagination Debugging
See exactly what "Next" button looks like:
```
Claude: "Here's the pagination section..."
[Screenshot showing next button location and style]
```

### 4. JavaScript Rendering Issues
Detect if content is lazy-loaded:
```
Claude: "Page loaded, now scrolling to trigger lazy load..."
[Screenshots before/after showing new content appearing]
```

## Limitations

**MCP is for Claude Desktop only** - not available in:
- CLI interfaces
- Web interface (claude.ai)
- API access

**Workarounds:**
- ✅ Use our Python debug scripts (`debug_scraper.py`, `visual_debug_scraper.py`)
- ✅ Take screenshots with Playwright Python API
- ✅ Generate HTML dumps for analysis

## Current Project Status

**What We Have (Without MCP):**
- ✅ `debug_scraper.py` - Text-based step-by-step trace
- ✅ `visual_debug_scraper.py` - Screenshot-based debugging
- ✅ `dump_page_html.py` - HTML structure analysis
- ✅ All bugs identified and fixed!

**What MCP Would Add:**
- ⭐ Real-time visual debugging in Claude Desktop
- ⭐ Interactive element selection
- ⭐ Live page manipulation
- ⭐ Easier selector discovery

## Recommendation

**For this project:**
1. ✅ **Current approach works fine** - Bugs already fixed using Python tools
2. 💡 **MCP is nice-to-have** - Useful for future debugging sessions
3. 🔧 **Configure it for later** - Set up in Claude Desktop for visual work

**When to use MCP:**
- Adding new sites with unknown structure
- Debugging complex JavaScript-heavy sites
- Understanding pagination patterns visually
- Teaching someone how the scraper works

## Setup Steps Summary

1. ✅ Install Playwright MCP: `npx @playwright/mcp@latest` (DONE)
2. ⏳ Edit `%APPDATA%\Claude\claude_desktop_config.json`
3. ⏳ Add MCP server configuration
4. ⏳ Restart Claude Desktop
5. ⏳ Test by asking Claude to navigate to a webpage

## Alternative: Continue with Python Tools

Our current Python-based tools (`debug_scraper.py`, `visual_debug_scraper.py`) work great and don't require MCP setup. All bugs have been identified and fixed using these tools!

---

**Note:** MCP is completely optional for this project. The scraper works fine without it, and all debugging can be done with our Python scripts.

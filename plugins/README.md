# MarkPolish Studio Plugins

## What are Plugins?

Plugins allow you to create custom markdown components that extend MarkPolish Studio's functionality.

## Creating a Plugin

1. Copy `example_callout.py` as a template
2. Modify the `PLUGIN_METADATA` dictionary
3. Implement the `render()` function
4. Save your plugin in the `plugins/` directory
5. Restart MarkPolish Studio

## Plugin Structure

Each plugin must have:

- **PLUGIN_METADATA**: Dictionary with plugin information
  - `name`: Unique plugin name
  - `syntax`: Regex pattern to match your component
  - `description`: What your plugin does
  - `category`: Plugin category (Layout, Content, Interactive, Media, Data)
  - `compatibility`: Dict with `wechat` and `html` boolean flags
  - `insertion_tool`: Markdown snippet users can insert

- **render()**: Function that converts matched text to HTML
  - Parameters: `match` (regex match), `styles` (theme styles), `mode` ("wechat" or "web")
  - Returns: HTML string

## WeChat Compatibility

WeChat has limitations:
- ❌ No JavaScript
- ❌ Limited CSS (no animations, transforms)
- ❌ No external resources
- ✅ Basic HTML works
- ✅ Inline CSS works
- ✅ Static images work

Set `"wechat": False` if your plugin requires JavaScript or advanced CSS.

## Examples

See `example_callout.py` for a complete example.

## Categories

- **Layout**: Components that affect page structure
- **Content**: Text, callouts, quotes, etc.
- **Interactive**: Components with user interaction (HTML only)
- **Media**: Images, videos, galleries
- **Data**: Charts, tables, analytics

## Need Help?

Check the plugin documentation in MarkPolish Studio's help section.

"""
Plugin System for MarkPolish Studio
Allows users to create and install custom markdown components
"""

import os
import json
import importlib.util
import streamlit as st
from typing import Dict, List, Optional, Tuple, Any
import re

# Component compatibility flags
COMPONENT_COMPATIBILITY = {
    "hero": {"wechat": True, "html": True},
    "col-2": {"wechat": True, "html": True},
    "col-3": {"wechat": True, "html": True},
    "steps": {"wechat": True, "html": True},
    "timeline": {"wechat": True, "html": True},
    "reveal": {"wechat": False, "html": True},  # Uses SVG animations
    "badge": {"wechat": True, "html": True},
    "button": {"wechat": True, "html": True},
    "card": {"wechat": True, "html": True},
    "img": {"wechat": True, "html": True},
}

class Plugin:
    """Represents a plugin component"""
    
    def __init__(self, name: str, syntax: str, render_func, compatibility: Dict[str, bool], 
                 description: str = "", category: str = "Custom", insertion_tool: str = None):
        self.name = name
        self.syntax = syntax  # Regex pattern or markdown syntax
        self.render_func = render_func  # Function that takes (match, styles, mode) -> HTML
        self.compatibility = compatibility  # {"wechat": bool, "html": bool}
        self.description = description
        self.category = category
        self.insertion_tool = insertion_tool  # Markdown snippet to insert
    
    def is_compatible(self, mode: str) -> bool:
        """Check if plugin is compatible with rendering mode"""
        return self.compatibility.get(mode, False)
    
    def render(self, match, styles: Dict, mode: str) -> str:
        """Render the plugin component"""
        if not self.is_compatible(mode):
            # Return fallback for incompatible components
            return f'<div style="padding: 10px; border: 1px dashed #ccc; color: #999;">⚠️ Component "{self.name}" not available in {mode} mode</div>'
        return self.render_func(match, styles, mode)

class PluginRegistry:
    """Manages plugin registration and loading"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_dir = "plugins"
        self.ensure_plugin_dir()
    
    def ensure_plugin_dir(self):
        """Create plugins directory if it doesn't exist"""
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            # Create example plugin
            self.create_example_plugin()
    
    def register_plugin(self, plugin: Plugin):
        """Register a plugin"""
        self.plugins[plugin.name] = plugin
        # Update compatibility registry
        COMPONENT_COMPATIBILITY[plugin.name] = plugin.compatibility
    
    def load_plugins_from_directory(self):
        """Load all plugins from the plugins directory"""
        if not os.path.exists(self.plugin_dir):
            return
        
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                try:
                    self.load_plugin_file(os.path.join(self.plugin_dir, filename))
                except Exception as e:
                    st.error(f"Failed to load plugin {filename}: {e}")
    
    def load_plugin_file(self, filepath: str):
        """Load a plugin from a Python file"""
        plugin_name = os.path.basename(filepath).replace('.py', '')
        
        spec = importlib.util.spec_from_file_location(plugin_name, filepath)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load plugin from {filepath}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Extract plugin metadata
        if hasattr(module, 'PLUGIN_METADATA'):
            metadata = module.PLUGIN_METADATA
            render_func = getattr(module, 'render', None)
            
            if render_func:
                plugin = Plugin(
                    name=metadata.get('name', plugin_name),
                    syntax=metadata.get('syntax', ''),
                    render_func=render_func,
                    compatibility=metadata.get('compatibility', {'wechat': False, 'html': True}),
                    description=metadata.get('description', ''),
                    category=metadata.get('category', 'Custom'),
                    insertion_tool=metadata.get('insertion_tool', '')
                )
                self.register_plugin(plugin)
    
    def get_plugins_by_category(self, category: str = None) -> List[Plugin]:
        """Get plugins filtered by category"""
        if category:
            return [p for p in self.plugins.values() if p.category == category]
        return list(self.plugins.values())
    
    def get_compatible_plugins(self, mode: str) -> List[Plugin]:
        """Get plugins compatible with the specified mode"""
        return [p for p in self.plugins.values() if p.is_compatible(mode)]
    
    def create_example_plugin(self):
        """Create an example plugin file for users to learn from"""
        # Use string concatenation to avoid f-string parsing issues
        example_content = '"""\n'
        example_content += 'Example Plugin for MarkPolish Studio\n'
        example_content += 'This is a template you can copy and modify to create your own plugins.\n'
        example_content += '"""\n\n'
        example_content += '# Plugin metadata - required\n'
        example_content += 'PLUGIN_METADATA = {\n'
        example_content += '    "name": "example_callout",\n'
        example_content += '    "syntax": r\'(?is):::\s*callout\s+type=(\\w+)\\n(.*?)\\n:::\',\n'
        example_content += '    "description": "Creates a callout box with different types (info, warning, error, success)",\n'
        example_content += '    "category": "Content",\n'
        example_content += '    "compatibility": {\n'
        example_content += '        "wechat": True,  # Works in WeChat\n'
        example_content += '        "html": True     # Works in HTML\n'
        example_content += '    },\n'
        example_content += '    "insertion_tool": "::: callout type=info\\nYour message here\\n:::"\n'
        example_content += '}\n\n'
        example_content += 'def render(match, styles, mode="wechat"):\n'
        example_content += '    """\n'
        example_content += '    Render function for the plugin\n'
        example_content += '    \n'
        example_content += '    Args:\n'
        example_content += '        match: Regex match object containing captured groups\n'
        example_content += '        styles: Dictionary of style strings from theme\n'
        example_content += '        mode: "wechat" or "web"\n'
        example_content += '    \n'
        example_content += '    Returns:\n'
        example_content += '        HTML string\n'
        example_content += '    """\n'
        example_content += '    import re\n'
        example_content += '    \n'
        example_content += '    # Extract groups from match\n'
        example_content += '    callout_type = match.group(1) if match.lastindex >= 1 else "info"\n'
        example_content += '    content = match.group(2) if match.lastindex >= 2 else ""\n'
        example_content += '    \n'
        example_content += '    # Define colors for different callout types\n'
        example_content += '    colors = {\n'
        example_content += '        "info": {"bg": "#E3F2FD", "border": "#2196F3", "text": "#1976D2"},\n'
        example_content += '        "warning": {"bg": "#FFF3E0", "border": "#FF9800", "text": "#F57C00"},\n'
        example_content += '        "error": {"bg": "#FFEBEE", "border": "#F44336", "text": "#C62828"},\n'
        example_content += '        "success": {"bg": "#E8F5E9", "border": "#4CAF50", "text": "#2E7D32"}\n'
        example_content += '    }\n'
        example_content += '    \n'
        example_content += '    color = colors.get(callout_type.lower(), colors["info"])\n'
        example_content += '    \n'
        example_content += '    # Build HTML using f-strings (recommended approach)\n'
        example_content += '    if mode == "wechat":\n'
        example_content += '        bg_color = color["bg"]\n'
        example_content += '        border_color = color["border"]\n'
        example_content += '        text_color = color["text"]\n'
        example_content += '        styles_text = styles.get("text", "#333")\n'
        example_content += '        html = f\'\'\'\n'
        example_content += '        <section style="background-color: {bg_color}; border-left: 4px solid {border_color}; \n'
        example_content += '                        padding: 15px; margin: 20px 0; border-radius: 8px;">\n'
        example_content += '            <div style="color: {text_color}; font-weight: bold; margin-bottom: 8px;">\n'
        example_content += '                {callout_type.upper()}\n'
        example_content += '            </div>\n'
        example_content += '            <div style="color: {styles_text};">\n'
        example_content += '                {content}\n'
        example_content += '            </div>\n'
        example_content += '        </section>\n'
        example_content += '        \'\'\'\n'
        example_content += '    else:\n'
        example_content += '        bg_color = color["bg"]\n'
        example_content += '        border_color = color["border"]\n'
        example_content += '        text_color = color["text"]\n'
        example_content += '        html = f\'\'\'\n'
        example_content += '        <div class="mp-callout mp-callout-{callout_type}" \n'
        example_content += '             style="background-color: {bg_color}; border-left: 4px solid {border_color}; \n'
        example_content += '                    padding: 15px; margin: 20px 0; border-radius: 8px;">\n'
        example_content += '            <div style="color: {text_color}; font-weight: bold; margin-bottom: 8px;">\n'
        example_content += '                {callout_type.upper()}\n'
        example_content += '            </div>\n'
        example_content += '            <div>{content}</div>\n'
        example_content += '        </div>\n'
        example_content += '        \'\'\'\n'
        example_content += '    \n'
        example_content += '    return html\n'
        
        example_path = os.path.join(self.plugin_dir, "example_callout.py")
        with open(example_path, 'w', encoding='utf-8') as f:
            f.write(example_content)
        
        # Create README
        readme_path = os.path.join(self.plugin_dir, "README.md")
        readme_content = '''# MarkPolish Studio Plugins

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
'''
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

def apply_plugins(text: str, styles: Dict, mode: str, registry: PluginRegistry) -> str:
    """Apply all registered plugins to the text"""
    # Get compatible plugins for the mode
    plugins = registry.get_compatible_plugins(mode)
    
    # Apply each plugin
    for plugin in plugins:
        try:
            # Try to match the plugin's syntax pattern
            pattern = plugin.syntax
            if isinstance(pattern, str):
                # Compile regex if it's a string
                regex = re.compile(pattern, re.IGNORECASE | re.DOTALL)
                # Find all matches and replace
                def replacer(match):
                    return plugin.render(match, styles, mode)
                text = regex.sub(replacer, text)
        except Exception as e:
            # Skip plugins that fail
            continue
    
    return text

# Global registry instance
_plugin_registry = None

def get_plugin_registry() -> PluginRegistry:
    """Get or create the global plugin registry"""
    global _plugin_registry
    if _plugin_registry is None:
        _plugin_registry = PluginRegistry()
        _plugin_registry.load_plugins_from_directory()
    return _plugin_registry

def reload_plugin_registry():
    """Force reload of plugin registry (useful after plugin changes)"""
    global _plugin_registry
    _plugin_registry = None
    return get_plugin_registry()


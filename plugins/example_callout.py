"""
Example Plugin for MarkPolish Studio
This is a template you can copy and modify to create your own plugins.
"""

# Plugin metadata - required
PLUGIN_METADATA = {
    "name": "example_callout",
    "syntax": r'(?is):::\s*callout\s+type=(\w+)\n(.*?)\n:::',
    "description": "Creates a callout box with different types (info, warning, error, success)",
    "category": "Content",
    "compatibility": {
        "wechat": True,  # Works in WeChat
        "html": True     # Works in HTML
    },
    "insertion_tool": "::: callout type=info\nYour message here\n:::"
}

def render(match, styles, mode="wechat"):
    """
    Render function for the plugin
    
    Args:
        match: Regex match object containing captured groups
        styles: Dictionary of style strings from theme
        mode: "wechat" or "web"
    
    Returns:
        HTML string
    """
    import re
    
    # Extract groups from match
    callout_type = match.group(1) if match.lastindex >= 1 else "info"
    content = match.group(2) if match.lastindex >= 2 else ""
    
    # Define colors for different callout types
    colors = {
        "info": {"bg": "#E3F2FD", "border": "#2196F3", "text": "#1976D2"},
        "warning": {"bg": "#FFF3E0", "border": "#FF9800", "text": "#F57C00"},
        "error": {"bg": "#FFEBEE", "border": "#F44336", "text": "#C62828"},
        "success": {"bg": "#E8F5E9", "border": "#4CAF50", "text": "#2E7D32"}
    }
    
    color = colors.get(callout_type.lower(), colors["info"])
    
    # Build HTML using f-strings (recommended approach)
    if mode == "wechat":
        bg_color = color["bg"]
        border_color = color["border"]
        text_color = color["text"]
        styles_text = styles.get("text", "#333")
        # Build HTML without extra whitespace/newlines that could break rendering
        html = (
            '<section style="background-color: ' + bg_color + 
            '; border-left: 4px solid ' + border_color + 
            '; padding: 15px; margin: 20px 0; border-radius: 8px;">' +
            '<div style="color: ' + text_color + 
            '; font-weight: bold; margin-bottom: 8px;">' +
            callout_type.upper() + '</div>' +
            '<div style="color: ' + styles_text + ';">' +
            content + '</div>' +
            '</section>'
        )
    else:
        bg_color = color["bg"]
        border_color = color["border"]
        text_color = color["text"]
        # Build HTML without extra whitespace
        html = (
            '<div class="mp-callout mp-callout-' + callout_type + 
            '" style="background-color: ' + bg_color + 
            '; border-left: 4px solid ' + border_color + 
            '; padding: 15px; margin: 20px 0; border-radius: 8px;">' +
            '<div style="color: ' + text_color + 
            '; font-weight: bold; margin-bottom: 8px;">' +
            callout_type.upper() + '</div>' +
            '<div>' + content + '</div>' +
            '</div>'
        )
    
    return html

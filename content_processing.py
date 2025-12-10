"""
Content processing module for MarkPolish Studio
Handles markdown parsing, content type detection, preview generation, and styling
"""

import re
import streamlit as st

# Import components and plugins if available
try:
    from components import apply_components
    from plugin_system import get_plugin_registry, apply_plugins
except ImportError:
    apply_components = None
    get_plugin_registry = None
    apply_plugins = None

# Import error handler if available
try:
    from error_handler import ErrorHandler
except ImportError:
    ErrorHandler = None


def get_stats(text):
    """Calculates word count and reading time"""
    if not text: 
        return 0, 0
    words = len(text.split())
    read_time = max(1, round(words / 200))  # Avg 200 wpm
    return words, read_time


def detect_content_type(text):
    """Detect content type based on text content"""
    text_lower = text.lower()
    
    # Check for keywords and patterns
    if any(word in text_lower for word in ["launch", "announce", "new feature", "update", "version"]):
        return "Product Launch"
    elif any(word in text_lower for word in ["newsletter", "weekly", "insights", "trends"]):
        return "Newsletter"
    elif any(word in text_lower for word in ["tutorial", "how to", "step", "guide", "learn"]):
        return "Tutorial"
    elif any(word in text_lower for word in ["promo", "discount", "offer", "campaign", "sale"]):
        return "Marketing"
    elif any(word in text_lower for word in ["meeting", "internal", "team", "project update"]):
        return "Internal"
    elif any(word in text_lower for word in ["blog", "article", "story", "thoughts"]):
        return "Blog Post"
    elif any(word in text_lower for word in ["announce", "notice", "important"]):
        return "Announcement"
    
    return None


def get_preview_css(theme, mode="Mobile"):
    """Get CSS for preview frame"""
    t = theme
    bg_color = t.get('bg', '#ffffff')
    text_color = t.get('text', '#000000')
    font_family = t.get('font', 'Arial, sans-serif')
    radius = t.get('radius', '8px')
    
    # Pre-compute mobile-specific values
    is_mobile = (mode == "Mobile")
    notch_display = "block" if is_mobile else "none"
    content_padding_top = "30px" if is_mobile else "0"
    
    if is_mobile:
        frame_css = """
            width: 100% !important;
            max-width: 375px !important;
            min-width: 0 !important;
            height: 750px !important;
            border: 16px solid #1a1a1a !important;
            border-radius: 50px !important;
            padding: 0 !important;
            overflow: hidden !important;
        """
    else:
        frame_css = "width: 100%; height: 750px; border: 1px solid #ddd; border-radius: 8px;"
    
    return f"""
    <style>
    * {{
        box-sizing: border-box;
    }}
    body, html {{ 
        margin: 0; 
        padding: 0; 
        background: transparent;
    }}
    /* Hide scrollbar */
    ::-webkit-scrollbar {{
        display: none;
    }}
    .preview-content {{
        -ms-overflow-style: none;
        scrollbar-width: none;
    }}
    .preview-frame {{ 
        {frame_css} 
        margin: 0 auto !important; 
        background: transparent !important; 
        box-shadow: none !important; 
        position: relative !important;
        display: block !important;
    }}
    /* Notch effect for mobile */
    .preview-frame::before {{
        content: '';
        display: {notch_display};
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 150px;
        height: 28px;
        background: #1a1a1a;
        border-bottom-left-radius: 16px;
        border-bottom-right-radius: 16px;
        z-index: 100;
    }}
    .preview-content {{
        width: 100%;
        height: 100%;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        -webkit-overflow-scrolling: touch !important;
        padding-top: {content_padding_top};
        background: {bg_color} !important;
    }}
    .mp-canvas {{ 
        padding: 20px; 
        box-sizing: border-box; 
        min-height: 100%;
        background: {bg_color};
        color: {text_color};
        font-family: {font_family};
        width: 100%;
        overflow-wrap: break-word;
        word-wrap: break-word;
        line-height: 1.75;
    }}
    /* Default theme colors - NO !important so inline styles from components win */
    .mp-canvas p,
    .mp-canvas li {{
        color: {text_color};
        font-family: {font_family};
        line-height: 1.75;
    }}
    .mp-canvas h1, .mp-canvas h2 {{
        color: {text_color};
        font-family: {font_family};
    }}
    .mp-canvas h3, .mp-canvas h4, .mp-canvas h5, .mp-canvas h6 {{
        color: {text_color};
        font-family: {font_family};
    }}
    .mp-canvas strong {{
        font-weight: bold;
    }}
    .mp-canvas a {{
        text-decoration: none;
    }}
    /* Container basics */
    .mp-canvas > div {{
        max-width: 100%;
        box-sizing: border-box;
    }}
    /* Steps component */
    .mp-canvas div[style*="display: flex"] {{
        display: flex !important;
        align-items: center !important;
    }}
    .mp-canvas span[style*="border-radius: 50%"] {{
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    /* Timeline component */
    .mp-canvas div[style*="position: relative"] {{
        position: relative !important;
        text-align: left !important;
        float: none !important;
    }}
    .mp-canvas span[style*="position: absolute"] {{
        position: absolute !important;
    }}
    .mp-canvas div[style*="border-left"] {{
        text-align: left !important;
    }}
    /* Grid layout */
    .mp-canvas section[style*="display: flex"] {{
        display: flex !important;
        gap: 10px !important;
        flex-wrap: wrap !important;
    }}
    /* Image constraints - KEEP !important */
    .mp-canvas img,
    img {{
        max-width: 100% !important; 
        height: auto !important; 
        box-sizing: border-box;
        display: block;
        margin: 12px 0;
        border-radius: {radius};
        object-fit: contain;
    }}
    svg {{ cursor: pointer; }}
    .mp-hero h1 {{ text-align: center; }}
    </style>
    """


def get_inline_styles(theme):
    """Get inline styles dictionary for theme"""
    t = theme
    font_base = f"font-family: {t['font']}; color: {t['text']}; line-height: 1.75; font-size: 16px; text-align: justify;"
    btn_text = "#000" if "050505" in t['bg'] else "#fff"
    return {
        'primary': t['primary'], 
        'p': f"{font_base} margin-bottom: 16px;",
        'li': f"{font_base} margin-bottom: 8px;",
        'h1': f"font-family: {t['font']}; color: {t['primary']}; font-size: 24px; font-weight: bold; margin-top: 30px; margin-bottom: 20px; line-height: 1.4; text-align: left;",
        'h2': f"font-family: {t['font']}; color: {t['primary']}; font-size: 18px; font-weight: bold; margin-top: 30px; margin-bottom: 15px; border-bottom: 2px solid {t['primary']}20; padding-bottom: 8px;",
        'h3': f"font-family: {t['font']}; color: {t['text']}; font-size: 17px; font-weight: bold; margin-top: 20px; margin-bottom: 10px;",
        'strong': f"font-weight: bold; color: {t['primary']};",
        'hero': f"background-color: {t['card']} !important; padding: 35px 20px !important; text-align: center !important; border-radius: {t['radius']} !important; margin: 0 0 25px 0 !important; box-shadow: {t['shadow']} !important; box-sizing: border-box !important;",
        'card': f"background-color: {t['card']} !important; border-left: 4px solid {t['primary']} !important; padding: 15px !important; margin: 20px 0 !important; border-radius: {t['radius']} !important; box-shadow: {t['shadow']} !important; color: {t['text']} !important; box-sizing: border-box !important;",
        'card_h_color': t['primary'], 
        'btn': f"background-color: {t['primary']}; color: {btn_text}; padding: 10px 25px; border-radius: {t['radius']}; text-decoration: none; display: inline-block; font-weight: bold;",
        'btn_wrap': "text-align: center; margin: 30px 0;",
        'grid': "display: flex !important; gap: 10px !important; margin: 20px 0 !important; flex-wrap: wrap !important;",
        'col': f"flex: 1 !important; background-color: {t['card']} !important; padding: 10px !important; border-radius: {t['radius']} !important; box-shadow: {t['shadow']} !important; min-width: 0 !important; box-sizing: border-box !important;",
        'img': f"max-width: 100% !important; width: 100% !important; border-radius: {t['radius']}; display: block; margin: 20px 0; box-shadow: {t['shadow']}; height: auto !important; box-sizing: border-box !important; object-fit: contain !important;",
        'wrapper': f"background-color: {t['bg']}; padding: 20px; min-height: 100%; box-sizing: border-box;",
        'quote': f"border-left: 4px solid {t['primary']}; padding-left: 15px; color: {t.get('muted', '#666')}; font-style: italic; background: {t.get('accent', '#eee')}; padding: 10px; margin: 20px 0;",
        'ul': "padding-left: 20px; margin-bottom: 16px;",
        'ol': "padding-left: 20px; margin-bottom: 16px;",
        'badge': f"background-color: {t['primary']}20; color: {t['primary']}; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; vertical-align: middle; margin-right: 5px;",
        'reveal_box': "position: relative; margin: 20px 0; cursor: pointer; overflow: hidden; border-radius: 8px;",
        'time_box': f"border-left: 2px solid {t['primary']}; padding-left: 20px; margin-left: 0; padding-bottom: 20px; position: relative; display: block; min-height: 30px; text-align: left; width: auto; float: none;",
        'time_dot': f"width: 12px; height: 12px; background-color: {t['primary']}; border-radius: 50%; position: absolute; left: -7px; top: 4px; display: block;",
        'step_box': f"display: flex; margin-bottom: 15px; align-items: center; gap: 12px;",
        'step_num': f"background-color: {t['primary']}; color: {t['bg']}; width: 28px; height: 28px; min-width: 28px; border-radius: 50%; text-align: center; line-height: 28px; font-size: 14px; font-weight: bold; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;"
    }


def deep_inject_styles(html_content, styles):
    """Inject inline styles into HTML content"""
    html_content = re.sub(r'<p>', f'<p style="{styles["p"]}">', html_content)
    html_content = re.sub(r'<li>', f'<li style="{styles["li"]}">', html_content)
    html_content = re.sub(r'<h1>', f'<h1 style="{styles["h1"]}">', html_content)
    html_content = re.sub(r'<h2>', f'<h2 style="{styles["h2"]}">', html_content)
    html_content = re.sub(r'<h3>', f'<h3 style="{styles["h3"]}">', html_content)
    html_content = re.sub(r'<strong>', f'<strong style="{styles["strong"]}">', html_content)
    html_content = re.sub(r'<blockquote>', f'<blockquote style="{styles["quote"]}">', html_content)
    html_content = html_content.replace('<ul>', f'<ul style="{styles["ul"]}">')
    html_content = html_content.replace('<ol>', f'<ol style="{styles["ol"]}">')
    return html_content


def parse_doc(text, styles, img_provider="Pollinations (AI)", mode="wechat"):
    """Parse document with components and plugins"""
    # IMPORTANT: Process order matters!
    # 1. Apply plugins FIRST (convert ::: callout to HTML)
    # 2. Then apply built-in components (convert other markdown to HTML)
    # Both return HTML, so result is a mix of HTML and remaining markdown
    
    if get_plugin_registry and apply_plugins:
        try:
            registry = get_plugin_registry()
            # Apply plugins - they convert markdown syntax to HTML
            text = apply_plugins(text, styles, mode, registry)
        except Exception as e:
            # If plugins fail, continue with built-in components only
            if ErrorHandler:
                ErrorHandler.log_error("apply_plugins", e)
    
    # Then apply built-in components (converts remaining markdown to HTML)
    if apply_components:
        result = apply_components(text, styles, mode=mode, img_provider=img_provider)
    else:
        result = text
    
    return result


def insert_component_at_position(content, component_template, position):
    """Insert a component template at the specified position in content
    
    Supports positions like:
    - "start" / "beginning" - Insert at the start
    - "end" - Insert at the end
    - "after paragraph 1" / "after paragraph 2" - Insert after specific paragraph
    - "before paragraph 2" - Insert before specific paragraph
    - "after heading 1" / "after # Title" - Insert after specific heading
    - "after introduction" - Insert after first paragraph
    """
    if not content:
        return component_template
    
    position_lower = position.lower().strip()
    
    # Handle simple positions
    if position_lower in ["start", "beginning", "at the start", "at the beginning"]:
        return component_template + "\n\n" + content
    elif position_lower in ["end", "at the end"]:
        return content + "\n\n" + component_template
    
    # Split content into paragraphs/blocks
    lines = content.split('\n')
    blocks = []
    current_block = []
    
    for line in lines:
        if line.strip() == '' and current_block:
            blocks.append('\n'.join(current_block))
            current_block = []
        else:
            current_block.append(line)
    if current_block:
        blocks.append('\n'.join(current_block))
    
    # Parse position for "after paragraph N" or "before paragraph N"
    import re as re_pos
    
    # Match patterns like "after paragraph 1", "before paragraph 2", "after para 3"
    para_match = re_pos.search(r'(after|before)\s+(?:paragraph|para|p)\s*(\d+)', position_lower)
    if para_match:
        action = para_match.group(1)  # "after" or "before"
        para_num = int(para_match.group(2))
        
        # Count paragraphs (non-empty blocks that aren't components)
        para_count = 0
        insert_idx = -1
        
        for i, block in enumerate(blocks):
            # Skip component blocks (start with :::)
            if block.strip().startswith(':::'):
                continue
            para_count += 1
            if para_count == para_num:
                insert_idx = i
                break
        
        if insert_idx >= 0:
            if action == "after":
                # Insert after this block
                blocks.insert(insert_idx + 1, component_template)
            else:  # before
                blocks.insert(insert_idx, component_template)
            return '\n\n'.join(blocks)
    
    # Match patterns like "after heading 1", "after # Title", "after introduction"
    heading_match = re_pos.search(r'(after|before)\s+(?:heading|section|h)\s*(\d+)', position_lower)
    if heading_match:
        action = heading_match.group(1)
        heading_num = int(heading_match.group(2))
        
        # Count headings
        heading_count = 0
        insert_idx = -1
        
        for i, block in enumerate(blocks):
            if block.strip().startswith('#'):
                heading_count += 1
                if heading_count == heading_num:
                    insert_idx = i
                    break
        
        if insert_idx >= 0:
            if action == "after":
                blocks.insert(insert_idx + 1, component_template)
            else:
                blocks.insert(insert_idx, component_template)
            return '\n\n'.join(blocks)
    
    # Match "after introduction" - insert after first paragraph
    if "after introduction" in position_lower or "after intro" in position_lower:
        if len(blocks) > 0:
            blocks.insert(1, component_template)
            return '\n\n'.join(blocks)
    
    # Match "before conclusion" - insert before last paragraph
    if "before conclusion" in position_lower:
        if len(blocks) > 0:
            blocks.insert(len(blocks) - 1, component_template)
            return '\n\n'.join(blocks)
    
    # Match generic "after X" - try to find X in content
    generic_match = re_pos.search(r'after\s+["\']?(.+?)["\']?\s*$', position_lower)
    if generic_match:
        search_text = generic_match.group(1).strip()
        for i, block in enumerate(blocks):
            if search_text.lower() in block.lower():
                blocks.insert(i + 1, component_template)
                return '\n\n'.join(blocks)
    
    # Default: append at end
    return content + "\n\n" + component_template


def clean_for_wechat(html):
    """Clean HTML for WeChat compatibility"""
    html = html.replace('<img', '<img data-fmt="png"')
    html = re.sub(r'(<img[^>]+style=")([^"]+")', r'\1max-width:100% !important; height:auto !important; box-sizing: border-box; \2', html)
    html = re.sub(r'(<img(?!.*style=)[^>]+)>', r'\1 style="max-width:100% !important; height:auto !important; display:block; margin: 12px 0; box-sizing: border-box;">', html)
    if "<body" in html:
        start = html.find("<body")
        start = html.find(">", start) + 1
        end = html.find("</body>")
        if start != -1 and end != -1:
            return html[start:end].strip()
    return html


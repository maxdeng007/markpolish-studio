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
    """Get CSS for preview frame - includes MarkPolish component styles"""
    t = theme
    bg_color = t.get('bg', '#ffffff')
    text_color = t.get('text', '#000000')
    font_family = t.get('font', 'Arial, sans-serif')
    radius = t.get('radius', '8px')
    primary_color = t.get('primary', '#4A90E2')
    card_bg = t.get('card', '#ffffff')
    shadow = t.get('shadow', '0 1px 3px rgba(0,0,0,0.06)')
    
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
    
    # Component-specific CSS with theme variables
    hero_style = f"background-color: {card_bg} !important; padding: 35px 20px !important; text-align: center !important; border-radius: {radius} !important; margin: 0 0 25px 0 !important; box-shadow: {shadow} !important; box-sizing: border-box !important;"
    card_style = f"background-color: {card_bg} !important; border-left: 4px solid {primary_color} !important; padding: 20px !important; margin: 20px 0 !important; border-radius: {radius} !important; box-shadow: {shadow} !important; box-sizing: border-box !important;"
    step_num_style = f"background-color: {primary_color}; color: {bg_color}; width: 28px; height: 28px; min-width: 28px; border-radius: 50%; text-align: center; line-height: 28px; font-size: 14px; font-weight: bold; display: flex; align-items: center; justify-content: center; flex-shrink: 0;"
    timeline_dot_style = f"background-color: {primary_color}; width: 12px; height: 12px; border-radius: 50%; position: absolute; left: -7px; top: 4px;"
    badge_style = f"background-color: {primary_color}20; color: {primary_color}; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; vertical-align: middle; margin-right: 5px;"
    
    return f"""
    <style>
    /* Base Reset */
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
    
    /* Base Typography - NO !important so inline styles from components win */
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
    
    /* MarkPolish Component Classes - Overrides for preview */
    .mp-hero {{ {hero_style} }}
    .mp-hero h1 {{ text-align: center; margin-top: 0; }}
    
    .mp-card {{ {card_style} }}
    .mp-card h3 {{ margin-top: 0; font-size: 16px; color: {primary_color}; }}
    
    .mp-center {{
        text-align: center !important;
        margin: 16px 0 !important;
        width: 100% !important;
        box-sizing: border-box !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
        border: none !important;
        border-radius: 0 !important;
    }}
    .mp-center *,
    .mp-center p,
    .mp-center h1,
    .mp-center h2,
    .mp-center h3,
    .mp-center h4,
    .mp-center h5,
    .mp-center h6 {{
        text-align: center !important;
        background: transparent !important;
        box-shadow: none !important;
    }}
    
    .mp-grid {{
        display: flex !important;
        gap: 10px !important;
        margin: 20px 0 !important;
        flex-wrap: wrap !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}
    .mp-col {{
        flex: 1 !important;
        min-width: 0 !important;
        padding: 10px !important;
        background-color: {card_bg} !important;
        border-radius: {radius} !important;
        box-shadow: {shadow} !important;
        box-sizing: border-box !important;
    }}
    
    .mp-steps {{
        margin: 20px 0 !important;
        width: 100% !important;
    }}
    .mp-step {{
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        margin-bottom: 15px !important;
    }}
    .mp-step__num {{ {step_num_style} }}
    .mp-step__content {{
        flex: 1 !important;
        display: inline-block !important;
        vertical-align: middle !important;
    }}
    
    .mp-timeline {{
        margin: 20px 0 !important;
        padding-left: 15px !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}
    .mp-timeline__item {{
        position: relative !important;
        padding-left: 20px !important;
        padding-bottom: 20px !important;
        border-left: 2px solid {primary_color} !important;
    }}
    .mp-timeline__dot {{ {timeline_dot_style} }}
    
    .mp-badge {{ {badge_style} }}
    
    .mp-btn-wrap {{
        text-align: center !important;
        margin: 30px 0 !important;
        width: 100% !important;
    }}
    .mp-btn {{
        display: inline-block !important;
        padding: 10px 25px !important;
        background-color: {primary_color} !important;
        color: #fff !important;
        border-radius: {radius} !important;
        text-decoration: none !important;
        font-weight: bold !important;
    }}
    
    .mp-video {{
        position: relative !important;
        width: 100% !important;
        max-width: 900px !important;
        margin: 12px auto !important;
    }}
    .mp-video video {{
        width: 100% !important;
        height: auto !important;
        display: block !important;
    }}
    .mp-video__caption {{
        font-size: 13px !important;
        color: #666 !important;
        margin-top: 6px !important;
        text-align: center !important;
    }}
    
    .mp-table {{
        width: 100% !important;
        border-collapse: collapse !important;
        margin: 20px 0 !important;
        font-size: 14px !important;
    }}
    .mp-table th {{
        background-color: {primary_color} !important;
        color: white !important;
        padding: 12px 15px !important;
        text-align: left !important;
        border: 1px solid #ddd !important;
        font-weight: bold !important;
    }}
    .mp-table td {{
        padding: 12px 15px !important;
        text-align: left !important;
        border: 1px solid #ddd !important;
    }}
    .mp-table tr:nth-child(even) {{
        background-color: {card_bg}40 !important;
    }}
    
    .mp-reveal {{
        position: relative !important;
        margin: 20px 0 !important;
        cursor: pointer !important;
        overflow: hidden !important;
        border-radius: {radius} !important;
    }}
    .mp-reveal__content {{
        padding: 15px !important;
        border: 1px dashed #ccc !important;
        border-radius: 8px !important;
        background: #fff !important;
        min-height: 100px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
    }}
    .mp-reveal__overlay {{
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: 10 !important;
    }}
    
    /* Steps component inline styles override */
    .mp-canvas div[style*="display: flex"] {{
        display: flex !important;
        align-items: center !important;
    }}
    .mp-canvas span[style*="border-radius: 50%"] {{
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    
    /* Timeline component inline styles override */
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
    </style>
    """


def get_inline_styles(theme):
    """Get inline styles dictionary for theme - CMS-compatible version"""
    t = theme
    font_base = f"font-family: {t['font']}; color: {t['text']}; line-height: 1.75; font-size: 16px; text-align: justify;"
    btn_text = "#000" if "050505" in t['bg'] else "#fff"
    
    # Generate theme-aware styles
    primary = t['primary']
    card_bg = t['card']
    radius = t['radius']
    shadow = t['shadow']
    
    return {
        'primary': primary,
        'p': f"{font_base} margin-bottom: 16px;",
        'li': f"{font_base} margin-bottom: 8px;",
        'h1': f"font-family: {t['font']}; color: {primary}; font-size: 24px; font-weight: bold; margin-top: 30px; margin-bottom: 20px; line-height: 1.4; text-align: left;",
        'h2': f"font-family: {t['font']}; color: {primary}; font-size: 18px; font-weight: bold; margin-top: 30px; margin-bottom: 15px; border-bottom: 2px solid {primary}20; padding-bottom: 8px;",
        'h3': f"font-family: {t['font']}; color: {t['text']}; font-size: 17px; font-weight: bold; margin-top: 20px; margin-bottom: 10px;",
        'strong': f"font-weight: bold; color: {primary};",
        'hero': f"background-color: {card_bg} !important; padding: 35px 20px !important; text-align: center !important; border-radius: {radius} !important; margin: 0 0 25px 0 !important; box-shadow: {shadow} !important; box-sizing: border-box !important;",
        'card': f"background-color: {card_bg} !important; border-left: 4px solid {primary} !important; padding: 15px !important; margin: 20px 0 !important; border-radius: {radius} !important; box-shadow: {shadow} !important; color: {t['text']} !important; box-sizing: border-box !important;",
        'card_h_color': primary,
        'btn': f"background-color: {primary}; color: {btn_text}; padding: 10px 25px; border-radius: {radius}; text-decoration: none; display: inline-block; font-weight: bold;",
        'btn_wrap': "text-align: center; margin: 30px 0;",
        'grid': "display: flex !important; gap: 10px !important; margin: 20px 0 !important; flex-wrap: wrap !important;",
        'col': f"flex: 1 !important; background-color: {card_bg} !important; padding: 10px !important; border-radius: {radius} !important; box-shadow: {shadow} !important; min-width: 0 !important; box-sizing: border-box !important;",
        'img': f"max-width: 100% !important; width: 100% !important; border-radius: {radius}; display: block; margin: 20px auto; box-shadow: {shadow}; height: auto !important; box-sizing: border-box !important; object-fit: contain !important;",
        'wrapper': f"background-color: {t['bg']}; padding: 20px; min-height: 100%; box-sizing: border-box;",
        'quote': f"border-left: 4px solid {primary}; padding-left: 15px; color: {t.get('muted', '#666')}; font-style: italic; background: {t.get('accent', '#eee')}; padding: 10px; margin: 20px 0;",
        'ul': "padding-left: 20px; margin-bottom: 16px;",
        'ol': "padding-left: 20px; margin-bottom: 16px;",
        'badge': f"background-color: {primary}20; color: {primary}; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; vertical-align: middle; margin-right: 5px;",
        'reveal_box': "position: relative; margin: 20px 0; cursor: pointer; overflow: hidden; border-radius: 8px;",
        'time_box': f"border-left: 2px solid {primary}; padding-left: 20px; margin-left: 0; padding-bottom: 20px; position: relative; display: block; min-height: 30px; text-align: left; width: auto; float: none;",
        'time_dot': f"width: 12px; height: 12px; background-color: {primary}; border-radius: 50%; position: absolute; left: -7px; top: 4px; display: block;",
        'step_box': f"display: flex; margin-bottom: 15px; align-items: center; gap: 12px;",
        'step_num': f"background-color: {primary}; color: {t['bg']}; width: 28px; height: 28px; min-width: 28px; border-radius: 50%; text-align: center; line-height: 28px; font-size: 14px; font-weight: bold; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;"
    }


def deep_inject_styles(html_content, styles):
    """Inject inline styles into HTML content - handles tags with or without attributes"""
    
    def add_style_to_tag(match, tag_name, style_value):
        """Add inline style to an HTML tag while preserving existing attributes"""
        tag_content = match.group(1) if match.group(1) else ""
        
        # Check if style attribute already exists
        if 'style="' in tag_content:
            existing_style_match = re.search(r'style="([^"]*)"', tag_content)
            if existing_style_match:
                existing_style = existing_style_match.group(1)
                if style_value.strip() in existing_style:
                    return match.group(0)
                new_style = existing_style.rstrip(';') + "; " + style_value
                # Use regular string (not f-string) to avoid Python 3.9 backslash issue
                style_replacement = 'style="%s"' % new_style
                return f'<{tag_name}{tag_content.replace(existing_style_match.group(0), style_replacement)}>'
        
        if tag_content.strip():
            return f'<{tag_name}{tag_content} style="{style_value}">'
        return f'<{tag_name} style="{style_value}">'
    
    tag_styles = [
        ('p', styles.get('p', '')),
        ('li', styles.get('li', '')),
        ('h1', styles.get('h1', '')),
        ('h2', styles.get('h2', '')),
        ('h3', styles.get('h3', '')),
        ('strong', styles.get('strong', '')),
        ('blockquote', styles.get('quote', '')),
        ('ul', styles.get('ul', '')),
        ('ol', styles.get('ol', '')),
    ]
    
    for tag_name, style_value in tag_styles:
        if style_value:
            pattern = rf'<{tag_name}(\s[^>]*)?>'
            html_content = re.sub(
                pattern,
                lambda m: add_style_to_tag(m, tag_name, style_value),
                html_content,
                flags=re.IGNORECASE
            )
    
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
    # First, add styles to images
    html = re.sub(r'(<img[^>]+style=")([^"]+")', r'\1max-width:100% !important; height:auto !important; box-sizing: border-box; \2', html)
    html = re.sub(r'(<img(?!.*style=)[^>]+)>', r'\1 style="max-width:100% !important; height:auto !important; display:block; margin: 12px auto; box-sizing: border-box;">', html)
    # Then, replace ALL instances of margin: 12px 0 with margin: 12px auto (must be last to catch all cases)
    html = re.sub(r'margin:\s*12px\s+0\s*;?', 'margin: 12px auto;', html)
    if "<body" in html:
        start = html.find("<body")
        start = html.find(">", start) + 1
        end = html.find("</body>")
        if start != -1 and end != -1:
            return html[start:end].strip()
    return html


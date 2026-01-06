import re
import urllib.parse
import base64
import streamlit as st
import random
import os
import shlex

# Import image handling functions for library fallback
try:
    from image_handling import load_image_from_library, get_image_library
except ImportError:
    load_image_from_library = None
    get_image_library = None

# --- CSS CONSTANTS FOR CMS-COMPATIBLE OUTPUT ---
# These are injected into the preview/HTML output for consistent styling
MP_CSS_STYLES = """
<style>
/* MarkPolish Component Styles - CMS Compatible */
.mp-content {
    font-family: inherit;
    line-height: 1.75;
    color: inherit;
}
.mp-content img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 12px 0;
    border-radius: inherit;
}
.mp-content p {
    margin-bottom: 16px;
    line-height: 1.75;
}
.mp-content h1 {
    font-size: 24px;
    font-weight: bold;
    margin-top: 30px;
    margin-bottom: 20px;
    line-height: 1.4;
}
.mp-content h2 {
    font-size: 18px;
    font-weight: bold;
    margin-top: 30px;
    margin-bottom: 15px;
    border-bottom: 2px solid transparent;
    padding-bottom: 8px;
}
.mp-content h3 {
    font-size: 17px;
    font-weight: bold;
    margin-top: 20px;
    margin-bottom: 10px;
}
.mp-content a {
    text-decoration: none;
}
.mp-content strong {
    font-weight: bold;
}

/* Hero Component */
.mp-hero {
    padding: 35px 20px;
    text-align: center;
    border-radius: inherit;
    margin: 0 0 25px 0;
    box-shadow: inherit;
    box-sizing: border-box;
    width: 100%;
}
.mp-hero h1 {
    margin-top: 0;
    text-align: center;
}

/* Card Component */
.mp-card {
    border-radius: inherit;
    box-shadow: inherit;
    padding: 20px;
    margin: 20px 0;
    box-sizing: border-box;
    width: 100%;
}
.mp-card h3 {
    margin-top: 0;
    font-size: 16px;
}

/* Grid Layout Components */
.mp-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 20px 0;
    width: 100%;
    box-sizing: border-box;
}
.mp-col {
    flex: 1;
    min-width: 0;
    padding: 10px;
    border-radius: inherit;
    box-shadow: inherit;
    box-sizing: border-box;
}

/* Steps Component */
.mp-steps {
    margin: 20px 0;
    width: 100%;
}
.mp-step {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 15px;
    box-sizing: border-box;
}
.mp-step__num {
    flex-shrink: 0;
    width: 28px;
    height: 28px;
    min-width: 28px;
    border-radius: 50%;
    text-align: center;
    line-height: 28px;
    font-size: 14px;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
}
.mp-step__content {
    flex: 1;
    display: inline-block;
    vertical-align: middle;
}

/* Timeline Component */
.mp-timeline {
    margin: 20px 0;
    padding-left: 15px;
    width: 100%;
    box-sizing: border-box;
}
.mp-timeline__item {
    position: relative;
    padding-left: 20px;
    padding-bottom: 20px;
    border-left: 2px solid;
    box-sizing: border-box;
}
.mp-timeline__dot {
    position: absolute;
    left: -7px;
    top: 4px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
}

/* Badge Component */
.mp-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
    vertical-align: middle;
    margin-right: 5px;
}

/* Button Component */
.mp-btn-wrap {
    text-align: center;
    margin: 30px 0;
    width: 100%;
    box-sizing: border-box;
}
.mp-btn {
    display: inline-block;
    padding: 10px 25px;
    border-radius: inherit;
    text-decoration: none;
    font-weight: bold;
    text-align: center;
}

/* Video Component */
.mp-video {
    position: relative;
    width: 100%;
    max-width: 900px;
    margin: 12px auto;
    box-sizing: border-box;
}
.mp-video video {
    width: 100%;
    height: auto;
    display: block;
}
.mp-video__caption {
    font-size: 13px;
    margin-top: 6px;
    text-align: center;
}

/* Table Component */
.mp-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 14px;
    box-sizing: border-box;
}
.mp-table th {
    padding: 12px 15px;
    text-align: left;
    font-weight: bold;
    border: 1px solid #ddd;
}
.mp-table td {
    padding: 12px 15px;
    text-align: left;
    border: 1px solid #ddd;
}
.mp-table tr:nth-child(even) {
    background-color: rgba(0,0,0,0.02);
}

/* Reveal Component */
.mp-reveal {
    position: relative;
    margin: 20px 0;
    cursor: pointer;
    overflow: hidden;
    border-radius: inherit;
}
.mp-reveal__content {
    padding: 15px;
    border: 1px dashed #ccc;
    border-radius: 8px;
    min-height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
}
.mp-reveal__overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 10;
}

/* Responsive adjustments */
@media (max-width: 600px) {
    .mp-grid {
        flex-direction: column;
    }
    .mp-col {
        width: 100%;
    }
    .mp-hero {
        padding: 25px 15px;
    }
    .mp-card {
        padding: 15px;
    }
}
</style>
"""

# --- 0. COMPONENT COMPATIBILITY ---
# Define which components work in WeChat vs HTML
COMPONENT_COMPATIBILITY = {
    "hero": {"wechat": True, "html": True},
    "col-2": {"wechat": True, "html": True},
    "col-3": {"wechat": True, "html": True},
    "steps": {"wechat": True, "html": True},
    "timeline": {"wechat": True, "html": True},
    "reveal": {"wechat": False, "html": True},  # Uses SVG animations - not WeChat compatible
    "badge": {"wechat": True, "html": True},
    "button": {"wechat": True, "html": True},
    "card": {"wechat": True, "html": True},
    "img": {"wechat": True, "html": True},
    "table": {"wechat": True, "html": True},
    "video": {"wechat": True, "html": True},
}

# --- 1. TOOLBAR CONFIGURATION ---
INSERTION_TOOLS = {
    "➕ Hero": "::: hero\n# Title\nSubtitle\n:::",
    "➕ 2-Col": "::: col-2\nLeft\n--split--\nRight\n:::",
    "➕ 3-Col": "::: col-3\nOne\n--split--\nTwo\n--split--\nThree\n:::",
    "➕ Steps": "::: steps\n1. Step One\n2. Step Two\n:::",
    "➕ Timeline": "::: timeline\n2024 Start\n2025 Launch\n:::",
    "➕ Table": "::: table\nHeader 1 | Header 2 | Header 3\nRow 1 Col 1 | Row 1 Col 2 | Row 1 Col 3\nRow 2 Col 1 | Row 2 Col 2 | Row 2 Col 3\n:::",
    "➕ Reveal": "::: reveal\nSecret Content\n--cover--\n👆\n:::",
    "➕ Badge": "[badge: NEW]",
    "➕ Button": "\n[Button Label](https://link.com)\n",
    "➕ Card": "::: card\n## Card Title\nCard content here.\n:::",
    "➕ AI Image": "[IMG: describe your image]"
}

# --- 2. PARSING ENGINE ---
def apply_components(text, styles, mode="web", img_provider="Pollinations (AI)"):
    s = styles
    # Helper: Styles for WeChat images
    img_s = f'style="{s["img"]}"' if mode=="wechat" else ''
    
    # --- A. IMAGE HANDLERS ---
    
    # 1. Local Images (Session State + Library Fallback)
    # Replaces [LOCAL: filename.png] with base64 data URI
    def local_img_repl(m):
        f_name = m.group(1).strip()
        
        # First, try session state
        if "local_images" in st.session_state and f_name in st.session_state.local_images:
            b64 = st.session_state.local_images[f_name]
            return f'\n<img src="{b64}" {img_s} alt="Image">\n'
        
        # If not in session state, try loading from library
        if load_image_from_library:
            # Try loading by exact filename first
            img_data = load_image_from_library(f_name)
            if img_data:
                # Cache it in session state for future use
                if "local_images" not in st.session_state:
                    st.session_state.local_images = {}
                st.session_state.local_images[f_name] = img_data
                return f'\n<img src="{img_data}" {img_s} alt="Image">\n'
            
            # If not found by filename, try searching by original_name in metadata
            if get_image_library:
                library_images = get_image_library()
                # Normalize the search name (remove path separators, handle case)
                search_name = f_name.strip()
                search_name_lower = search_name.lower()
                
                for img_info in library_images:
                    # Check if the original_name matches (exact or case-insensitive)
                    original_name = img_info.get("original_name", "")
                    original_name_lower = original_name.lower()
                    
                    # Try multiple matching strategies
                    if (original_name == search_name or 
                        original_name_lower == search_name_lower or
                        original_name.endswith(search_name) or
                        original_name_lower.endswith(search_name_lower) or
                        os.path.basename(original_name) == os.path.basename(search_name)):
                        # Found by original name, load the actual library file
                        library_filename = img_info["filename"]
                        img_data = load_image_from_library(library_filename)
                        if img_data:
                            # Cache it in session state for future use
                            if "local_images" not in st.session_state:
                                st.session_state.local_images = {}
                            st.session_state.local_images[f_name] = img_data
                            return f'\n<img src="{img_data}" {img_s} alt="Image">\n'
        
        return f"\n> ⚠️ Image not found: {f_name}\n"
    
    # Case Insensitive regex for [LOCAL: ...]
    text = re.sub(r'\[LOCAL:\s*(.*?)\]', local_img_repl, text, flags=re.IGNORECASE)

    # 2. AI / Web Images
    # Replaces [IMG: prompt] with URL based on provider
    def web_img_repl(m):
        prompt = m.group(1)
        encoded = urllib.parse.quote(prompt)
        seed = random.randint(0, 9999)
        
        if img_provider == "Picsum (Stock)":
            # Picsum doesn't support text prompts, so we use seed
            url = f"https://picsum.photos/seed/{seed}/800/450"
        elif img_provider == "Placeholder (Text)":
            # Simple placeholder with text
            url = f"https://placehold.co/800x450/EEE/31343C?text={encoded}"
        elif img_provider.startswith("Gradient"):
            # Beautiful CSS gradient images using inline SVG - compact and layout-friendly
            # These create modern, attractive gradient images without breaking layout
            gradient_styles = {
                "Gradient (Blue)": {
                    "gradient": '<linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#667eea;stop-opacity:1" /><stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" /></linearGradient>',
                    "emoji": "💙"
                },
                "Gradient (Purple)": {
                    "gradient": '<linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#f093fb;stop-opacity:1" /><stop offset="100%" style="stop-color:#f5576c;stop-opacity:1" /></linearGradient>',
                    "emoji": "💜"
                },
                "Gradient (Sunset)": {
                    "gradient": '<linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#fa709a;stop-opacity:1" /><stop offset="100%" style="stop-color:#fee140;stop-opacity:1" /></linearGradient>',
                    "emoji": "🌅"
                },
                "Gradient (Ocean)": {
                    "gradient": '<linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#4facfe;stop-opacity:1" /><stop offset="100%" style="stop-color:#00f2fe;stop-opacity:1" /></linearGradient>',
                    "emoji": "🌊"
                },
                "Gradient (Forest)": {
                    "gradient": '<linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#11998e;stop-opacity:1" /><stop offset="100%" style="stop-color:#38ef7d;stop-opacity:1" /></linearGradient>',
                    "emoji": "🌲"
                },
                "Gradient (Aurora)": {
                    "gradient": '<linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#a18cd1;stop-opacity:1" /><stop offset="100%" style="stop-color:#fbc2eb;stop-opacity:1" /></linearGradient>',
                    "emoji": "✨"
                },
                "Gradient (Fire)": {
                    "gradient": '<linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#f83600;stop-opacity:1" /><stop offset="100%" style="stop-color:#f9d423;stop-opacity:1" /></linearGradient>',
                    "emoji": "🔥"
                },
                "Gradient (Midnight)": {
                    "gradient": '<linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#2c3e50;stop-opacity:1" /><stop offset="100%" style="stop-color:#4ca1af;stop-opacity:1" /></linearGradient>',
                    "emoji": "🌙"
                }
            }
            
            # Get gradient style or use default
            gradient_info = gradient_styles.get(img_provider, gradient_styles["Gradient (Blue)"])
            gradient_svg = gradient_info["gradient"]
            emoji = gradient_info.get("emoji", "🎨")
            
            # Clean prompt for text display
            display_text = prompt.strip() if prompt.strip() else "Gradient"
            
            # Create compact SVG image with gradient and text
            # Using data URI to embed SVG directly
            text_encoded = urllib.parse.quote(display_text)
            emoji_encoded = urllib.parse.quote(emoji)
            
            # Build SVG with gradient background (800x450 to match placeholder ratio)
            svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="450" viewBox="0 0 800 450">
  <defs>{gradient_svg}</defs>
  <rect width="800" height="450" fill="url(#grad1)"/>
  <text x="400" y="225" font-family="Arial, sans-serif" font-size="36" fill="white" text-anchor="middle" dominant-baseline="middle" font-weight="bold">{emoji} {display_text}</text>
</svg>'''
            
            # Convert to data URI
            svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
            url = f"data:image/svg+xml;base64,{svg_base64}"
            
            return f'\n<img src="{url}" {img_s} alt="{display_text}" style="border-radius: 8px;">\n'
        elif img_provider.startswith("Pattern"):
            # Real pattern backgrounds using inline SVG patterns
            # Create proper dot and line patterns
            if "Dots" in img_provider:
                # Polka dots pattern
                pattern_svg = '''<defs>
    <pattern id="dotPattern" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
      <circle cx="20" cy="20" r="8" fill="rgba(255,255,255,0.25)"/>
    </pattern>
  </defs>
  <rect width="800" height="450" fill="#607d8b"/>
  <rect width="800" height="450" fill="url(#dotPattern)"/>'''
                emoji = "🔵"
            else:
                # Diagonal lines pattern
                pattern_svg = '''<defs>
    <pattern id="linePattern" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="20" stroke="rgba(255,255,255,0.25)" stroke-width="3"/>
    </pattern>
  </defs>
  <rect width="800" height="450" fill="#78909c"/>
  <rect width="800" height="450" fill="url(#linePattern)"/>'''
                emoji = "📐"
            
            # Clean prompt for text display
            display_text = prompt.strip() if prompt.strip() else "Pattern"
            
            # Build SVG with pattern background (800x450 to match placeholder ratio)
            svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="450" viewBox="0 0 800 450">
  {pattern_svg}
  <text x="400" y="225" font-family="Arial, sans-serif" font-size="36" fill="white" text-anchor="middle" dominant-baseline="middle" font-weight="bold">{emoji} {display_text}</text>
</svg>'''
            
            # Convert to data URI
            svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
            url = f"data:image/svg+xml;base64,{svg_base64}"
            
            return f'\n<img src="{url}" {img_s} alt="{display_text}" style="border-radius: 8px;">\n'
        else:
            # Pollinations AI (Default)
            # URL format: https://image.pollinations.ai/prompt/{encoded}?width=800&height=450&nologo=true&seed={seed}
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=450&nologo=true&seed={seed}"
            
        return f'\n<img src="{url}" {img_s} alt="AI Generated">\n'
    
    # Case Insensitive regex for [IMG: ...]
    text = re.sub(r'\[IMG:\s*(.*?)\]', web_img_repl, text, flags=re.IGNORECASE)

    # 2.5 Video Component
    # Syntax: ::: video src="https://..." poster="" caption="" autoplay=false muted=false loop=false :::
    def video_r(m):
        attrs_raw = m.group(1).strip()
        attrs = {}
        for token in shlex.split(attrs_raw):
            if "=" in token:
                k, v = token.split("=", 1)
                attrs[k.strip()] = v.strip().strip('"')
        src = attrs.get("src", "").strip()
        poster = attrs.get("poster", "").strip()
        caption = attrs.get("caption", "").strip()
        def as_bool(val: str):
            return str(val).lower() in {"1", "true", "yes", "on"}
        autoplay = as_bool(attrs.get("autoplay", "false"))
        muted = as_bool(attrs.get("muted", "false"))
        loop = as_bool(attrs.get("loop", "false"))

        if not src:
            return "\\n> ⚠️ Video source missing\\n"

        video_attrs = ['controls', 'preload="metadata"']
        if poster:
            video_attrs.append(f'poster="{poster}"')
        if autoplay:
            video_attrs.append("autoplay")
        if muted:
            video_attrs.append("muted")
        if loop:
            video_attrs.append("loop")

        wrapper_style = "position:relative;width:100%;max-width:900px;margin:12px auto;"
        video_style = "width:100%;height:auto;display:block;"
        cap_html = f'<div style="font-size:13px;color:#666;margin-top:6px;text-align:center;">{caption}</div>' if caption else ""

        return (f'<div class="mp-video" style="{wrapper_style}">'
                f'<video src="{src}" style="{video_style}" {" ".join(video_attrs)}></video>'
                f'{cap_html}'
                f'</div>')

    text = re.sub(r'(?is):::\s*video\s*(.*?)\s*:::', video_r, text)
    
    # --- B. LAYOUT COMPONENTS ---

    # 3. Hero Component
    # Syntax: ::: hero \n # Title \n Sub \n :::
    def hero_r(m):
        c = m.group(1)
        # Process H1 to add center alignment inline style
        h1_style_raw = s["h1"]
        h1_centered = h1_style_raw.replace("text-align: left", "text-align: center")
        if "text-align: center" not in h1_centered:
            h1_centered += " text-align: center;"
        
        # Replace markdown # with styled H1
        c = re.sub(r'^# (.*)', f'<h1 style="{h1_centered}">\\1</h1>', c, flags=re.MULTILINE)
        
        # Add text-align: center to container's inline style to ensure centering
        hero_style = s["hero"] + " text-align: center;"
        
        if mode=="wechat": 
            return f'<section style="{hero_style}">{c}</section>' 
        else:
            return f'<div class="mp-hero" style="{hero_style}">{c}</div>'
            
    text = re.sub(r'(?is):::\s*hero\n(.*?)\n:::', hero_r, text)
    
    # 4. Steps Component
    # Syntax: ::: steps \n 1. Item \n 2. Item \n :::
    def steps_r(m):
        lines = [l.strip() for l in m.group(1).split('\n') if l.strip()]
        
        if mode == "wechat": 
            # WeChat mode - use inline styles
            html = '<section class="mp-steps-wrapper" style="margin: 20px 0; display: block; clear: both; width: 100%;">'
            for i, line in enumerate(lines, 1):
                content = re.sub(r'^\d+[\.\)]\s*', '', line)
                html += (f'<div style="{s["step_box"]}">'
                         f'<span style="{s["step_num"]}">{i}</span>'
                         f'<span style="flex: 1 1 auto; display: inline-block; vertical-align: middle;">{content}</span></div>')
            html += '</section>'
        else: 
            # Web mode - use CSS classes
            html = '<div class="mp-steps">'
            for i, line in enumerate(lines, 1):
                content = re.sub(r'^\d+[\.\)]\s*', '', line)
                html += (f'<div class="mp-step">'
                         f'<span class="mp-step__num">{i}</span>'
                         f'<span class="mp-step__content">{content}</span></div>')
            html += '</div>'
        return html
        
    text = re.sub(r'(?is):::\s*steps\n(.*?)\n:::', steps_r, text)

    # 5. Timeline Component
    # Syntax: ::: timeline \n Year Event \n :::
    def time_r(m):
        lines = [l.strip() for l in m.group(1).split('\n') if l.strip()]
        primary_color = s.get('primary', '#4A90E2')
        
        if mode == "wechat": 
            # WeChat mode - use inline styles
            html = '<section class="mp-timeline-wrapper" style="margin: 20px 0; padding-left: 15px; display: block; clear: both; width: 100%;">'
            for line in lines:
                html += (f'<div style="{s["time_box"]}">'
                         f'<span style="{s["time_dot"]}"></span>'
                         f'<span style="display: inline-block; vertical-align: middle;">{line}</span></div>')
            html += '</section>'
        else: 
            # Web mode - use CSS classes with dynamic primary color
            timeline_style = f'border-left-color: {primary_color};'
            dot_style = f'background-color: {primary_color};'
            html = '<div class="mp-timeline">'
            for line in lines:
                html += (f'<div class="mp-timeline__item" style="{timeline_style}">'
                         f'<span class="mp-timeline__dot" style="{dot_style}"></span>'
                         f'<span>{line}</span></div>')
            html += '</div>'
        return html
        
    text = re.sub(r'(?is):::\s*timeline\n(.*?)\n:::', time_r, text)

    # 6. Reveal Component (Interactive SVG)
    # Syntax: ::: reveal \n Hidden \n --cover-- \n Tap \n :::
    def reveal_r(m):
        content = m.group(1).strip()
        cover_text = m.group(2).strip() if m.group(2) else "Tap to Reveal"
        unique_id = f"rev_{random.randint(10000, 99999)}"
        
        # Get primary color for styling
        primary_color = s.get("primary", "#4A90E2")
        
        # WeChat mode uses basic inline styles, web mode uses CSS classes
        if mode == "wechat":
            inner_style = (f'border: 1px dashed #ccc; padding: 15px; border-radius: 8px; '
                          f'background: #fff; min-height: 100px; display: flex; '
                          f'align-items: center; justify-content: center; text-align: center;')
            box_style = s.get('reveal_box', 'position: relative; margin: 20px 0; cursor: pointer; overflow: hidden; border-radius: 8px;')
            
            svg_overlay = f"""
            <div style="position: absolute; top:0; left:0; width:100%; height:100%; z-index:10;">
                <svg style="width:100%; height:100%; cursor:pointer;" viewBox="0 0 300 100" preserveAspectRatio="none">
                    <g style="cursor:pointer;" pointer-events="all">
                        <rect width="100%" height="100%" fill="{primary_color}" rx="8" />
                        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="white" font-weight="bold" font-size="24">{cover_text}</text>
                        <animate attributeName="opacity" begin="click;touchstart" from="1" to="0" dur="0.3s" fill="freeze" restart="never" />
                        <set attributeName="visibility" to="hidden" begin="click+0.3s;touchstart+0.3s" />
                    </g>
                </svg>
            </div>
            """
            return f'<section style="{box_style}" id="{unique_id}"><div style="{inner_style}">{content}</div>{svg_overlay}</section>'
        else:
            # Web mode - use CSS classes
            return f"""
            <div class="mp-reveal" id="{unique_id}">
                <div class="mp-reveal__content">{content}</div>
                <div class="mp-reveal__overlay">
                    <svg style="width:100%; height:100%; cursor:pointer;" viewBox="0 0 300 100" preserveAspectRatio="none">
                        <g style="cursor:pointer;" pointer-events="all">
                            <rect width="100%" height="100%" fill="{primary_color}" rx="8" />
                            <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="white" font-weight="bold" font-size="24">{cover_text}</text>
                            <animate attributeName="opacity" begin="click;touchstart" from="1" to="0" dur="0.3s" fill="freeze" restart="never" />
                            <set attributeName="visibility" to="hidden" begin="click+0.3s;touchstart+0.3s" />
                        </g>
                    </svg>
                </div>
            </div>
            """
    
    text = re.sub(r'(?is):::\s*reveal\s*(.*?)\s*--cover--\s*(.*?)\s*:::', reveal_r, text)

    # 7. Custom Badge Replacement
    # Syntax: [badge: Text]
    badge_style = s.get("badge", f"background-color: {s.get('primary', '#4A90E2')}20; color: {s.get('primary', '#4A90E2')}; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; vertical-align: middle; margin-right: 5px;")
    text = re.sub(r'\[badge:\s*(.*?)\]', f'<span class="mp-badge" style="{badge_style}">\\1</span>', text, flags=re.IGNORECASE)

    # 8. Grid Layout (2 or 3 columns)
    # Syntax: ::: col-2 \n A --split-- B \n :::
    def grid_r(m, cols):
        parts = [x.strip() for x in m.group(1).split("--split--") if x.strip()]
        if len(parts) < 2: return m.group(0) # fallback if not enough parts
        
        if mode=="wechat":
            col_html = "".join([f'<div style="{s["col"]}">{p}</div>' for p in parts])
            return f'<section style="{s["grid"]}">{col_html}</section>'
        else:
            col_html = "".join([f'<div class="mp-col">{p}</div>' for p in parts])
            return f'<div class="mp-grid">{col_html}</div>'
    
    text = re.sub(r'(?is):::\s*col-2\n(.*?)\n:::', lambda m: grid_r(m, 2), text)
    text = re.sub(r'(?is):::\s*col-3\n(.*?)\n:::', lambda m: grid_r(m, 3), text)

    # 8.5. Table Component
    # Syntax: ::: table \n Header1 | Header2 \n Row1Col1 | Row1Col2 \n :::
    def table_r(m):
        lines = [l.strip() for l in m.group(1).split('\n') if l.strip()]
        if not lines:
            return m.group(0)
        
        primary_color = s.get('primary', '#4A90E2')
        card_bg = s.get('card', '#f8f9fa')
        
        # WeChat mode uses inline styles, web mode uses CSS classes
        if mode == "wechat":
            table_style = "width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px;"
            th_style = f"background-color: {primary_color}; color: white; padding: 12px 15px; text-align: left; border: 1px solid #ddd; font-weight: bold;"
            td_style = "padding: 12px 15px; text-align: left; border: 1px solid #ddd;"
            tr_even_style = f"background-color: {card_bg};"
            
            html = f'<table style="{table_style}">'
            for idx, line in enumerate(lines):
                cells = [c.strip() for c in line.split('|')]
                if idx == 0:
                    html += '<thead><tr>'
                    for cell in cells:
                        html += f'<th style="{th_style}">{cell}</th>'
                    html += '</tr></thead><tbody>'
                else:
                    row_bg = tr_even_style if idx % 2 == 0 else ""
                    html += f'<tr style="{row_bg}">'
                    for cell in cells:
                        html += f'<td style="{td_style}">{cell}</td>'
                    html += '</tr>'
            html += '</tbody></table>'
        else:
            # Web mode - use CSS classes
            th_style = f"background-color: {primary_color}; color: white;"
            tr_even_style = f"background-color: {card_bg};"
            
            html = '<table class="mp-table">'
            for idx, line in enumerate(lines):
                cells = [c.strip() for c in line.split('|')]
                if idx == 0:
                    html += '<thead><tr>'
                    for cell in cells:
                        html += f'<th style="{th_style}">{cell}</th>'
                    html += '</tr></thead><tbody>'
                else:
                    row_bg = tr_even_style if idx % 2 == 0 else ""
                    html += f'<tr style="{row_bg}">'
                    for cell in cells:
                        html += f'<td>{cell}</td>'
                    html += '</tr>'
            html += '</tbody></table>'
        return html
    
    text = re.sub(r'(?is):::\s*table\n(.*?)\n:::', table_r, text)

    # --- C. DECORATIONS ---

    # 9. Button Links
    # Syntax: [Label](url) on its own line
    if mode == "wechat": 
        btn_style = s.get("btn", f"background-color: {s.get('primary', '#4A90E2')}; color: #fff; padding: 10px 25px; border-radius: {s.get('radius', '8px')}; text-decoration: none; display: inline-block; font-weight: bold;")
        text = re.sub(r'(?m)^\[(.*?)\]\((.*?)\)\s*$', 
                      f'<div style="{s["btn_wrap"]}"><a href="\\2" style="{btn_style}">\\1</a></div>', text)
    else: 
        btn_style = s.get("btn", f"background-color: {s.get('primary', '#4A90E2')}; color: #fff;")
        text = re.sub(r'(?m)^\[(.*?)\]\((.*?)\)\s*$', 
                      f'<div class="mp-btn-wrap"><a href="\\2" class="mp-btn" style="{btn_style}">\\1</a></div>', text)
    
    # 10. Card Component (Explicit syntax to avoid conflict with H2)
    # Syntax: ::: card \n ## Title \n Content \n :::
    def card_r(m):
        content = m.group(1).strip()
        # Extract header (first ## line) and body (rest)
        lines = content.split('\n')
        header = None
        body_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith('##') and header is None:
                header = line_stripped.lstrip('#').strip()
            elif line_stripped:  # Only add non-empty lines to body
                body_lines.append(line)
        
        body = '\n'.join(body_lines).strip()
        h_col = s.get("card_h_color", "#007aff")
        
        if mode=="wechat": 
            return (f'<section style="{s["card"]}">'
                    f'<span style="font-weight:bold; font-size:16px; color:{h_col}">{header or "Card"}</span>'
                    f'<div style="margin-top:8px">{body}</div></section>')
        else: 
            return f'<div class="mp-card"><h3>{header or "Card"}</h3>{body}</div>'
    
    # Card component - handle multiline content properly
    text = re.sub(r'(?is):::\s*card\s*\n(.*?)\n:::', card_r, text)
    
    return text

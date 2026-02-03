"""
PDF generation module for MarkPolish Studio
Handles PDF export with support for multiple PDF libraries
"""

import os
import re
import base64
import random
import platform
import urllib.parse
from io import BytesIO
from html.parser import HTMLParser
from PIL import Image
import requests
import streamlit as st

# Import error handler if available
try:
    from error_handler import ErrorHandler
except ImportError:
    ErrorHandler = None

# Import image handling for load_image_from_library
try:
    from image_handling import load_image_from_library
except ImportError:
    def load_image_from_library(filename):
        return None

# Z-Image-Turbo: DashScope and ModelScope (魔搭) for AI image generation
try:
    from z_image import (
        generate_image as z_image_generate,
        generate_image_modelscope,
        get_dashscope_api_key,
        get_modelscope_api_key,
        IMAGE_SIZE_PRESETS,
    )
except ImportError:
    z_image_generate = None
    generate_image_modelscope = None
    get_dashscope_api_key = None
    get_modelscope_api_key = None
    IMAGE_SIZE_PRESETS = {"1:1": "1024*1024", "16:9": "1280*720", "9:16": "720*1280"}

# Daily usage limits for AI image providers
try:
    from ai_image_usage import is_over_limit as ai_usage_is_over_limit, increment_usage as ai_usage_increment
except ImportError:
    ai_usage_is_over_limit = lambda _: False
    ai_usage_increment = lambda _: None

# Check for PDF libraries
HAS_WEASYPRINT = False
HAS_PDFKIT = False
HAS_XHTML2PDF = False
HAS_REPORTLAB = False

try:
    from weasyprint import HTML, CSS
    HAS_WEASYPRINT = True
except (ImportError, OSError):
    HAS_WEASYPRINT = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
    from reportlab.lib.colors import HexColor
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    from xhtml2pdf import pisa
    HAS_XHTML2PDF = True
except (ImportError, OSError):
    HAS_XHTML2PDF = False

try:
    import pdfkit
    HAS_PDFKIT = True
except ImportError:
    HAS_PDFKIT = False


class HTMLToPDFParser(HTMLParser):
    """Parse HTML and extract structured content for PDF"""
    def __init__(self):
        super().__init__()
        self.elements = []
        self.current_text = []
        self.current_tag = None
        self.in_code = False
        
    def handle_starttag(self, tag, attrs):
        # Save any accumulated text before tag
        if self.current_text:
            text = ''.join(self.current_text).strip()
            if text:
                self.elements.append(('text', text, self.current_tag))
            self.current_text = []
        
        self.current_tag = tag
        
        # Handle images
        if tag == 'img':
            img_src = None
            for attr_name, attr_value in attrs:
                if attr_name == 'src':
                    img_src = attr_value
                    break
            if img_src:
                self.elements.append(('image', img_src, None))
        
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag[1]) if len(tag) > 1 else 1
            self.elements.append(('heading', level, None))
        elif tag == 'p':
            self.elements.append(('paragraph', None, None))
        elif tag in ['ul', 'ol']:
            self.elements.append(('list_start', tag, None))
        elif tag == 'li':
            self.elements.append(('list_item', None, None))
        elif tag in ['code', 'pre']:
            self.in_code = True
        elif tag == 'br':
            self.elements.append(('linebreak', None, None))
        elif tag in ['section', 'div']:
            # Extract style attributes to detect component types
            style_attr = None
            class_attr = None
            for attr_name, attr_value in attrs:
                if attr_name == 'style':
                    style_attr = attr_value
                elif attr_name == 'class':
                    class_attr = attr_value
            
            # Detect component type from style or class - be more lenient
            component_type = 'normal'
            if style_attr:
                style_lower = style_attr.lower()
                # More flexible detection
                if 'hero' in style_lower or ('background' in style_lower and ('center' in style_lower or 'padding' in style_lower)):
                    component_type = 'hero'
                elif 'card' in style_lower or 'border-left' in style_lower:
                    component_type = 'card'
                elif 'grid' in style_lower or 'display: flex' in style_lower or 'display:grid' in style_lower:
                    component_type = 'grid'
                # Also check for common styling patterns
                elif 'border-radius' in style_lower and 'padding' in style_lower:
                    # Likely a card or styled box
                    component_type = 'card'
            elif class_attr:
                class_lower = class_attr.lower()
                if 'hero' in class_lower or 'mp-hero' in class_lower:
                    component_type = 'hero'
                elif 'card' in class_lower or 'mp-card' in class_lower:
                    component_type = 'card'
                elif 'grid' in class_lower or 'mp-grid' in class_lower:
                    component_type = 'grid'
            
            # If it's a section tag, always treat it as a styled component
            if tag == 'section' and component_type == 'normal':
                # Check if it has any styling at all
                if style_attr:
                    style_lower = style_attr.lower()
                    if 'background' in style_lower or 'border' in style_lower or 'padding' in style_lower:
                        component_type = 'card'  # Default to card styling
                # Even without explicit style, if it's a section tag, treat as styled
                elif tag == 'section':
                    component_type = 'card'  # Default styling for sections
            
            # Extract style properties for rendering
            bg_color = None
            border_color = None
            padding = None
            border_radius = None
            box_shadow = None
            border_width = None
            border_style = None
            
            if style_attr:
                # Extract background-color
                bg_match = re.search(r'background(?:-color)?:\s*([^;]+)', style_attr, re.IGNORECASE)
                if bg_match:
                    bg_color = bg_match.group(1).strip()
                
                # Extract border properties
                # Try border-left first (for cards)
                border_left_match = re.search(r'border-left:\s*(\d+)px\s+solid\s+([^;]+)', style_attr, re.IGNORECASE)
                if border_left_match:
                    border_width = float(border_left_match.group(1))
                    border_color = border_left_match.group(2).strip()
                    border_style = 'left'
                else:
                    # Try general border
                    border_match = re.search(r'border(?:-color)?:\s*([^;]+)', style_attr, re.IGNORECASE)
                    if border_match:
                        border_str = border_match.group(1).strip()
                        # Parse border: width style color
                        border_parts = border_str.split()
                        if len(border_parts) >= 3:
                            try:
                                border_width = float(border_parts[0].replace('px', ''))
                                border_style = border_parts[1]
                                border_color = border_parts[2]
                            except:
                                border_color = border_str
                
                # Extract padding
                padding_match = re.search(r'padding:\s*([^;]+)', style_attr, re.IGNORECASE)
                if padding_match:
                    padding = padding_match.group(1).strip()
                
                # Extract border-radius
                radius_match = re.search(r'border-radius:\s*([^;]+)', style_attr, re.IGNORECASE)
                if radius_match:
                    radius_str = radius_match.group(1).strip()
                    # Extract numeric value (e.g., "16px" -> 16)
                    radius_val = re.search(r'(\d+(?:\.\d+)?)', radius_str)
                    if radius_val:
                        border_radius = float(radius_val.group(1))
                
                # Extract box-shadow
                shadow_match = re.search(r'box-shadow:\s*([^;]+)', style_attr, re.IGNORECASE)
                if shadow_match:
                    box_shadow = shadow_match.group(1).strip()
            
            self.elements.append(('section_start', component_type, {
                'bg_color': bg_color,
                'border_color': border_color,
                'border_width': border_width,
                'border_style': border_style,
                'padding': padding,
                'border_radius': border_radius,
                'box_shadow': box_shadow,
                'style': style_attr
            }))
    
    def handle_endtag(self, tag):
        if self.current_text:
            text = ''.join(self.current_text).strip()
            if text:
                self.elements.append(('text', text, self.current_tag))
            self.current_text = []
        
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.elements.append(('heading_end', None, None))
        elif tag == 'p':
            self.elements.append(('paragraph_end', None, None))
        elif tag in ['ul', 'ol']:
            self.elements.append(('list_end', None, None))
        elif tag in ['section', 'div']:
            self.elements.append(('section_end', None, None))
        elif tag in ['code', 'pre']:
            self.in_code = False
        
        self.current_tag = None
    
    def handle_data(self, data):
        if not self.in_code:
            # Clean up whitespace
            data = data.replace('\n', ' ').replace('\r', ' ')
            data = ' '.join(data.split())  # Normalize whitespace
        self.current_text.append(data)
    
    def handle_entityref(self, name):
        # Handle named entities like &nbsp;
        entity_map = {
            'nbsp': ' ',
            'amp': '&',
            'lt': '<',
            'gt': '>',
            'quot': '"',
        }
        char = entity_map.get(name, '')
        self.current_text.append(char)
    
    def handle_charref(self, name):
        # Handle numeric entities like &#160;
        try:
            if name.startswith('x'):
                char = chr(int(name[1:], 16))
            else:
                char = chr(int(name))
            self.current_text.append(char)
        except:
            pass


def parse_html_for_pdf(html_content):
    """Parse HTML and return structured elements for PDF generation"""
    parser = HTMLToPDFParser()
    parser.feed(html_content)
    parser.close()
    
    # Handle any remaining text
    if parser.current_text:
        text = ''.join(parser.current_text).strip()
        if text:
            parser.elements.append(('text', text, None))
    
    return parser.elements


def extract_images_from_html(html_content):
    """Extract image URLs from HTML img tags"""
    images = []
    # Find all img tags
    img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
    matches = re.finditer(img_pattern, html_content, re.IGNORECASE)
    for match in matches:
        img_url = match.group(1)
        images.append(img_url)
    return images


def clean_text_for_pdf(text):
    """Clean text for PDF - remove HTML, special chars, and normalize (preserve Unicode/Chinese)"""
    if not text:
        return ""
    
    # Remove all HTML tags completely
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    
    # Remove markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Italic
    text = re.sub(r'`([^`]+)`', r'\1', text)  # Code
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Links
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)  # Images
    
    # Handle special shortcodes
    text = re.sub(r'\[IMG:[^\]]+\]', '[Image]', text)
    text = re.sub(r'\[LOCAL:[^\]]+\]', '[Image]', text)
    text = re.sub(r':::hero\s+([^:]+):::', r'\1', text)
    text = re.sub(r':::card\s+([^:]+):::', r'\1', text)
    
    # Normalize whitespace (but preserve Unicode characters)
    text = ' '.join(text.split())
    
    # Keep all Unicode characters (including Chinese, Japanese, Korean, etc.)
    # Only remove control characters and problematic formatting
    cleaned = []
    for char in text:
        # Keep all printable characters including Unicode
        if char.isprintable() or char.isspace():
            cleaned.append(char)
        elif char in ['\n', '\t', '\r']:
            cleaned.append(' ')
    
    return ''.join(cleaned)


def extract_image_url(markdown_text, img_provider="ModelScope (AI)", img_ratio="1:1"):
    """Extract image URLs from [IMG:...] and [LOCAL:...] shortcodes"""
    images = {}
    size_str = IMAGE_SIZE_PRESETS.get(img_ratio, "1024*1024") if img_ratio else "1024*1024"

    # Width/height from ratio for Picsum and Placeholder (same ratio logic as AI images)
    def _w_h_from_ratio():
        if "*" in size_str:
            parts = size_str.strip().split("*", 1)
            try:
                return int(parts[0].strip()), int(parts[1].strip())
            except (ValueError, IndexError):
                pass
        return 800, 450

    # Extract [IMG: prompt] - convert to URL or data URI
    def img_repl(m):
        prompt = m.group(1).strip()
        encoded = urllib.parse.quote(prompt)
        seed = random.randint(0, 9999)
        img_w, img_h = _w_h_from_ratio()

        if img_provider == "Z-Image-Turbo (AI)":
            cache = st.session_state.get("ai_image_cache", {})
            cache_key = f"{img_provider}|{img_ratio}|{prompt}"
            url = cache.get(cache_key)
            if not url and z_image_generate:
                if ai_usage_is_over_limit(img_provider):
                    try:
                        st.session_state["ai_image_limit_reached"] = img_provider
                    except Exception:
                        pass
                    url = f"https://placehold.co/{img_w}x{img_h}/EEE/31343C?text={encoded}"
                else:
                    api_key = get_dashscope_api_key() if get_dashscope_api_key else None
                    url = z_image_generate(prompt, api_key=api_key, size=size_str)
                    if url:
                        ai_usage_increment(img_provider)
                        try:
                            st.session_state["ai_image_quota_just_updated"] = True
                        except Exception:
                            pass
                        if "ai_image_cache" not in st.session_state:
                            st.session_state["ai_image_cache"] = {}
                        st.session_state["ai_image_cache"][cache_key] = url
                        while len(st.session_state["ai_image_cache"]) > 30:
                            k = next(iter(st.session_state["ai_image_cache"]))
                            del st.session_state["ai_image_cache"][k]
            key = f"[IMG:{prompt}]"
            images[key] = url if url else f"https://placehold.co/{img_w}x{img_h}/EEE/31343C?text={encoded}"
            return key
        elif img_provider == "ModelScope (AI)":
            cache = st.session_state.get("ai_image_cache", {})
            cache_key = f"{img_provider}|{img_ratio}|{prompt}"
            url = cache.get(cache_key)
            if not url and generate_image_modelscope:
                if ai_usage_is_over_limit(img_provider):
                    try:
                        st.session_state["ai_image_limit_reached"] = img_provider
                    except Exception:
                        pass
                    url = f"https://placehold.co/{img_w}x{img_h}/EEE/31343C?text={encoded}"
                else:
                    api_key = get_modelscope_api_key() if get_modelscope_api_key else None
                    url = generate_image_modelscope(prompt, api_key=api_key, size=size_str)
                    if url:
                        ai_usage_increment(img_provider)
                        try:
                            st.session_state["ai_image_quota_just_updated"] = True
                        except Exception:
                            pass
                        if "ai_image_cache" not in st.session_state:
                            st.session_state["ai_image_cache"] = {}
                        st.session_state["ai_image_cache"][cache_key] = url
                        while len(st.session_state["ai_image_cache"]) > 30:
                            k = next(iter(st.session_state["ai_image_cache"]))
                            del st.session_state["ai_image_cache"][k]
            key = f"[IMG:{prompt}]"
            images[key] = url if url else f"https://placehold.co/{img_w}x{img_h}/EEE/31343C?text={encoded}"
            return key
        elif img_provider == "Picsum (Stock)":
            url = f"https://picsum.photos/seed/{seed}/{img_w}/{img_h}"
        elif img_provider == "Placeholder (Text)":
            url = f"https://placehold.co/{img_w}x{img_h}/EEE/31343C?text={encoded}"
        else:
            url = f"https://placehold.co/{img_w}x{img_h}/EEE/31343C?text={encoded}"
        
        key = f"[IMG:{prompt}]"
        images[key] = url
        return key
    
    # Extract [LOCAL: filename] - get from session state or library
    def local_repl(m):
        filename = m.group(1).strip()
        key = f"[LOCAL:{filename}]"
        
        # Try session state first
        if "local_images" in st.session_state and filename in st.session_state.local_images:
            images[key] = st.session_state.local_images[filename]
        else:
            # Try image library
            image_data = load_image_from_library(filename)
            if image_data:
                images[key] = image_data
            else:
                images[key] = None  # Image not found
        
        return key
    
    # Process the text to extract image references
    text = re.sub(r'\[IMG:\s*(.*?)\]', img_repl, markdown_text, flags=re.IGNORECASE)
    text = re.sub(r'\[LOCAL:\s*(.*?)\]', local_repl, text, flags=re.IGNORECASE)
    
    return images


def markdown_to_pdf_elements(markdown_text, images_dict=None):
    """Convert markdown text directly to PDF elements (bypassing HTML)"""
    elements = []
    lines = markdown_text.split('\n')
    
    in_list = False
    list_type = None  # 'ul' or 'ol'
    images_dict = images_dict or {}
    
    for line in lines:
        original_line = line
        line = line.strip()
        
        if not line:
            elements.append(('spacer', 6))
            continue
        
        # Check for image shortcodes BEFORE cleaning
        img_match = re.search(r'\[(IMG|LOCAL):\s*(.*?)\]', line, re.IGNORECASE)
        if img_match:
            img_key = img_match.group(0)
            if img_key in images_dict and images_dict[img_key]:
                elements.append(('image', images_dict[img_key], None))
                elements.append(('spacer', 12))
                # Remove image shortcode from line and continue processing rest
                line = line.replace(img_match.group(0), '').strip()
                if not line:
                    continue
        
        # Clean the line - remove HTML tags but preserve structure
        cleaned_line = re.sub(r'<[^>]+>', '', line)
        
        # Skip lines that are just HTML tags or empty after cleaning
        if not cleaned_line:
            continue
        
        # Headings
        if cleaned_line.startswith('#'):
            level = len(cleaned_line) - len(cleaned_line.lstrip('#'))
            heading_text = cleaned_line.lstrip('#').strip()
            heading_text = clean_text_for_pdf(heading_text)
            if heading_text:
                elements.append(('heading', heading_text, level))
                elements.append(('spacer', 12))
        # Unordered list
        elif cleaned_line.startswith('- ') or cleaned_line.startswith('* '):
            if not in_list:
                in_list = True
                list_type = 'ul'
            item_text = cleaned_line[2:].strip()
            item_text = clean_text_for_pdf(item_text)
            if item_text:
                elements.append(('list_item', item_text, 'ul'))
        # Ordered list
        elif re.match(r'^\d+\.\s', cleaned_line):
            if not in_list:
                in_list = True
                list_type = 'ol'
            item_text = re.sub(r'^\d+\.\s', '', cleaned_line).strip()
            item_text = clean_text_for_pdf(item_text)
            if item_text:
                elements.append(('list_item', item_text, 'ol'))
        # Bold text (markdown **text**)
        elif cleaned_line.startswith('**') and cleaned_line.endswith('**') and len(cleaned_line) > 4:
            text = cleaned_line[2:-2].strip()
            text = clean_text_for_pdf(text)
            if text:
                elements.append(('text', text, 'bold'))
                elements.append(('spacer', 6))
        # Regular paragraph
        else:
            if in_list:
                in_list = False
                elements.append(('spacer', 6))
            
            text = clean_text_for_pdf(cleaned_line)
            if text:
                elements.append(('text', text, 'normal'))
                elements.append(('spacer', 8))
    
    if in_list:
        elements.append(('spacer', 6))
    
    return elements


def generate_pdf(html_content, theme, output_path=None, markdown_source=None, img_provider="ModelScope (AI)", img_ratio="1:1"):
    """Generate PDF from HTML content with theme styling"""
    if not HAS_WEASYPRINT and not HAS_PDFKIT and not HAS_XHTML2PDF and not HAS_REPORTLAB:
        return None, "PDF library not installed. Install: python3 -m pip install reportlab"
    
    try:
        t = theme
        
        # Try weasyprint first (best quality)
        if HAS_WEASYPRINT:
            try:
                full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{ size: A4; margin: 2cm; }}
        body {{ font-family: {t['font']}; color: {t['text']}; line-height: 1.7; }}
        h1 {{ color: {t['primary']}; font-size: 24px; font-weight: bold; }}
        h2 {{ color: {t['primary']}; font-size: 18px; font-weight: bold; }}
        img {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>{html_content}</body>
</html>"""
                if output_path:
                    HTML(string=full_html).write_pdf(output_path)
                    return True, "Success"
                else:
                    pdf_bytes = HTML(string=full_html).write_pdf()
                    return pdf_bytes, "Success"
            except Exception:
                pass  # Fall through to other methods
        
        # Try xhtml2pdf
        if HAS_XHTML2PDF:
            try:
                from xhtml2pdf import pisa
                from io import BytesIO
                full_html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{{font-family:{t['font']};}}</style></head><body>{html_content}</body></html>"""
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(full_html.encode('utf-8')), result)
                if not pdf.err:
                    pdf_bytes = result.getvalue()
                    if output_path:
                        with open(output_path, 'wb') as f:
                            f.write(pdf_bytes)
                        return True, "Success"
                    return pdf_bytes, "Success"
            except Exception:
                pass
        
        # Use reportlab (pure Python, no system deps) - most reliable
        if HAS_REPORTLAB:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
            from reportlab.lib.colors import HexColor
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.colors import Color
            from reportlab.platypus import Table, TableStyle
            from reportlab.platypus.flowables import Flowable
            from io import BytesIO
            
            # Create PDF in memory
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=72)
            
            # Try to register a Unicode font for Chinese/Unicode support
            unicode_font_name = 'Helvetica'  # Default fallback
            unicode_bold_font_name = 'Helvetica-Bold'
            
            # Try to find and register a system font that supports Chinese
            system = platform.system()
            font_paths = []
            
            if system == 'Darwin':  # macOS
                font_paths = [
                    '/System/Library/Fonts/PingFang.ttc',
                    '/System/Library/Fonts/STHeiti Light.ttc',
                    '/System/Library/Fonts/Helvetica.ttc',
                    '/Library/Fonts/Arial Unicode.ttf',
                ]
            elif system == 'Windows':
                font_paths = [
                    'C:/Windows/Fonts/simsun.ttc',  # SimSun (Chinese)
                    'C:/Windows/Fonts/msyh.ttc',   # Microsoft YaHei
                    'C:/Windows/Fonts/arialuni.ttf',  # Arial Unicode
                ]
            elif system == 'Linux':
                font_paths = [
                    '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                ]
            
            # Try to register a Unicode font
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        # Register the font
                        pdfmetrics.registerFont(TTFont('UnicodeFont', font_path))
                        unicode_font_name = 'UnicodeFont'
                        unicode_bold_font_name = 'UnicodeFont'  # Use same font for bold
                        break
                except Exception:
                    continue
            
            # Create styles
            styles = getSampleStyleSheet()
            
            # Custom styles based on theme
            # Convert hex colors to RGB tuples for reportlab
            def hex_to_rgb(hex_color):
                """Convert hex color to RGB tuple (0-1 range for reportlab)"""
                hex_color = hex_color.replace('#', '') if hex_color.startswith('#') else hex_color
                try:
                    # Parse hex color (e.g., '007AFF' -> (0, 122, 255))
                    r = int(hex_color[0:2], 16) / 255.0
                    g = int(hex_color[2:4], 16) / 255.0
                    b = int(hex_color[4:6], 16) / 255.0
                    return (r, g, b)
                except Exception:
                    return (0, 0, 0)  # Fallback to black
            
            primary_color = Color(*hex_to_rgb(t['primary']))
            text_color = Color(*hex_to_rgb(t['text']))
            
            # Enhanced styling to match HTML version
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                textColor=primary_color,
                fontSize=26,
                spaceAfter=24,
                spaceBefore=12,
                alignment=TA_LEFT,
                fontName=unicode_bold_font_name,
                leading=32
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                textColor=primary_color,
                fontSize=20,
                spaceAfter=18,
                spaceBefore=16,
                alignment=TA_LEFT,
                fontName=unicode_bold_font_name,
                leading=24
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                textColor=text_color,
                fontSize=12,
                leading=18,
                alignment=TA_JUSTIFY,
                spaceAfter=14,
                spaceBefore=0,
                fontName=unicode_font_name,
                leftIndent=0,
                rightIndent=0
            )
            
            # Bold style for emphasized text
            bold_style = ParagraphStyle(
                'CustomBold',
                parent=normal_style,
                fontName=unicode_bold_font_name,
                fontSize=12
            )
            
            # Build story from markdown or HTML
            story = []
            
            # Extract images from markdown if available
            images_dict = {}
            if markdown_source:
                images_dict = extract_image_url(markdown_source, img_provider, img_ratio)
            
            # Prefer HTML parsing (since parsed_md is already processed to HTML)
            # Extract images from HTML first
            html_images = extract_images_from_html(html_content)
            
            # Use HTML parsing to get structure and images
            elements = parse_html_for_pdf(html_content)
            
            # Also try markdown parsing as fallback for shortcodes
            if markdown_source:
                md_images = extract_image_url(markdown_source, img_provider, img_ratio)
                # Merge markdown images into images_dict
                images_dict.update(md_images)
            
            # Initialize heading level tracker before processing elements
            current_heading_level = None  # Track heading level for HTML parser
            current_section = None  # Track current section styling
            section_content = []  # Collect content for styled sections
            
            # Helper function to parse CSS color to reportlab Color
            def parse_css_color(color_str):
                """Parse CSS color string to reportlab Color"""
                if not color_str:
                    return None
                color_str = color_str.strip()
                # Handle hex colors
                if color_str.startswith('#'):
                    return Color(*hex_to_rgb(color_str))
                # Handle rgb/rgba
                rgb_match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)', color_str)
                if rgb_match:
                    r = int(rgb_match.group(1)) / 255.0
                    g = int(rgb_match.group(2)) / 255.0
                    b = int(rgb_match.group(3)) / 255.0
                    return Color(r, g, b)
                # Handle named colors (basic set)
                color_map = {
                    'white': Color(1, 1, 1),
                    'black': Color(0, 0, 0),
                    'red': Color(1, 0, 0),
                    'green': Color(0, 1, 0),
                    'blue': Color(0, 0, 1),
                }
                if color_str.lower() in color_map:
                    return color_map[color_str.lower()]
                return None
            
            # Helper function to parse box-shadow
            def parse_box_shadow(shadow_str):
                """Parse CSS box-shadow to get offset, blur, and color"""
                if not shadow_str or shadow_str == 'none':
                    return None
                # Parse: "0 1px 3px rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.06)"
                # For simplicity, take the first shadow
                shadows = shadow_str.split(',')
                if shadows:
                    first_shadow = shadows[0].strip()
                    # Extract numbers and color
                    parts = re.findall(r'(-?\d+(?:\.\d+)?)\s*(?:px)?|rgba?\([^)]+\)|#[0-9a-fA-F]+', first_shadow)
                    if len(parts) >= 3:
                        try:
                            offset_x = float(parts[0]) if parts[0] else 0
                            offset_y = float(parts[1]) if len(parts) > 1 and parts[1] else 0
                            blur = float(parts[2]) if len(parts) > 2 and parts[2] else 0
                            # Extract color (last part)
                            color_str = parts[-1] if parts else 'rgba(0,0,0,0.1)'
                            shadow_color = parse_css_color(color_str) or Color(0, 0, 0, alpha=0.1)
                            return {
                                'offset_x': offset_x,
                                'offset_y': -offset_y,  # PDF Y is inverted
                                'blur': blur,
                                'color': shadow_color
                            }
                        except:
                            pass
                return None
            
            # Helper function to render styled section
            def render_styled_section(section_type, section_style, content_elements):
                """Render a styled section (hero, card, etc.) with background, borders, shadows, and rounded corners"""
                if not content_elements:
                    return
                
                # Parse style properties
                bg_color = None
                border_color = None
                border_width = None
                border_style_type = None
                padding_val = 15  # Default padding in points
                border_radius_val = 0
                shadow_info = None
                
                if section_style:
                    bg_color = parse_css_color(section_style.get('bg_color'))
                    border_color = parse_css_color(section_style.get('border_color'))
                    border_width = section_style.get('border_width')
                    border_style_type = section_style.get('border_style', 'left' if section_type == 'card' else None)
                    
                    if section_style.get('padding'):
                        # Parse padding (e.g., "15px" -> 15, "35px 20px" -> take first)
                        padding_str = section_style.get('padding')
                        padding_match = re.search(r'(\d+(?:\.\d+)?)', padding_str)
                        if padding_match:
                            padding_val = float(padding_match.group(1))
                    
                    if section_style.get('border_radius'):
                        border_radius_val = float(section_style.get('border_radius'))
                    
                    if section_style.get('box_shadow'):
                        shadow_info = parse_box_shadow(section_style.get('box_shadow'))
                
                # Default colors based on component type
                if section_type == 'hero':
                    if not bg_color:
                        bg_color = Color(0.95, 0.95, 0.98)  # Light background
                    if not border_color:
                        border_color = primary_color
                    if not border_width:
                        border_width = 0
                elif section_type == 'card':
                    if not bg_color:
                        bg_color = Color(0.98, 0.98, 0.98)  # Light gray
                    if not border_color:
                        border_color = primary_color
                    if not border_width:
                        border_width = 4  # Default left border width
                    if not border_style_type:
                        border_style_type = 'left'
                
                # Build content for the section - collect all flowables
                section_flowables = []
                for ce in content_elements:
                    if ce[0] == 'text':
                        text = ce[1]
                        if not text or not text.strip():
                            continue
                        text = clean_text_for_pdf(text)
                        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        if text:
                            try:
                                if isinstance(text, bytes):
                                    text = text.decode('utf-8', errors='ignore')
                                # Use title style for hero sections, normal for cards
                                style = title_style if section_type == 'hero' else normal_style
                                section_flowables.append(Paragraph(text, style))
                                section_flowables.append(Spacer(1, 6))
                            except:
                                pass
                    elif ce[0] == 'image':
                        # Image flowable
                        section_flowables.append(ce[1])
                        section_flowables.append(Spacer(1, 8))
                    elif ce[0] == 'heading':
                        text = ce[1] if len(ce) > 1 and ce[1] else None
                        level = ce[2] if len(ce) > 2 else 1
                        if text:
                            text = clean_text_for_pdf(text)
                            text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                            if text:
                                try:
                                    style = title_style if level == 1 else heading_style
                                    section_flowables.append(Paragraph(text, style))
                                    section_flowables.append(Spacer(1, 8))
                                except:
                                    pass
                
                if not section_flowables:
                    return
                
                # Create a custom flowable that combines styled box with content
                class StyledSectionFlowable(Flowable):
                    """Custom flowable that draws styled sections with content inside"""
                    def __init__(self, content_table, images_list, bg_color, border_color, border_width, border_style_type,
                                 padding, border_radius, shadow_info, section_type, width):
                        Flowable.__init__(self)
                        self.content_table = content_table
                        self.images_list = images_list
                        self.bg_color = bg_color or Color(1, 1, 1)
                        self.border_color = border_color
                        self.border_width = border_width or 0
                        self.border_style_type = border_style_type
                        self.padding = padding
                        self.border_radius = border_radius or 0
                        self.shadow_info = shadow_info
                        self.section_type = section_type
                        self.width = width
                        self.height = 0
                    
                    def wrap(self, availWidth, availHeight):
                        # Calculate content height
                        content_height = self.padding * 2  # Top and bottom padding
                        content_width = self.width - (self.padding * 2)
                        
                        # Wrap the content table
                        if self.content_table:
                            try:
                                w, h = self.content_table.wrap(content_width, availHeight)
                                content_height += h
                            except:
                                content_height += 50  # Fallback
                        
                        # Add image heights
                        for img in self.images_list:
                            if hasattr(img, 'wrap'):
                                try:
                                    w, h = img.wrap(content_width, availHeight)
                                    content_height += h + 8  # Image + spacing
                                except:
                                    content_height += 100  # Fallback
                        
                        self.height = max(content_height, self.padding * 2 + 20)  # Minimum height
                        return (self.width, self.height)
                    
                    def draw(self):
                        # Calculate box dimensions - full width, height from content
                        bg_x = self.padding
                        bg_y = 0
                        bg_w = self.width - (self.padding * 2)
                        bg_h = self.height
                        
                        # Draw shadow first (behind everything)
                        if self.shadow_info:
                            self.canv.saveState()
                            shadow_color = self.shadow_info.get('color')
                            if shadow_color is None:
                                shadow_color = Color(0, 0, 0, alpha=0.15)
                            
                            shadow_x = self.shadow_info.get('offset_x', 0)
                            shadow_y = self.shadow_info.get('offset_y', 0)
                            shadow_blur = max(self.shadow_info.get('blur', 0), 2)
                            
                            # Draw shadow offset
                            shadow_rect_x = bg_x + shadow_x
                            shadow_rect_y = bg_y + shadow_y
                            shadow_rect_w = bg_w
                            shadow_rect_h = bg_h
                            
                            self.canv.setFillColor(shadow_color)
                            
                            if self.border_radius > 0:
                                self.canv.roundRect(shadow_rect_x, shadow_rect_y, shadow_rect_w, shadow_rect_h,
                                                  self.border_radius, fill=1, stroke=0)
                            else:
                                self.canv.rect(shadow_rect_x, shadow_rect_y, shadow_rect_w, shadow_rect_h,
                                             fill=1, stroke=0)
                            self.canv.restoreState()
                        
                        # Draw background with rounded corners
                        self.canv.setFillColor(self.bg_color)
                        
                        if self.border_radius > 0:
                            self.canv.roundRect(bg_x, bg_y, bg_w, bg_h, self.border_radius, fill=1, stroke=0)
                        else:
                            self.canv.rect(bg_x, bg_y, bg_w, bg_h, fill=1, stroke=0)
                        
                        # Draw borders
                        if self.border_color and self.border_width > 0:
                            self.canv.setStrokeColor(self.border_color)
                            self.canv.setLineWidth(self.border_width)
                            
                            if self.border_style_type == 'left':
                                # Left border only (for cards)
                                self.canv.line(bg_x, bg_y, bg_x, bg_y + bg_h)
                            elif self.border_style_type == 'bottom':
                                # Bottom border (for hero)
                                self.canv.line(bg_x, bg_y, bg_x + bg_w, bg_y)
                            else:
                                # Full border
                                if self.border_radius > 0:
                                    self.canv.roundRect(bg_x, bg_y, bg_w, bg_h, self.border_radius, fill=0, stroke=1)
                                else:
                                    self.canv.rect(bg_x, bg_y, bg_w, bg_h, fill=0, stroke=1)
                        
                        # Note: Content is drawn separately by ReportLab
                        # This flowable only draws the background/border/shadow
                
                # Calculate available width
                available_width = 500 - (padding_val * 2)
                
                # Separate text content from images
                table_rows = []
                images_to_add = []
                
                for item in section_flowables:
                    if isinstance(item, Paragraph):
                        table_rows.append([item])
                    elif isinstance(item, Spacer):
                        table_rows.append([Paragraph(' ', normal_style)])
                    else:
                        # Images need to be added separately
                        images_to_add.append(item)
                
                # Use Table with background - simpler and more reliable
                if table_rows:
                    content_table = Table(table_rows, colWidths=[available_width])
                    table_style = TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), bg_color if bg_color else Color(0.98, 0.98, 0.98)),
                        ('LEFTPADDING', (0, 0), (-1, -1), padding_val),
                        ('RIGHTPADDING', (0, 0), (-1, -1), padding_val),
                        ('TOPPADDING', (0, 0), (-1, -1), padding_val),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), padding_val),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ])
                    
                    # Add left border for cards
                    if border_style_type == 'left' and border_color and border_width:
                        table_style.add('LINEBEFORE', (0, 0), (0, -1), border_width, border_color)
                        table_style.add('LEFTPADDING', (0, 0), (0, -1), padding_val + border_width)
                    
                    # Add bottom border for hero
                    if border_style_type == 'bottom' and border_color and border_width:
                        table_style.add('LINEBELOW', (0, 0), (-1, -1), border_width, border_color)
                    
                    content_table.setStyle(table_style)
                    story.append(content_table)
                
                # Add images
                for img in images_to_add:
                    story.append(img)
                    story.append(Spacer(1, 8))
                
                story.append(Spacer(1, 16))
            
            # Helper function to download/fetch image
            def get_image_data(image_url_or_data):
                """Get image data from URL or base64 data URI"""
                if not image_url_or_data:
                    return None
                
                try:
                    # If it's a data URI, extract the base64 data
                    if image_url_or_data.startswith('data:image'):
                        # Extract base64 part
                        header, data = image_url_or_data.split(',', 1)
                        img_data = base64.b64decode(data)
                        return BytesIO(img_data)
                    
                    # If it's a URL, download it
                    elif image_url_or_data.startswith('http'):
                        response = requests.get(image_url_or_data, timeout=10)
                        if response.status_code == 200:
                            return BytesIO(response.content)
                    
                    # If it's a local file path
                    elif os.path.exists(image_url_or_data):
                        with open(image_url_or_data, 'rb') as f:
                            return BytesIO(f.read())
                    
                except Exception as e:
                    return None
                
                return None
            
            for elem in elements:
                elem_type = elem[0] if len(elem) > 0 else None
                
                if elem_type == 'spacer':
                    story.append(Spacer(1, elem[1]))
                elif elem_type == 'image':
                    # Handle image embedding
                    image_url_or_data = elem[1]
                    img_data = get_image_data(image_url_or_data)
                    
                    if img_data:
                        try:
                            from reportlab.platypus import Image as RLImage
                            # Open and resize image if needed
                            img = Image.open(img_data)
                            # Resize if too large (max width 500 points for PDF)
                            max_width = 500
                            if img.width > max_width:
                                ratio = max_width / img.width
                                new_size = (max_width, int(img.height * ratio))
                                img = img.resize(new_size, Image.Resampling.LANCZOS)
                            
                            # Convert to RGB if needed
                            if img.mode != 'RGB':
                                img = img.convert('RGB')
                            
                            # Save to BytesIO
                            img_buffer = BytesIO()
                            img.save(img_buffer, format='JPEG', quality=85)
                            img_buffer.seek(0)
                            
                            # Add image to PDF
                            pdf_img = RLImage(img_buffer, width=max_width, height=img.height * (max_width / img.width))
                            
                            # If inside a section, add to section content
                            if current_section:
                                section_content.append(('image', pdf_img, None))
                            else:
                                story.append(pdf_img)
                                story.append(Spacer(1, 12))
                        except Exception as e:
                            # If image fails, add a placeholder text
                            if current_section:
                                section_content.append(('text', f"[Image: {str(e)[:50]}]", None))
                            else:
                                story.append(Paragraph(f"[Image: {str(e)[:50]}]", normal_style))
                                story.append(Spacer(1, 12))
                elif elem_type == 'heading':
                    # For HTML parser, elem[1] is the level
                    level = elem[1] if isinstance(elem[1], int) else (int(elem[1]) if str(elem[1]).isdigit() else 1)
                    # Store heading level for next text element
                    current_heading_level = level
                    continue
                elif elem_type == 'heading_end':
                    current_heading_level = None
                    if not current_section:
                        story.append(Spacer(1, 12))
                elif elem_type == 'section_start':
                    # If there was a previous section, render it first
                    if current_section and section_content:
                        render_styled_section(current_section[0], current_section[1], section_content)
                        section_content = []
                    
                    # Start collecting content for new styled section
                    section_type = elem[1] if len(elem) > 1 else 'normal'
                    section_style = elem[2] if len(elem) > 2 else None
                    
                    # Always start section collection (even if 'normal', might have styling)
                    current_section = (section_type, section_style)
                    section_content = []
                    continue
                elif elem_type == 'section_end':
                    # Render the collected section content
                    if current_section and section_content:
                        render_styled_section(current_section[0], current_section[1], section_content)
                        section_content = []
                    current_section = None
                    continue
                elif elem_type == 'list_item':
                    text = elem[1]
                    list_type = elem[2] if len(elem) > 2 else 'ul'
                    
                    if not text or not text.strip():
                        continue
                    
                    # Additional cleaning
                    text = clean_text_for_pdf(text)
                    if not text:
                        continue
                    
                    # Escape for reportlab XML
                    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    
                    # Add bullet
                    if list_type == 'ul':
                        text = f"• {text}"
                    
                    # If inside a section, add to section content
                    if current_section:
                        section_content.append(('text', text, None))
                        continue
                    
                    try:
                        story.append(Paragraph(text, normal_style))
                    except Exception as e:
                        # If it fails, try with UTF-8 encoding
                        try:
                            if isinstance(text, str):
                                text_clean = text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
                                if text_clean:
                                    story.append(Paragraph(text_clean, normal_style))
                        except:
                            pass
                elif elem_type == 'text':
                    text = elem[1]
                    elem_tag = elem[2] if len(elem) > 2 else None
                    
                    if not text or not text.strip():
                        continue
                    
                    # Additional cleaning
                    text = clean_text_for_pdf(text)
                    if not text:
                        continue
                    
                    # Escape for reportlab XML
                    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    
                    # If we're inside a styled section, collect content instead of rendering immediately
                    if current_section:
                        # Check if this should be a heading
                        if current_heading_level is not None:
                            level = current_heading_level
                            section_content.append(('heading', text, level))
                            current_heading_level = None
                        else:
                            section_content.append(('text', text, elem_tag))
                        continue
                    
                    # Determine style based on context
                    style = normal_style
                    
                    # Check if this text should be a heading (from HTML parser)
                    if current_heading_level is not None:
                        level = current_heading_level
                        style = title_style if level == 1 else heading_style
                        current_heading_level = None  # Reset after use
                    elif elem_tag and elem_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        # Heading tag detected
                        level = int(elem_tag[1]) if len(elem_tag) > 1 else 1
                        style = title_style if level == 1 else heading_style
                    
                    try:
                        # Ensure text is properly encoded for reportlab
                        if isinstance(text, bytes):
                            text = text.decode('utf-8', errors='ignore')
                        story.append(Paragraph(text, style))
                    except Exception as e:
                        # If it fails, try with UTF-8 encoding
                        try:
                            if isinstance(text, str):
                                text_clean = text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
                                if text_clean:
                                    story.append(Paragraph(text_clean, style))
                        except:
                            pass
                # Handle old HTML parser format for backward compatibility
                elif elem_type == 'heading_end' or elem_type == 'paragraph_end' or elem_type == 'list_end':
                    story.append(Spacer(1, 8))
                elif elem_type == 'text' and len(elem) >= 2:
                    # Old HTML parser format
                    text = elem[1]
                    if not text or not text.strip():
                        continue
                    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    try:
                        story.append(Paragraph(text, normal_style))
                    except:
                        pass
            
            # Build PDF
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                return True, "Success"
            return pdf_bytes, "Success"
        
        # Try pdfkit as last resort (only if wkhtmltopdf is available)
        if HAS_PDFKIT:
            try:
                full_html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{{font-family:{t['font']};}}</style></head><body>{html_content}</body></html>"""
                if output_path:
                    pdfkit.from_string(full_html, output_path)
                    return True, "Success"
                else:
                    pdf_bytes = pdfkit.from_string(full_html, False)
                    return pdf_bytes, "Success"
            except Exception as e:
                # pdfkit failed (probably wkhtmltopdf not available)
                return None, f"PDFKit error: {str(e)}. Using reportlab instead."
        
        return None, "PDF generation failed - no working library"
    except Exception as e:
        if ErrorHandler:
            ErrorHandler.log_error("generate_pdf", e)
            success, message = ErrorHandler.handle_export_error("PDF", e)
            return None, message
        return None, f"Error: {str(e)}"


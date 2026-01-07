"""
AI integration module for MarkPolish Studio
Handles OpenAI API calls, language detection, and AI-powered content processing
"""

import re
import requests
import streamlit as st

# Import error handler if available
try:
    from error_handler import ErrorHandler
except ImportError:
    ErrorHandler = None

# Import OpenAI if available
try:
    from openai import OpenAI
    import httpx
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# Import provider manager
try:
    from ai_provider_manager import get_manager, AIProvider
    HAS_PROVIDER_MANAGER = True
except ImportError:
    HAS_PROVIDER_MANAGER = False
    AIProvider = None


def get_provider_config(provider_id: str) -> dict:
    """
    Get provider configuration for AI calls

    Args:
        provider_id: Provider ID

    Returns:
        Dict with engine, url, key, model
    """
    if not HAS_PROVIDER_MANAGER:
        return {"engine": "None", "url": "", "key": "", "model": ""}

    manager = get_manager()
    provider = manager.get_provider(provider_id)

    if not provider:
        return {"engine": "None", "url": "", "key": "", "model": ""}

    # Get API key based on security level
    api_key = manager.get_api_key(provider_id) if provider.provider_type != "ollama" else ""

    return {
        "engine": provider.provider_type,
        "url": provider.api_host,
        "key": api_key,
        "model": provider.default_model,
        "provider_name": provider.name,
        "icon": _get_provider_icon(provider.provider_type),
    }


def _get_provider_icon(provider_type: str) -> str:
    """Get icon for provider type"""
    icons = {
        "openai": "🔵",
        "openrouter": "🟣",
        "anthropic": "🟠",
        "gemini": "🟡",
        "deepseek": "🔴",
        "ollama": "🟢",
        "custom": "⚪",
    }
    return icons.get(provider_type, "🤖")


def check_connection(engine, url, key):
    """Check connection to AI service"""
    # Normalize engine name for consistency
    engine_normalized = engine.lower().strip()
    
    if "ollama" in engine_normalized:
        try:
            session = requests.Session()
            session.trust_env = False 
            # Ollama's base URL without /v1
            clean_url = url.replace("/v1", "").rstrip("/")
            # Try both /api/tags and root endpoint
            response = session.get(f"{clean_url}/api/tags", timeout=2)
            if response.status_code == 200: 
                return True, "✅ Online (Ollama)"
            else:
                # Fallback: try root
                response = session.get(clean_url, timeout=1)
                if response.status_code == 200:
                    return True, "✅ Online (Ollama)"
                else:
                    return False, f"⚠️ Status: {response.status_code}"
        except requests.exceptions.Timeout:
            return False, "⏱️ Timeout"
        except requests.exceptions.ConnectionError:
            return False, "❌ Connection Failed"
        except Exception as e:
            return False, f"❌ Error: {str(e)[:30]}"
    elif "openrouter" in engine_normalized:
        if not key: 
            return False, "⚠️ Missing Key"
        try:
            headers = {"Authorization": f"Bearer {key}"}
            response = requests.get("https://openrouter.ai/api/v1/auth/key", headers=headers, timeout=3)
            if response.status_code == 200: 
                return True, "✅ Online (OpenRouter)"
            elif response.status_code == 401: 
                return False, "❌ Invalid Key"
            else: 
                return False, f"❌ Error {response.status_code}"
        except: 
            return False, "❌ Network Error"
    elif engine == "OpenAI":
        if not key:
            return False, "⚠️ Missing Key"
        try:
            headers = {"Authorization": f"Bearer {key}"}
            response = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=3)
            if response.status_code == 200:
                return True, "✅ Online (OpenAI)"
            elif response.status_code == 401:
                return False, "❌ Invalid Key"
            else:
                return False, f"❌ Error {response.status_code}"
        except:
            return False, "❌ Network Error"
    elif engine == "Gemini":
        if not key:
            return False, "⚠️ Missing Key"
        try:
            response = requests.get(
                "https://generativelanguage.googleapis.com/v1beta/models",
                params={"key": key},
                timeout=3,
            )
            if response.status_code == 200:
                return True, "✅ Online (Gemini)"
            elif response.status_code in (401, 403):
                return False, "❌ Invalid Key"
            else:
                return False, f"❌ Error {response.status_code}"
        except:
            return False, "❌ Network Error"
    return False, "Unknown"


def detect_language(text):
    """Detect if text is mostly Chinese or English"""
    if not text:
        return "English"
    
    # Count Chinese characters (CJK Unified Ideographs)
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    total_chars = sum(1 for char in text if char.isalnum() or '\u4e00' <= char <= '\u9fff')
    
    if total_chars == 0:
        return "English"
    
    # If more than 30% are Chinese characters, consider it Chinese
    chinese_ratio = chinese_chars / total_chars if total_chars > 0 else 0
    return "Chinese" if chinese_ratio > 0.3 else "English"


def detect_content_type(text):
    """
    Detect content type based on text patterns and structure
    
    Args:
        text: Content to analyze
        
    Returns:
        Detected content type string
    """
    if not text:
        return "Blog Post"
    
    text_lower = text.lower()
    
    # Tutorial/How-to patterns
    tutorial_patterns = [
        r'step\s*\d', r'how\s*to', r'tutorial', r'instruction',
        r'first,?\s+second', r'begin with', r'start by',
        r'\d+\.\s+\w+', r'next,?\s+then', r'finally,?\s+'
    ]
    if any(re.search(p, text_lower) for p in tutorial_patterns):
        return "Tutorial"
    
    # Timeline/History patterns
    timeline_patterns = [
        r'\d{4}', r'year\s*\d', r' history', r'chronological',
        r'originally', r'previously', r'eventually', r'over time',
        r'back in', r'decade', r'century', r'timeline'
    ]
    if any(re.search(p, text_lower) for p in timeline_patterns):
        return "Timeline"
    
    # Announcement patterns
    announcement_patterns = [
        r'announce', r'launching', r'introducing', r'new feature',
        r'coming soon', r'exciting news', r'breaking',
        r'public notice', r'official statement'
    ]
    if any(re.search(p, text_lower) for p in announcement_patterns):
        return "Announcement"
    
    # Product Launch patterns
    product_patterns = [
        r'product', r'feature', r'upgrade', r'release',
        r'now available', r'check out', r'shop now',
        r'buy now', r'limited time', r'special offer'
    ]
    if any(re.search(p, text_lower) for p in product_patterns):
        return "Product Launch"
    
    # Newsletter patterns
    newsletter_patterns = [
        r'welcome', r'subscribe', r'reader', r'weekly',
        r'monthly', r'digest', r'in this issue', r'community'
    ]
    if any(re.search(p, text_lower) for p in newsletter_patterns):
        return "Newsletter"
    
    # Marketing patterns
    marketing_patterns = [
        r'benefit', r'why you should', r'don\'t miss',
        r'limited offer', r'only \d+', r'best choice',
        r'proven', r'result', r'transform'
    ]
    if any(re.search(p, text_lower) for p in marketing_patterns):
        return "Marketing"
    
    # Default to Blog Post for general content
    return "Blog Post"


def analyze_structure(text):
    """
    Analyze the structural patterns in the content
    
    Args:
        text: Content to analyze
        
    Returns:
        Dictionary with structural analysis
    """
    lines = text.strip().split('\n')
    
    analysis = {
        'has_hero': False,
        'heading_count': 0,
        'heading_levels': [],
        'paragraph_count': 0,
        'list_items': 0,
        'has_timeline_pattern': False,
        'has_steps_pattern': False,
        'has_comparison': False,
        'total_lines': len(lines),
        'has_intro': False,
        'has_conclusion': False
    }
    
    # Analyze headings
    h1_count = 0
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith('#'):
            level = len(line_stripped) - len(line_stripped.lstrip('#'))
            analysis['heading_levels'].append(level)
            analysis['heading_count'] += 1
            if level == 1:
                h1_count += 1
                if analysis['heading_count'] == 1:
                    analysis['has_hero'] = True
        
        elif line_stripped and not line_stripped.startswith('#'):
            # Check for paragraph (non-empty line that's not a heading)
            if len(line_stripped) > 50:  # Likely a paragraph
                if analysis['heading_count'] == 0:
                    analysis['has_intro'] = True
                if analysis['heading_count'] > 0:
                    analysis['has_conclusion'] = True
            
            # Check for list items
            if re.match(r'^[\-\*\+]\s+', line_stripped) or re.match(r'^\d+[\.\)]\s+', line_stripped):
                analysis['list_items'] += 1
    
    # Detect patterns
    text_lower = text.lower()
    if any(p in text_lower for p in ['step', 'first', 'second', 'then', 'finally', 'next']):
        analysis['has_steps_pattern'] = True
    if any(p in text_lower for p in ['year', 'history', 'timeline', 'chronological', 'originally']):
        analysis['has_timeline_pattern'] = True
    if any(p in text_lower for p in ['vs\s+\w+|versus|compare|difference|instead|both']):
        analysis['has_comparison'] = True
    
    return analysis


def run_ai(text, context, config, task_type="polish", content_type=None, available_plugins=None):
    """
    Run AI task with optional plugin information
    
    Args:
        text: Content to process
        context: Context for the task
        config: AI configuration
        task_type: Type of task (polish, format, suggest_components, etc.)
        content_type: Content type for style guidance
        available_plugins: List of Plugin objects to include in suggestions
    """
    if config['engine'] == "None": 
        return text, "ℹ️ AI Off"
    if not HAS_OPENAI: 
        return text, "❌ pip install openai"
    
    key = config.get('key')
    engine = config.get('engine', '').lower()
    
    # Normalize Ollama detection
    is_ollama = "ollama" in engine
    
    if is_ollama: 
        key = "ollama"  # Ollama doesn't need API key
    
    # Build plugin component list for AI
    plugin_components_info = ""
    if available_plugins:
        plugin_list = []
        for plugin in available_plugins:
            plugin_info = f"{plugin.name}"
            if plugin.description:
                plugin_info += f" ({plugin.description})"
            plugin_list.append(plugin_info)
        if plugin_list:
            plugin_components_info = f"\n\nAlso available plugin components: {', '.join(plugin_list)}. Use plugin names exactly as listed."

    # Content type-specific prompts
    content_type_prompts = {
        "Product Launch": "Write in an exciting, announcement style. Focus on benefits and features. Use engaging language.",
        "Newsletter": "Write in a friendly, informative newsletter style. Use clear sections and engaging headlines.",
        "Tutorial": "Write in a clear, step-by-step instructional style. Be precise and easy to follow.",
        "Marketing": "Write in a persuasive, benefit-focused marketing style. Use compelling language and clear CTAs.",
        "Internal": "Write in a professional, clear internal communication style. Be concise and actionable.",
        "Blog Post": "Write in an engaging, conversational blog style. Use storytelling and personal insights.",
        "Announcement": "Write in a clear, professional announcement style. Highlight key information upfront.",
        "Timeline": "Write in a chronological, historical narrative style. Use dates and time markers effectively.",
    }
    
    # Auto-detect content type if not provided
    detected_content_type = content_type if content_type else detect_content_type(text)
    content_style = content_type_prompts.get(detected_content_type, "") if detected_content_type else ""
    style_instruction = f"\n5. Writing Style: {content_style}" if content_style else ""

    # Detect language for titles
    detected_language = detect_language(text) if task_type == "titles" else None
    language_instruction = ""
    if detected_language == "Chinese":
        language_instruction = " IMPORTANT: Generate titles in Chinese (中文). Match the language of the content."
    else:
        language_instruction = " IMPORTANT: Generate titles in English. Match the language of the content."

    # Build system prompts based on task type
    if task_type == "titles":
        sys_msg = (
            "You are a Viral Marketing Expert. "
            "Generate 5 catchy, punchy titles based on the content."
            f"{language_instruction} "
            "CRITICAL FORMATTING INSTRUCTION: Output them as a generic Markdown Numbered List (1. Title / 2. Title). "
            "Ensure there is a newline between every title. "
            "Do not write long paragraphs. Keep titles under 20 words each."
            "Return ONLY the list."
        )
        user_content = f"CONTENT:\n{text}"
    elif task_type == "expand":
        sys_msg = (
            "You are a Content Expansion Expert. "
            "Expand the provided content by adding more detail, examples, and context. "
            "1. Keep the original structure and formatting. "
            "2. Add supporting details and explanations. "
            "3. Expand bullet points into full paragraphs where appropriate. "
            "4. Maintain the same tone and style. "
            "5. CRITICAL: Protect [IMG] and ::: tags exactly as they are."
            f"{style_instruction}"
        )
        user_content = f"CONTENT TO EXPAND:\n{text}\n\nCONTEXT (if helpful):\n{context}"
    elif task_type == "format":
        # Analyze structure first
        structure_analysis = analyze_structure(text)
        
        # Build intelligent component suggestions based on analysis
        component_suggestions = []
        
        # Hero suggestion
        if not structure_analysis['has_hero']:
            component_suggestions.append("::: hero - Use at the beginning for main title and subtitle")
        
        # Timeline suggestion for chronological content
        if structure_analysis['has_timeline_pattern']:
            component_suggestions.append("::: timeline - Use for chronological events or history")
        
        # Steps suggestion for tutorial/how-to content
        if structure_analysis['has_steps_pattern'] or detected_content_type == "Tutorial":
            component_suggestions.append("::: steps - Use for step-by-step instructions")
        
        # Col-2 for comparisons
        if structure_analysis['has_comparison']:
            component_suggestions.append("::: col-2 - Use for side-by-side comparison")
        
        # Card for key points or summaries
        if structure_analysis['list_items'] >= 3:
            component_suggestions.append("::: card - Use for highlighting key points or summaries")
        
        # Col-3 for three-way comparisons or triads
        if structure_analysis['list_items'] >= 6:
            component_suggestions.append("::: col-3 - Use for three-column layouts")
        
        # Build component list for format task
        format_components_note = "markdown components (::: hero, ::: col-2, ::: col-3, ::: steps, ::: timeline, ::: card, etc.)"
        if plugin_components_info:
            format_components_note += f" including available plugin components{plugin_components_info.replace('Also available plugin components:', '')}"
        
        # Create comprehensive structure analysis note
        analysis_note = (
            f"\n\nSTRUCTURE ANALYSIS:\n"
            f"- Current headings: {structure_analysis['heading_count']}\n"
            f"- Heading levels: {structure_analysis['heading_levels']}\n"
            f"- List items: {structure_analysis['list_items']}\n"
            f"- Has chronological pattern: {structure_analysis['has_timeline_pattern']}\n"
            f"- Has step-by-step pattern: {structure_analysis['has_steps_pattern']}\n"
            f"- Has comparison pattern: {structure_analysis['has_comparison']}\n"
            f"- Detected content type: {detected_content_type}\n"
        )
        
        sys_msg = (
            "You are an Expert Content Architect. Your task is to intelligently restructure and format content "
            "to maximize readability, visual appeal, and logical flow. Think of yourself as a professional "
            "editor who transforms raw content into beautifully structured documents.\n\n"
            
            "CRITICAL FORMATTING RULES (follow in order of priority):\n\n"
            
            "1. HEADING HIERARCHY (Most Important):\n"
            "- Ensure ONE H1 (#) at the very beginning - this is the main title\n"
            "- Use H2 (##) for major sections under the main title\n"
            "- Use H3 (###) for subsections under H2\n"
            "- NEVER skip heading levels (no H1 → H3)\n"
            "- Ensure headings form a logical, nested structure\n\n"
            
            "2. COMPONENT PLACEMENT:\n"
            "- Place hero component at the VERY BEGINNING if there's a main title\n"
            "- Place timeline component for chronological/historical content\n"
            "- Place steps component for how-to/tutorial content\n"
            "- Place col-2 for side-by-side comparisons or two related items\n"
            "- Place col-3 for three-column layouts\n"
            "- Place card components to highlight key takeaways, summaries, or important notes\n"
            "- Place components where they naturally fit the content flow\n"
            f"SUGGESTED COMPONENTS FOR THIS CONTENT:\n{chr(10).join(component_suggestions) if component_suggestions else '- No specific components suggested based on analysis'}\n\n"
            
            "3. CONTENT PRESERVATION (Strict Rules):\n"
            "- KEEP all original content, wording, and meaning\n"
            "- NEVER add boilerplate, placeholders, or promotional text\n"
            "- NEVER duplicate or repeat content\n"
            "- Only restructure, don't rewrite\n\n"
            
            "4. FLOW AND READABILITY:\n"
            "- Add appropriate whitespace (blank lines) between sections\n"
            "- Use bullet points or numbered lists for sequential items (3+ items)\n"
            "- Group related information together\n"
            "- Ensure logical progression from intro → body → conclusion\n\n"
            
            "5. TAG PROTECTION:\n"
            "- CRITICAL: Protect existing [IMG] and ::: tags exactly as they are\n"
            "- Do not wrap, modify, or alter these special tags\n"
            "- If adding new components, use the exact syntax: ::: component-name\n"
            f"{plugin_components_info}\n"
            
            f"OUTPUT:\n"
            "Return ONLY the formatted content. Do not include explanations or notes about changes.\n"
            "Ensure the output is valid Markdown with proper structure.\n"
            f"{style_instruction}"
        )
        user_content = f"CONTENT TO FORMAT:\n{text}{analysis_note}"
    elif task_type == "suggest_components":
        detected_lang = detect_language(text)
        lang_note = "用中文回答" if detected_lang == "Chinese" else "Answer in English"
        
        # Build component list
        builtin_components = "hero, col-2, col-3, steps, timeline, card"
        components_list = builtin_components
        if available_plugins:
            # Extract plugin names
            plugin_names = [p.name for p in available_plugins]
            if plugin_names:
                components_list += ", " + ", ".join(plugin_names)
        
        sys_msg = (
            "You are a Content Structure Expert. "
            "Analyze the content and suggest which markdown components would enhance it. "
            f"Available components: {components_list}. "
            f"{plugin_components_info}"
            "Return ONLY a JSON array with format: "
            '[{"component": "hero", "position": "beginning"}, {"component": "col-2", "position": "after paragraph 2"}]'
            "Position can be: 'beginning', 'end', 'after paragraph X', 'before heading X', or 'middle'. "
            "Return ONLY valid JSON, no other text."
        )
        user_content = f"CONTENT:\n{text}"
    else:
        # Default polish task with context
        sys_msg = (
            "You are a professional Markdown Editor. "
            "Your task is to polish and improve the content while STRICTLY preserving the original structure. "
            "RULES (follow in order):\n"
            "1. Do NOT change, move, add, or remove any headings (#, ##, ###)\n"
            "2. Do NOT change the order of paragraphs\n"
            "3. Do NOT add or remove line breaks\n"
            "4. Do NOT modify [IMG] tags or ::: component tags\n"
            "5. Only improve: grammar, wording, flow, and clarity within each existing paragraph\n"
            "6. Keep the same tone and style as the original\n"
            "7. If context is provided, incorporate it naturally without changing structure\n"
            "8. Output ONLY the polished content, nothing else"
        )
        user_content = f"CONTEXT:\n{context}\n\nCONTENT TO POLISH:\n{text}"
    
    try:
        # Use Ollama-compatible client for local Ollama instances
        client = httpx.Client(trust_env=False, timeout=60.0) if is_ollama else httpx.Client(timeout=30.0)
        ai = OpenAI(base_url=config['url'], api_key=key, http_client=client)
        res = ai.chat.completions.create(
            model=config['model'], 
            messages=[
                {"role":"system","content":sys_msg},
                {"role":"user","content":user_content}
            ]
        )
        return res.choices[0].message.content, "✅ Success"
    except Exception as e:
        if ErrorHandler:
            ErrorHandler.log_error("run_ai", e, {"engine": config.get('engine'), "model": config.get('model')})
            success, message = ErrorHandler.handle_ai_error(config.get('engine', 'Unknown'), e)
            return text, message
        return text, f"⚠️ Error: {str(e)}"


def insert_component_at_position(content, component_template, position):
    """Insert a component at the specified position in the content"""
    lines = content.split('\n')
    
    if position == "beginning":
        return component_template + "\n\n" + content
    elif position == "end":
        return content + "\n\n" + component_template
    elif position == "middle":
        # Insert in the middle
        mid_point = len(lines) // 2
        return '\n'.join(lines[:mid_point]) + "\n\n" + component_template + "\n\n" + '\n'.join(lines[mid_point:])
    elif position.startswith("after paragraph"):
        # Extract paragraph number
        try:
            para_num = int(re.search(r'\d+', position).group())
            para_count = 0
            insert_idx = 0
            
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith('#'):
                    para_count += 1
                    if para_count == para_num:
                        insert_idx = i + 1
                        break
            
            if insert_idx > 0:
                return '\n'.join(lines[:insert_idx]) + "\n\n" + component_template + "\n\n" + '\n'.join(lines[insert_idx:])
        except:
            pass
    elif position.startswith("before heading"):
        # Extract heading number or text
        heading_match = re.search(r'heading\s+(\d+|.+)', position, re.IGNORECASE)
        if heading_match:
            heading_ref = heading_match.group(1)
            for i, line in enumerate(lines):
                if line.strip().startswith('#'):
                    if heading_ref.isdigit():
                        # Match by heading level
                        level = len(line) - len(line.lstrip('#'))
                        if level == int(heading_ref):
                            return '\n'.join(lines[:i]) + "\n\n" + component_template + "\n\n" + '\n'.join(lines[i:])
                    else:
                        # Match by heading text
                        heading_text = line.lstrip('#').strip()
                        if heading_ref.lower() in heading_text.lower():
                            return '\n'.join(lines[:i]) + "\n\n" + component_template + "\n\n" + '\n'.join(lines[i:])
    
    # Default: insert at end
    return content + "\n\n" + component_template


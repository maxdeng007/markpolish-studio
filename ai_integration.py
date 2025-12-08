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


def check_connection(engine, url, key):
    """Check connection to AI service"""
    if engine == "Ollama (Local)":
        try:
            session = requests.Session()
            session.trust_env = False 
            clean_url = url.replace("/v1", "")
            response = session.get(clean_url, timeout=0.5)
            if response.status_code == 200: 
                return True, "✅ Online (Ollama)"
            else: 
                return False, f"⚠️ Status: {response.status_code}"
        except: 
            return False, "❌ Offline"
    elif engine == "OpenRouter":
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
    if config['engine'] == "Ollama (Local)": 
        key = "ollama"
    
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
    }
    
    content_style = content_type_prompts.get(content_type, "") if content_type else ""
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
        # Build component list for format task
        format_components_note = "markdown components (::: hero, ::: col-2, ::: card, etc.)"
        if plugin_components_info:
            format_components_note += f" including available plugin components{plugin_components_info.replace('Also available plugin components:', '')}"
        
        sys_msg = (
            "You are a Markdown Formatting Assistant. "
            "Improve the structure and formatting of the content. "
            "1. Suggest better use of headings, lists, and components. "
            "2. Improve readability and flow. "
            f"3. Add appropriate {format_components_note} where they would enhance the content. "
            "4. Keep the original content and meaning. "
            "5. CRITICAL: Protect existing [IMG] and ::: tags."
            f"{style_instruction}"
        )
        user_content = f"CONTENT:\n{text}"
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
        # Default polish task
        sys_msg = (
            "You are a specialized Markdown Formatting Engine. "
            "1. If Context provided, use it to rewrite/improve the Input. "
            "2. If Context is empty, just polish the Input. "
            "3. Output polished markdown only. "
            "4. CRITICAL: Protect [IMG] and ::: tags."
            f"{style_instruction}"
        )
        user_content = f"CONTEXT:\n{context}\n\nINPUT:\n{text}"
    
    try:
        client = httpx.Client(trust_env=False) if config['engine']=="Ollama (Local)" else httpx.Client()
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


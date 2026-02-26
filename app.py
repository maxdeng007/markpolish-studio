import streamlit as st
import markdown
import re
import urllib.parse
import time
import os
from datetime import datetime

# Load .env for local dev (DASHSCOPE_API_KEY, MODELSCOPE_API_KEY etc.)
def _load_env():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    env_paths = [
        os.path.join(app_dir, ".env"),  # project root (same dir as app.py)
        ".env",                          # current working directory
        os.path.join(os.getcwd(), ".env"),
    ]
    try:
        from dotenv import load_dotenv
        for path in env_paths:
            if path and os.path.isfile(path):
                load_dotenv(path, override=True)  # override so .env wins over empty env
                break
        # Also load from app_dir again with override so project .env always wins
        project_env = os.path.join(app_dir, ".env")
        if os.path.isfile(project_env):
            load_dotenv(project_env, override=True)
    except ImportError:
        pass
    # Fallback: manually read .env if key still missing (handles encoding/quirks)
    want_keys = {"MODELSCOPE_API_KEY", "MODELSCOPE_SDK_TOKEN", "DASHSCOPE_API_KEY"}
    env_canonical = {"modelscope_api_key": "MODELSCOPE_API_KEY", "modelscope_sdk_token": "MODELSCOPE_SDK_TOKEN", "dashscope_api_key": "DASHSCOPE_API_KEY"}
    for path in [os.path.join(app_dir, ".env"), os.path.join(os.getcwd(), ".env"), ".env"]:
        if not path or not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, _, v = line.partition("=")
                        k, v = k.strip(), v.strip().strip('"').strip("'")
                        if not v:
                            continue
                        canon = env_canonical.get(k.lower()) or (k if k in want_keys else None)
                        if canon and not os.environ.get(canon):
                            os.environ[canon] = v
        except Exception:
            pass
        break

_load_env()

# --- UI TRANSLATIONS ---
TRANSLATIONS = {
    "en": {
        "app_title": "MarkPolish V1.0",
        "app_subtitle": "Content Ops Edition",
        "simple_mode": "Simple Mode",
        "dark_mode": "Dark Mode",
        "language": "Language",
        "ai_assistant": "AI Assistant",
        "files_templates": "Files & Templates",
        "add_components": "Add Components",
        "appearance": "Appearance",
        "plugins": "Plugins",
        "preview_mode": "Preview Mode",
        "editor": "Editor",
        "preview": "Preview",
        "mobile": "Mobile",
        "pc": "PC",
        "words": "words",
        "chars": "chars",
        "min_read": "min read",
        "saved": "Saved",
        "saving": "Saving...",
        "save_error": "Save error",
        "quick_save": "Quick Save",
        "undo": "Undo",
        "redo": "Redo",
        "export": "Export",
        "copy_wechat": "Copy for WeChat",
        "standard_html": "Standard HTML",
        "download": "Download",
        "theme": "Theme",
        "image_source": "Image Source",
        "files": "Files",
        "templates": "Templates",
        "no_content": "No content to preview. Start typing in the editor!",
        "layout": "Layout",
        "content": "Content",
        "interactive": "Interactive",
        "media": "Media",
        "comp_hero": "Hero",
        "comp_2col": "2-Col",
        "comp_3col": "3-Col",
        "comp_steps": "Steps",
        "comp_timeline": "Timeline",
        "comp_table": "Table",
        "comp_card": "Card",
        "comp_center": "Center",
        "comp_reveal": "Reveal",
        "comp_badge": "Badge",
        "comp_button": "Button",
        "comp_image": "AI Image",
        "comp_video": "Video",
        "files": "Files",
        "templates": "Templates",
        "save": "Save",
        "load": "Load",
        "delete": "Delete",
        "version_history": "Version History",
        "category": "Category",
        "all_templates": "All Templates",
        "use_template": "Use Template",
        "preview": "Preview",
        "search_templates": "Search templates",
        "no_files": "No files yet",
        "file_name": "File Name",
        "click_to_insert": "Click to insert components",
        "wechat_only_switch": "Only for WeChat/WeCom",
        "markdown_help": "Markdown Syntax Help",
        "image_assets": "Image & Assets",
        "upload_image": "Upload Image",
        "image_library": "Image Library",
        "no_images": "No images yet",
        "insert_image": "Insert",
        "preview_mode": "Preview Mode",
        "mobile_preview": "Mobile",
        "pc_preview": "PC",
        "reload_plugins": "Reload",
        "create_plugin": "Create Plugin",
        "installed_plugins": "Installed Plugins",
        "no_plugins": "No plugins installed",
        "no_files_search": "No files match your search.",
        "no_files_yet": "No saved files yet. Create a new file or use a template to get started.",
        "no_templates_match": "No templates match your search.",
        "click_to_insert_hint": "Click any button to insert. Use the switch to show only WeChat/WeCom-compatible components.",
        "view_full_guide": "View Full Guide",
        "syntax_tip": "Tip: Click any syntax example above to copy it to your clipboard!",
        "add_context": "Add reference material to help AI",
        "detected": "Detected",
        "content_type": "Content type",
        "modified": "Modified",
        "version": "Version",
        "size": "Size",
        "bytes": "bytes",
        "templates_available": "templates available",
        "search_files": "Search files",
        "select_file": "Select File",
        "select_template": "Select Template",
        "save_current": "Save Current Content",
        "connect": "Connect",
        "content_type_label": "Content Type",
        "context_optional": "Context (Optional)",
        "plugins_active": "Plugin(s) Active",
        "guide": "Guide",
        "no_images_library": "No images in library. Upload images to add them here.",
        "drag_drop": "Drag and drop file here",
        "browse_files": "Browse files",
        "syntax_inserted": "This syntax is inserted automatically when you click the plugin button above",
        "ai_engine": "AI Engine",
        "api_key": "API Key",
        "model": "Model",
        "paste_notes": "Paste notes here:",
        "file_name_placeholder": "Enter file name (without .md)",
        "save_button": "💾 Save",
        "choose_theme_help": "Choose a color theme for your content",
        "plugin_components_hint": "💡 Plugin components appear in 'Add Components' section above - just click to use!",
        "reload_plugins_help": "Reload plugins after creating new ones",
        "view_plugin_guide_help": "View plugin creation guide",
        "image_source_help": "Default source for [IMG: prompt] tags. ModelScope (魔搭) needs MODELSCOPE_API_KEY; Z-Image-Turbo needs DASHSCOPE_API_KEY (Secrets or .env).",
        "image_ratio": "Image ratio",
        "image_ratio_help": "Aspect ratio for AI images (Z-Image-Turbo / ModelScope) and for Picsum / Placeholder.",
        "ai_image_quota": "Daily: {remaining}/{limit} left",
        "ai_image_limit_switched": "Daily limit reached for {provider}. Switched to {fallback}.",
        "file_upload_limit": "Limit 200MB per file • PNG, JPG, JPEG, GIF",
        "preview_cached": "💡 Preview cached for performance ⚡ (cached)",
        "images_in_library": "{count} image(s) in library",
        "image_uploaded": "✅ Image uploaded!",
        "image_saved_to_library": "Image saved to library. You can reuse it from the Image Library above.",
        "preview_mode_help": "Mobile: WeChat/WeCom style | PC: Standard web style",
        "view_language": "View & language",
        "tab_visual": "Visual",
        "tab_wechat_code": "WeChat Code",
        "tab_standard_html": "Standard HTML",
        "choose_image_file": "Choose image file",
        "save_to_image_library": "Save to Image Library",
        "ai_engine_help": "Choose AI engine. 'None' disables AI features.",
        "plugin_component": "Plugin component",
        "ai_actions": "AI Actions",
        "generate_titles": "💡 Generate Titles",
        "expand_content": "📈 Expand Content",
        "smart_format": "✨ Smart Format",
        "suggest_components": "💡 Suggest Components",
        "polish_with_context": "🧠 Polish with Context",
        "polish_with_context_help": "Use AI to polish your content with context",
        "please_set_ai_engine": "Please set AI Engine at first.",
        "brainstorming_titles": "Brainstorming titles...",
        "detected_language": "Detected language: {lang} - Titles generated in {lang}",
        "expanding_content": "Expanding content...",
        "formatting_content": "Formatting content...",
        "analyzing_structure": "Analyzing structure...",
        "ai_processing": "AI Processing",
        "ai_working": "AI is working...",
        "ai_status_idle": "AI is idle.",
        "ai_status_last_action": "Last AI action: {action}",
        "ai_status_failed": "Last AI action failed.",
        "ai_status_success": "Last AI action completed.",
        "ai_retry": "🔁 Retry last AI action",
        "ai_input_too_long": "Content is too long for AI. Please shorten it.",
        "help_generate_titles": "Generate titles from your current content.",
        "help_expand_content": "Expand the current content with more detail.",
        "help_smart_format": "Auto-format and tidy your content.",
        "help_suggest_components": "Get layout/component suggestions from your content.",
        "help_polish_with_context": "Polish content using the optional context notes.",
        "polishing_content": "Polishing with context...",
        "ai_action_in_progress": "Another AI action is running.",
        "ai_action_debounced": "Please wait a moment before starting another AI action.",
        "ai_input_required": "Please add text before using this action.",
        "ai_action_failed": "AI request failed. Please retry.",
        "quick_toolbar": "Quick Access",
        "format_bold": "Bold",
        "format_italic": "Italic",
        "format_link": "Link",
        "format_code": "Code",
        "insert_hero": "Hero",
        "insert_card": "Card",
        "insert_2col": "2 Columns",
        "insert_3col": "3 Columns",
        "found_suggestions": "💡 Found {count} component suggestion(s)",
        "no_suggestions": "No component suggestions found.",
        "suggested_components": "💡 Suggested Components",
        "insert_component": "Insert component",
        "component_inserted": "✅ {name} inserted at {position}!",
        "clear_suggestions": "🗑️ Clear Suggestions",
        "configure_ai_engine": "⚠️ Please configure AI Engine in sidebar first.",
        "undo_help": "Undo last change",
        "redo_help": "Redo last undone change",
        "load_button": "📂 Load",
        "delete_button": "🗑️ Delete",
        "history_button": "📜 History",
        "file_info": "📊 {size} bytes • Modified: {date}",
        "copy_wechat_html": "📋 Copy WeChat HTML",
        "export_pdf": "📄 Export PDF",
        "export_word": "📝 Export Word",
        "download_html": "📥 Download HTML",
        "copy_html_code": "📋 Copy HTML code",
        "download_pdf": "📥 Download PDF",
        "download_word": "📥 Download Word",
        "force_save": "💾 Force Save Now",
        "force_save_help": "Autosave runs automatically; use Force Save for manual backup.",
        # New AI Provider UI translations
        "provider": "Provider",
        "api_host": "API Host",
        "fetch_models": "Fetch Models",
        "models_available": "{count} models available",
        "fetching": "Fetching...",
        "test_connection": "Test",
        # Toast messages
        "toast_saved": "Saved!",
        "toast_no_content_to_save": "No content to save",
        "toast_enter_file_name": "Please enter a file name",
        "toast_version_restored": "Version restored!",
        "toast_restore_failed": "Failed to restore version",
        "toast_version_history_cleared": "Version history cleared",
        "toast_no_version_history": "No version history available for this file.",
        "toast_components_unavailable": "Components not available",
        "toast_reloaded": "Reloaded!",
        "toast_plugin_error": "Plugin error: {error}",
        "toast_pollinations_online": "Pollinations AI is back online! Try generating images.",
        "toast_pollinations_upgrade": "Pollinations AI is still showing upgrade message.",
        "toast_pollinations_not_responding": "Pollinations AI is not responding.",
        "toast_pollinations_down": "Cannot connect to Pollinations AI. Service may be down.",
        "toast_online": "Online",
        "toast_checking": "Checking... (Click button to test)",
        "toast_expand_applied": "{msg} - Expanded content applied to editor!",
        "toast_format_applied": "{msg}",
        "toast_large_preview": "Preview is large (~{size_kb} KB). Click to render on demand.",
        "toast_template_loaded": "Loaded template: {label}",
        "toast_word_generated": "Word document generated!",
        "toast_word_install_hint": "Word: `pip install python-docx`",
        "toast_pdf_install_hint": "PDF: `pip install reportlab`",
        "toast_pdf_failed": "PDF failed: {status} / 请重试",
        "toast_word_failed": "Word failed: {status} / 请重试",
        "toast_no_plugins": "🚀 No plugins yet",
        "toast_file_loaded": "✅ Loaded {file_name}",
        "toast_file_deleted": "✅ Deleted {file_name}",
        "toast_delete_failed": "Failed to delete: {error}",
        "toast_template_not_found": "Template '{template}' not found. Available: {count} templates",
        "toast_deleted": "Deleted",
        "toast_auto_saved": "Auto-saved!",
        "toast_pdf_generated": "PDF generated! Click download to save.",
        "toast_copied": "✅ Copied!",
        "toast_copy_failed": "Copy failed. Press Ctrl/Cmd + C.",
    },
    "zh": {
        "app_title": "MarkPolish V1.0",
        "app_subtitle": "内容运营版",
        "simple_mode": "简洁模式",
        "dark_mode": "深色模式",
        "language": "语言",
        "ai_assistant": "AI 助手",
        "files_templates": "文件与模板",
        "add_components": "添加组件",
        "appearance": "外观设置",
        "plugins": "插件",
        "preview_mode": "预览模式",
        "editor": "编辑器",
        "preview": "预览",
        "mobile": "手机",
        "pc": "电脑",
        "words": "字",
        "chars": "字符",
        "min_read": "分钟阅读",
        "saved": "已保存",
        "saving": "保存中...",
        "save_error": "保存失败",
        "quick_save": "快速保存",
        "undo": "撤销",
        "redo": "重做",
        "export": "导出",
        "copy_wechat": "复制到微信",
        "standard_html": "标准 HTML",
        "download": "下载",
        "theme": "主题",
        "image_source": "图片来源",
        "files": "文件",
        "templates": "模板",
        "no_content": "暂无内容，请在编辑器中输入！",
        "layout": "布局",
        "content": "内容",
        "interactive": "交互",
        "media": "媒体",
        "comp_hero": "封面",
        "comp_2col": "两列",
        "comp_3col": "三列",
        "comp_steps": "步骤",
        "comp_timeline": "时间线",
        "comp_table": "表格",
        "comp_card": "卡片",
        "comp_center": "居中",
        "comp_reveal": "揭示",
        "comp_badge": "标签",
        "comp_button": "按钮",
        "comp_image": "AI 图片",
        "comp_video": "视频",
        "files": "文件",
        "templates": "模板",
        "save": "保存",
        "load": "加载",
        "delete": "删除",
        "version_history": "版本历史",
        "category": "分类",
        "all_templates": "全部模板",
        "use_template": "使用模板",
        "preview": "预览",
        "search_templates": "搜索模板...",
        "no_files": "暂无文件",
        "file_name": "文件名",
        "click_to_insert": "点击插入组件",
        "wechat_only_switch": "仅限微信/企微",
        "markdown_help": "Markdown 语法帮助",
        "image_assets": "图片与资源",
        "upload_image": "上传图片",
        "image_library": "图片库",
        "no_images": "暂无图片",
        "insert_image": "插入",
        "preview_mode": "预览模式",
        "mobile_preview": "手机",
        "pc_preview": "电脑",
        "reload_plugins": "刷新",
        "create_plugin": "创建插件",
        "installed_plugins": "已安装插件",
        "no_plugins": "暂无插件",
        "no_files_search": "没有匹配的文件",
        "no_files_yet": "暂无保存的文件。创建新文件或使用模板开始吧！",
        "no_templates_match": "没有匹配的模板",
        "click_to_insert_hint": "点击按钮插入组件。开启「仅限微信/企微」开关可只显示兼容组件。",
        "view_full_guide": "查看完整指南",
        "syntax_tip": "提示：点击上方的语法示例可复制到剪贴板！",
        "add_context": "添加参考资料帮助 AI",
        "detected": "检测到",
        "content_type": "内容类型",
        "modified": "修改于",
        "version": "版本",
        "size": "大小",
        "bytes": "字节",
        "templates_available": "个模板可用",
        "search_files": "搜索文件",
        "select_file": "选择文件",
        "select_template": "选择模板",
        "save_current": "保存当前内容",
        "connect": "连接",
        "content_type_label": "内容类型",
        "context_optional": "上下文（可选）",
        "plugins_active": "个插件已激活",
        "guide": "指南",
        "no_images_library": "图片库为空，上传图片后将显示在此处。",
        "drag_drop": "拖放文件到这里",
        "browse_files": "浏览文件",
        "syntax_inserted": "点击上方插件按钮时，此语法将自动插入",
        "ai_engine": "AI 引擎",
        "api_key": "API 密钥",
        "model": "模型",
        "paste_notes": "在此粘贴笔记：",
        "file_name_placeholder": "输入文件名（不含 .md）",
        "save_button": "💾 保存",
        "choose_theme_help": "为内容选择颜色主题",
        "plugin_components_hint": "💡 插件组件出现在上方的「添加组件」部分 - 只需点击即可使用！",
        "reload_plugins_help": "创建新插件后重新加载",
        "view_plugin_guide_help": "查看插件创建指南",
        "image_source_help": "[IMG: prompt] 标签的默认来源。ModelScope（魔搭）需配置 MODELSCOPE_API_KEY；Z-Image-Turbo 需配置 DASHSCOPE_API_KEY（Secrets 或 .env）。",
        "image_ratio": "图片比例",
        "image_ratio_help": "AI 图片及 Picsum / Placeholder 的宽高比。",
        "ai_image_quota": "今日剩余：{remaining}/{limit}",
        "ai_image_limit_switched": "今日 {provider} 已达上限，已切换为 {fallback}。",
        "file_upload_limit": "每个文件限制 200MB • PNG, JPG, JPEG, GIF",
        "preview_cached": "💡 预览已缓存以提升性能 ⚡（已缓存）",
        "images_in_library": "{count} 张图片在图库",
        "image_uploaded": "✅ 图片已上传！",
        "image_saved_to_library": "图片已保存到图库。可以在上方的图片库复用。",
        "preview_mode_help": "手机：微信/企业微信风格 | 电脑：标准网页风格",
        "view_language": "视图与语言",
        "tab_visual": "可视化",
        "tab_wechat_code": "微信代码",
        "tab_standard_html": "标准 HTML",
        "choose_image_file": "选择图片文件",
        "save_to_image_library": "保存到图片库",
        "ai_engine_help": "选择 AI 引擎。「无」将禁用 AI 功能。",
        "plugin_component": "插件组件",
        "ai_actions": "AI 操作",
        "generate_titles": "💡 生成标题",
        "expand_content": "📈 扩展内容",
        "smart_format": "✨ 智能格式化",
        "suggest_components": "💡 建议组件",
        "polish_with_context": "🧠 上下文润色",
        "polish_with_context_help": "使用 AI 根据上下文润色您的内容",
        "please_set_ai_engine": "请先设置 AI 引擎。",
        "brainstorming_titles": "正在生成标题...",
        "detected_language": "检测到语言：{lang} - 标题以 {lang} 生成",
        "expanding_content": "正在扩展内容...",
        "formatting_content": "正在格式化内容...",
        "analyzing_structure": "正在分析结构...",
        "ai_processing": "AI 处理中",
        "ai_working": "AI 正在处理...",
        "ai_status_idle": "AI 空闲中。",
        "ai_status_last_action": "上次 AI 操作：{action}",
        "ai_status_failed": "上次 AI 操作失败。",
        "ai_status_success": "上次 AI 操作已完成。",
        "ai_retry": "🔁 重试上一次 AI 操作",
        "ai_input_too_long": "内容过长，无法调用 AI，请先精简。",
        "help_generate_titles": "根据当前内容生成标题。",
        "help_expand_content": "为当前内容补充细节和篇幅。",
        "help_smart_format": "自动格式化并整理内容。",
        "help_suggest_components": "根据内容给出布局/组件建议。",
        "help_polish_with_context": "结合可选上下文对内容进行润色。",
        "polishing_content": "正在结合上下文润色内容...",
        "ai_action_in_progress": "另一项 AI 操作正在运行。",
        "ai_action_debounced": "请稍等片刻再开始新的 AI 操作。",
        "ai_input_required": "请先输入内容再使用此操作。",
        "ai_action_failed": "AI 请求失败，请重试。",
        "quick_toolbar": "快速工具栏",
        "format_bold": "粗体",
        "format_italic": "斜体",
        "format_link": "链接",
        "format_code": "代码",
        "insert_hero": "英雄区",
        "insert_card": "卡片",
        "insert_2col": "2列",
        "insert_3col": "3列",
        "found_suggestions": "💡 找到 {count} 个组件建议",
        "no_suggestions": "未找到组件建议。",
        "suggested_components": "💡 建议的组件",
        "insert_component": "插入组件",
        "component_inserted": "✅ {name} 已插入到 {position}！",
        "clear_suggestions": "🗑️ 清除建议",
        "configure_ai_engine": "⚠️ 请先在侧边栏配置 AI 引擎。",
        "undo_help": "撤销上次更改",
        "redo_help": "重做上次撤销的更改",
        "load_button": "📂 加载",
        "delete_button": "🗑️ 删除",
        "history_button": "📜 历史",
        "file_info": "📊 {size} 字节 • 修改于：{date}",
        "copy_wechat_html": "📋 复制微信 HTML",
        "export_pdf": "📄 导出 PDF",
        "export_word": "📝 导出 Word",
        "download_html": "📥 下载 HTML",
        "copy_html_code": "📋 复制 HTML 代码",
        "download_pdf": "📥 下载 PDF",
        "download_word": "📥 下载 Word",
        "force_save": "💾 立即强制保存",
        "force_save_help": "已自动保存，需手动备份时可点击强制保存。",
        # New AI Provider UI translations
        "provider": "提供商",
        "api_host": "API 主机",
        "fetch_models": "获取模型",
        "models_available": "{count} 个模型可用",
        "fetching": "正在获取...",
        "test_connection": "测试",
        # Toast messages
        "toast_saved": "已保存！",
        "toast_no_content_to_save": "没有内容可保存",
        "toast_enter_file_name": "请输入文件名",
        "toast_version_restored": "版本已恢复！",
        "toast_restore_failed": "恢复版本失败",
        "toast_version_history_cleared": "版本历史已清除",
        "toast_no_version_history": "此文件没有版本历史。",
        "toast_components_unavailable": "组件不可用",
        "toast_reloaded": "已重新加载！",
        "toast_plugin_error": "插件错误：{error}",
        "toast_pollinations_online": "✅ Pollinations AI 已恢复上线！请尝试生成图片。",
        "toast_pollinations_upgrade": "⚠️ Pollinations AI 仍在显示升级消息。",
        "toast_pollinations_not_responding": "❌ Pollinations AI 无响应。",
        "toast_pollinations_down": "❌ 无法连接 Pollinations AI，服务可能已下线。",
        "toast_online": "在线",
        "toast_checking": "检查中...（点击按钮测试）",
        "toast_expand_applied": "{msg} - 扩展内容已应用到编辑器！",
        "toast_format_applied": "{msg}",
        "toast_large_preview": "预览较大（约 {size_kb} KB）。点击按需渲染。",
        "toast_template_loaded": "已加载模板：{label}",
        "toast_word_generated": "Word 文档已生成！",
        "toast_word_install_hint": "💡 Word：请运行 `pip install python-docx`",
        "toast_pdf_install_hint": "💡 PDF：请运行 `pip install reportlab`",
        "toast_pdf_failed": "PDF 失败：{status} / 请重试",
        "toast_word_failed": "Word 失败：{status} / 请重试",
        "toast_no_plugins": "🚀 暂无插件",
        "toast_file_loaded": "✅ 已加载 {file_name}",
        "toast_file_deleted": "✅ 已删除 {file_name}",
        "toast_delete_failed": "删除失败：{error}",
        "toast_template_not_found": "模板 '{template}' 未找到。可用模板：{count} 个",
        "toast_deleted": "已删除",
        "toast_auto_saved": "自动保存！",
        "toast_pdf_generated": "PDF 已生成！点击下载保存。",
        "toast_copied": "✅ 已复制！",
        "toast_copy_failed": "复制失败，请按 Ctrl/Cmd + C。",
    }
}

def get_text(key):
    """Get translated text based on current language setting"""
    lang = st.session_state.get("ui_language", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


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


# Plugin name and description translations
PLUGIN_TRANSLATIONS = {
    "en": {
        "example_callout": "Example Callout",
        "example_callout_description": "Creates a callout box with different types (info, warning, error, success)",
    },
    "zh": {
        "example_callout": "示例标注",
        "example_callout_description": "创建不同类型的标注框（信息、警告、错误、成功）",
    }
}

def get_plugin_name(plugin_name):
    """Get translated plugin name"""
    lang = st.session_state.get("ui_language", "en")
    translations = PLUGIN_TRANSLATIONS.get(lang, PLUGIN_TRANSLATIONS["en"])
    key = plugin_name.lower().replace(" ", "_")
    return translations.get(key, plugin_name.replace('_', ' ').title())

def get_plugin_description(plugin_name, description):
    """Get translated plugin description"""
    if not description:
        return description
    lang = st.session_state.get("ui_language", "en")
    translations = PLUGIN_TRANSLATIONS.get(lang, PLUGIN_TRANSLATIONS["en"])
    key = f"{plugin_name.lower().replace(' ', '_')}_description"
    return translations.get(key, description)

# --- 0. SETUP ---
# Import configuration
try:
    from config import APP_TITLE, LAYOUT, INITIAL_SIDEBAR_STATE, setup_directories, TEMPLATES, SIDEBAR_HOVER_HTML
    # Setup page config using imported values
    st.set_page_config(page_title=APP_TITLE, layout=LAYOUT, initial_sidebar_state=INITIAL_SIDEBAR_STATE)
    setup_directories()
except ImportError:
    # Fallback if config module not available
    st.set_page_config(page_title="MarkPolish V1.0", layout="wide", initial_sidebar_state="collapsed")
    if not os.path.exists("projects"):
        os.makedirs("projects")
    if not os.path.exists("projects/images"):
        os.makedirs("projects/images")
    TEMPLATES = {}
    SIDEBAR_HOVER_HTML = ""  # Fallback empty string if config not available

# Import Helpers
try:
    from themes import STYLES
    from components import apply_components, INSERTION_TOOLS, COMPONENT_COMPATIBILITY
    from error_handler import ErrorHandler
    from performance import PerformanceOptimizer
    from plugin_system import get_plugin_registry, apply_plugins
except ImportError:
    STYLES = {}
    ErrorHandler = None
    PerformanceOptimizer = None
    COMPONENT_COMPATIBILITY = {}
    get_plugin_registry = None
    apply_plugins = None

try:
    from keyboard_listener import create_keyboard_listener
    HAS_KEYBOARD_LISTENER = True
except ImportError:
    HAS_KEYBOARD_LISTENER = False

try:
    from cursor_tracker import create_cursor_tracker, get_cursor_position
    HAS_CURSOR_TRACKER = True
except ImportError:
    HAS_CURSOR_TRACKER = False
    def get_cursor_position():
        return None, None, None

# Import AI
try:
    from openai import OpenAI
    import httpx
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# Import new modules
try:
    from file_operations import (
        save_project, load_project, get_version_history, restore_version,
        get_version_storage_size, auto_save, load_auto_save, clear_auto_save,
        cleanup_old_autosave_files, push_to_undo_stack, undo_action, redo_action
    )
except ImportError:
    # Fallback if modules not available
    def save_project(name, content): return None, "Module not available"
    def load_project(filename): return None
    def get_version_history(project_name): return []
    def restore_version(project_name, version_index): return None, "Module not available"
    def get_version_storage_size(project_name): return 0
    def auto_save(content, project_name=None): return False, None
    def load_auto_save(project_name=None): return None, None
    def clear_auto_save(project_name=None): pass
    def cleanup_old_autosave_files(): pass
    def push_to_undo_stack(content, undo_stack, max_size=50): pass
    def undo_action(undo_stack, redo_stack, current_content): return None, undo_stack, redo_stack
    def redo_action(undo_stack, redo_stack, current_content): return None, undo_stack, redo_stack

try:
    from image_handling import (
        process_image, get_image_library, load_image_from_library, delete_image_from_library
    )
except ImportError:
    def process_image(file, save_to_library=True): return None, None
    def get_image_library(): return []
    def load_image_from_library(filename): return None
    def delete_image_from_library(filename): return False

try:
    from ai_integration import check_connection, run_ai, detect_language, get_provider_config
except ImportError:
    def check_connection(engine, url, key): return False, "Module not available"
    def run_ai(text, context, config, task_type="polish", content_type=None, available_plugins=None): return None, "Module not available"
    def detect_language(text): return "en"
    def get_provider_config(provider_id): return {"engine": "None", "url": "", "key": "", "model": ""}

try:
    from ai_provider_manager import get_manager, init_providers, AIProvider
    HAS_PROVIDER_MANAGER = True
except ImportError:
    HAS_PROVIDER_MANAGER = False
    def get_manager(): return None
    def init_providers(): pass
    def AIProvider(*args, **kwargs): return None

try:
    from content_processing import (
        detect_content_type, get_preview_css, get_inline_styles, deep_inject_styles,
        parse_doc, clean_for_wechat, insert_component_at_position, get_stats
    )
except ImportError:
    def detect_content_type(text): return "article"
    def get_preview_css(theme, mode="Mobile"): return ""
    def get_inline_styles(theme): 
        t = theme if isinstance(theme, dict) else {'bg': '#fff', 'text': '#000', 'font': 'Arial', 'primary': '#4A90E2'}
        return {'wrapper': f"background-color: {t.get('bg', '#fff')}; padding: 20px; min-height: 100%; box-sizing: border-box;"}
    def deep_inject_styles(html_content, styles): return html_content
    def parse_doc(text, styles, img_provider="ModelScope (AI)", img_ratio="1:1", mode="wechat"): return text  # Return text as-is if module not available
    def clean_for_wechat(html): return html
    def insert_component_at_position(content, component_template, position): return content
    def get_stats(text): return 0, 0

# Import templates from config if not already imported or empty
if 'TEMPLATES' not in globals() or not TEMPLATES:
    try:
        from config import TEMPLATES
    except ImportError:
        TEMPLATES = {
            "Empty Draft": "",
            "⚡ Quick Update": "## Quick Update\n\nBrief announcement here.\n\n[Learn More](https://example.com)",
            "📌 Simple Notice": "## Important Notice\n\nPlease note the following:\n\n- Point 1\n- Point 2\n- Point 3\n\nThank you for your attention."
        }

# --- MAIN UI ---
# All helper functions have been moved to separate modules
# See: file_operations.py, image_handling.py,
#      ai_integration.py, content_processing.py, pdf_generator.py

def main():
    # IMMEDIATELY inject JavaScript to remove help tooltips (runs before any UI renders)
    early_help_remover = """
    <script>
    // Run as early as possible - using document.startViewTransition or immediate execution
    (function() {
        var attempts = 0;
        var maxAttempts = 5000;
        var lastCount = 0;
        
        function isHelpElement(el) {
            var text = (el.textContent || '').trim();
            var className = el.className || '';
            
            // Check data-testid
            if (el.getAttribute && el.getAttribute('data-testid') === 'stHelp') return true;
            
            // Check class names
            if (typeof className === 'string') {
                if (className.includes('stHelp') || 
                    className.includes('1t7d4j1') || 
                    className.includes('e1rz36mz4')) {
                    return true;
                }
            }
            
            // Check for DeltaGenerator text patterns
            if (text.length > 30 && (
                text.includes('DeltaGenerator') || 
                text.includes('LockedCursor') ||
                text.includes('_root_container'))) {
                return true;
            }
            
            return false;
        }
        
        function removeAllHelpElements() {
            var allElements = document.querySelectorAll('*');
            var removed = 0;
            
            for (var i = 0; i < allElements.length; i++) {
                var el = allElements[i];
                if (isHelpElement(el) && el.parentNode) {
                    try { 
                        el.parentNode.removeChild(el); 
                        removed++;
                    } catch(e) {}
                }
            }
            
            return removed;
        }
        
        function continuousRemove() {
            var count = removeAllHelpElements();
            attempts++;
            
            // Continue for a long time or until we've checked many times with no changes
            if (attempts < maxAttempts) {
                if (count === 0 && attempts > 100) {
                    // Slow down after initial cleanup
                    setTimeout(continuousRemove, 100);
                } else {
                    requestAnimationFrame(continuousRemove);
                }
            }
        }
        
        // Start immediately
        continuousRemove();
        
        // Watch for any DOM changes forever
        var observer = new MutationObserver(function() { 
            removeAllHelpElements(); 
        });
        observer.observe(document.body, { childList: true, subtree: true });
    })();
    </script>
    """
    st.markdown(early_help_remover, unsafe_allow_html=True)
    
    query_params = st.query_params
    
    # Copy toast handled in-component (HTML) for reliability
    
    # Helper: enforce only one sidebar expander open (or all closed)
    def enforce_single_sidebar_open(state_dict):
        if not isinstance(state_dict, dict):
            return state_dict
        open_keys = [k for k, v in state_dict.items() if v]
        if not open_keys:
            # If nothing is open, keep all closed (do not auto-open AI Assistant on rerun)
            for k in state_dict.keys():
                state_dict[k] = False
            return state_dict
        preferred = st.session_state.get("last_sidebar_open")
        target = preferred if (preferred and preferred in open_keys) else open_keys[-1]
        for k in state_dict.keys():
            state_dict[k] = (k == target)
        st.session_state.last_sidebar_open = target
        return state_dict
    
    # Read expander state from query params (set by JavaScript)
    # This allows JavaScript to update state
    if "expander_state" in query_params:
        # Check if we've already processed this state (prevent loops)
        last_processed = st.session_state.get("last_expander_state_hash", "")
        current_hash = str(query_params.get("expander_state", ""))
        
        if current_hash != last_processed:
            try:
                import json
                state_json = query_params["expander_state"]
                js_state = json.loads(state_json)
                # Initialize if not exists
                if "sidebar_expanded" not in st.session_state:
                    st.session_state.sidebar_expanded = {}
                # Update session state with JavaScript-detected state
                for key, value in js_state.items():
                    st.session_state.sidebar_expanded[key] = value
                # Remember last open expander for next render
                js_open = [k for k, v in js_state.items() if v]
                if js_open:
                    st.session_state.last_sidebar_open = js_open[-1]
                # Mark as processed
                st.session_state.last_expander_state_hash = current_hash
            except Exception as e:
                pass  # Silently fail if JSON parsing fails
    # Read cursor position from query params (set by cursor tracker)
    # This makes cursor position available for component insertion
    if "_cursor_start" in query_params:
        try:
            st.session_state._cursor_start = int(query_params["_cursor_start"])
        except:
            pass
    if "_cursor_end" in query_params:
        try:
            st.session_state._cursor_end = int(query_params["_cursor_end"])
        except:
            pass
    
    # Initialize session state variables
    if "auto_save_enabled" not in st.session_state:
        st.session_state.auto_save_enabled = True
    if "last_auto_save_time" not in st.session_state:
        st.session_state.last_auto_save_time = 0
    if "auto_save_status" not in st.session_state:
        st.session_state.auto_save_status = "saved"
    if "undo_stack" not in st.session_state:
        st.session_state.undo_stack = []
    if "redo_stack" not in st.session_state:
        st.session_state.redo_stack = []
    if "current_project_name" not in st.session_state:
        st.session_state.current_project_name = None
    if "keyboard_action" not in st.session_state:
        st.session_state.keyboard_action = None
    if "last_content_hash" not in st.session_state:
        st.session_state.last_content_hash = None
    if "performance_optimizer" not in st.session_state and PerformanceOptimizer:
        st.session_state.performance_optimizer = PerformanceOptimizer()
    if "preview_update_pending" not in st.session_state:
        st.session_state.preview_update_pending = False
    if "last_preview_content_hash" not in st.session_state:
        st.session_state.last_preview_content_hash = None
    
    # Cleanup old auto-save files on startup
    cleanup_old_autosave_files()

    # Ensure only one sidebar section is open at a time (server-side safety)
    if "sidebar_expanded" in st.session_state:
        st.session_state.sidebar_expanded = enforce_single_sidebar_open(st.session_state.sidebar_expanded)

    # Tighten main content gutters to give editor/preview more horizontal space
    tight_layout_css = """
    <style>
    :root {
        --mp-gutter: 0.75rem;
        --mp-gutter-mobile: 0.5rem;
    }
    /* Hide empty component containers with 0 height */
    div.stElementContainer.element-container[height="0px"],
    div.stElementContainer.element-container[data-stale="false"][height="0px"],
    .stElementContainer.element-container[style*="height: 0px"],
    .stElementContainer.element-container[style*="height:0px"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }
    /* Also hide any component wrapper with 0 height */
    div[data-testid="stElementContainer"][height="0px"],
    div[data-testid="stElementContainer"][style*="height: 0px"] {
        display: none !important;
    }
    /* Set gap to 0 for main content blocks only (not sidebar) */
    section.main .st-emotion-cache-tn0cau {
        gap: 0 !important;
    }
    /* Add proper spacing for sidebar elements */
    section.tSidebar .stSelectbox {
        margin-bottom: 0.75rem !important;
    }
    section.tSidebar .stTextInput {
        margin-bottom: 0.5rem !important;
    }
    section.tSidebar .stHorizontalBlock {
        gap: 0.5rem !important;
    }
    section.tSidebar .stHorizontalBlock .stButton {
        flex: 1 !important;
    }
    /* Responsive padding for larger screens */
    @media (min-width: calc(736px + 8rem)) {
        .st-emotion-cache-zy6yx3 {
            padding-left: 3rem !important;
            padding-right: 3rem !important;
        }
    }
    /* Reduce Streamlit default side padding and prevent max-width from shrinking content */
    .stAppViewContainer .main .block-container {
        padding-left: var(--mp-gutter) !important;
        padding-right: var(--mp-gutter) !important;
        max-width: 100% !important;
    }
    /* Shrink left/right padding on vertical blocks (editor/preview wrapper) */
    section.main .stVerticalBlock[data-testid="stVerticalBlock"],
    section.main .st-emotion-cache-tn0cau {
        margin-left: 0 !important;
        margin-right: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    /* Tighten column gutters */
    div[data-testid="column"] > div {
        padding-left: 0.35rem !important;
        padding-right: 0.35rem !important;
    }
    .stHorizontalBlock {
        gap: 0.7rem !important;
    }
    /* Normalize buttons / touch targets */
    .stButton button, button[kind="secondary"] {
        padding: 0.55rem 0.7rem !important;
        min-height: 44px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] button {
        min-height: 36px;
    }
    /* Prevent button text wrapping - but allow in narrow containers */
    .stButton button {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    /* Allow text wrapping for buttons in narrow sidebar containers */
    section.tSidebar .stButton button {
        white-space: normal !important;
        text-overflow: clip !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }
    /* Ensure proper height for button containers in sidebar */
    section.tSidebar .stVerticalBlock .stButton {
        min-height: 44px;
    }
    /* CSS Changes from Browser Preview */
    /* Change 3: width from 48.0156px to fit-content for p */
    p {
        width: fit-content;
    }
    /* Change 4: width from 72.4062px to fit-content for button */
    button.st-emotion-cache-6ms01g {
        width: 100%;
    }
    /* Change 7: display from block to flex for stElementContainer (fetch_openai button) */
    div.stElementContainer.element-container.st-key-fetch_openai {
        display: flex;
    }
    /* Change 8: display from block to flex for p element containing "4 models available" */
    div.stElementContainer.element-container.st-key-fetch_openai p {
        display: flex;
    }
    /* Change 9: stVerticalBlock justify-content from start to flex-start */
    .stVerticalBlock.st-emotion-cache-wfksaw.e196pkbe2 {
        justify-content: flex-start !important;
    }
    /* Change 10: stVerticalBlock align-items from stretch to flex-start */
    .stVerticalBlock.st-emotion-cache-wfksaw.e196pkbe2 {
        align-items: flex-start !important;
    }
    /* Change 11: stColumn display from block to flex */
    .stColumn.st-emotion-cache-139jccg.e196pkbe1 {
        display: flex !important;
    }
    /* Change 12: stColumn flex-direction from row to column */
    .stColumn.st-emotion-cache-139jccg.e196pkbe1 {
        flex-direction: column !important;
    }
    /* Change 13: stColumn justify-content from normal to flex-start */
    .stColumn.st-emotion-cache-139jccg.e196pkbe1 {
        justify-content: flex-start !important;
    }
    /* Change 14: stColumn align-items from normal to flex-start */
    .stColumn.st-emotion-cache-139jccg.e196pkbe1 {
        align-items: flex-start !important;
    }
    /* Sidebar horizontal block fixes for alignment */
    section.tSidebar .stHorizontalBlock {
        align-items: center !important;
        justify-content: flex-start !important;
    }
    /* Sidebar vertical block alignment fixes */
    section.tSidebar .stVerticalBlock {
        justify-content: flex-end !important;
        align-items: flex-start !important;
    }
    
    /* Force main content columns to align top - most specific rule */
    section.main .stVerticalBlock > div[data-testid="stColumn"] {
        align-items: flex-start !important;
        justify-content: flex-start !important;
        vertical-align: top !important;
    }
    
    /* Also target the column wrappers directly */
    .stColumn {
        align-items: flex-start !important;
        justify-content: flex-start !important;
    }
    
    /* Force all column wrappers in main content to align top */
    section.main div[data-testid="stColumn"] {
        align-items: flex-start !important;
        justify-content: flex-start !important;
        vertical-align: top !important;
    }
    /* Fix button text squeezing in sidebar */
    section.tSidebar .stHorizontalBlock .stButton button {
        white-space: normal !important;
        text-overflow: clip !important;
        word-wrap: break-word !important;
        min-height: auto !important;
        height: auto !important;
        padding: 0.4rem 0.6rem !important;
    }
    /* Fix API Key section alignment */
    section.tSidebar .stTextInput {
        margin-top: 0.5rem !important;
    }
    /* Ensure proper spacing between sidebar elements */
    section.tSidebar > div {
        gap: 0.75rem !important;
    }
    /* Hide technical help tooltips (DeltaGenerator, internal docs) - MORE AGGRESSIVE */
    section.tSidebar [data-testid="stHelp"],
    section.tSidebar [data-testid="stHelpDoc"],
    section.tSidebar .stHelp,
    section.tSidebar .stTooltipIcon,
    section.tSidebar span.stHelp,
    section.tSidebar [class*="st-emotion-cache-1t7d4j1"],
    section.tSidebar [class*="st-emotion-cache-pwll7a"],
    section.tSidebar [class*="st-emotion-cache-13dqw1y"],
    section.tSidebar [class*="st-emotion-cache-e1rz36mz4"],
    section.tSidebar [class*="e1rz36mz4"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
        position: absolute !important;
        left: -9999px !important;
        top: -9999px !important;
        z-index: -9999 !important;
    }
    
    /* Force column alignment to top using JavaScript MutationObserver */
    <script>
    (function() {
        // Function to enforce column alignment
        function enforceColumnAlignment() {
            // Target all columns in the main content area
            var columns = document.querySelectorAll('section.main div[data-testid="stColumn"]');
            columns.forEach(function(col) {
                col.style.alignItems = 'flex-start';
                col.style.justifyContent = 'flex-start';
                col.style.verticalAlign = 'top';
            });
            
            // Also target stColumn class elements
            var stColumns = document.querySelectorAll('.stColumn');
            stColumns.forEach(function(col) {
                col.style.alignItems = 'flex-start';
                col.style.justifyContent = 'flex-start';
            });
        }
        
        // Run immediately
        enforceColumnAlignment();
        
        // Run continuously to catch any changes
        setInterval(enforceColumnAlignment, 100); // Every 100ms
        
        // Also use MutationObserver to catch DOM changes
        if (typeof MutationObserver !== 'undefined') {
            var observer = new MutationObserver(function(mutations) {
                enforceColumnAlignment();
            });
            
            var mainSection = document.querySelector('section.main');
            if (mainSection) {
                observer.observe(mainSection, {
                    childList: true,
                    subtree: true,
                    attributes: true,
                    attributeFilter: ['style', 'class']
                });
            }
        }
    })();
    </script>
    @media (max-width: 900px) {
        .stAppViewContainer .main .block-container {
            padding-left: var(--mp-gutter-mobile) !important;
            padding-right: var(--mp-gutter-mobile) !important;
        }
    }

    </style>
    """
    st.markdown(tight_layout_css, unsafe_allow_html=True)
    
    # Check for auto-saved content on startup
    # Only show prompt if it hasn't been dismissed in this session
    if "restore_prompt_dismissed" not in st.session_state:
        st.session_state.restore_prompt_dismissed = False
    
    if not st.session_state.get("restore_prompt_dismissed", False):
        if "content" not in st.session_state or not st.session_state.get("content"):
            autosave_content, autosave_time = load_auto_save(st.session_state.current_project_name)
            if autosave_content and autosave_content.strip():
                st.session_state.show_restore_prompt = True
                st.session_state.restore_content = autosave_content
                st.session_state.restore_time = autosave_time
        else:
            st.session_state.show_restore_prompt = False
    else:
        st.session_state.show_restore_prompt = False
    
    # Re-inject sidebar hover code on every rerun to ensure it persists
    try:
        sidebar_html = SIDEBAR_HOVER_HTML
    except NameError:
        sidebar_html = ""  # Fallback if not imported
    if sidebar_html:
        st.components.v1.html(sidebar_html, height=0)
    
    # Inject JavaScript to track sidebar expander state
    expander_tracker_html = """
    <script>
    (function() {
        // Map of expander labels to state keys
        const expanderMap = {
            '🤖': 'ai_assistant',
            '📂': 'files_templates',
            '🧩': 'add_components',
            '🎨': 'appearance',
            '🔌': 'plugins',
            '🖼️': 'image_assets'
        };
        
        let lastState = {};
        let updateTimer = null;
        
        function getExpanderState() {
            const state = {};
            const expanders = document.querySelectorAll('[data-testid="stExpander"]');
            
            expanders.forEach(expander => {
                // Get the expander header
                const header = expander.querySelector('summary') || 
                             expander.querySelector('[data-testid="stExpanderToggleIcon"]')?.closest('div')?.parentElement;
                if (!header) return;
                
                const headerText = header.textContent || '';
                let expanderKey = null;
                
                // Match by emoji
                for (const [emoji, key] of Object.entries(expanderMap)) {
                    if (headerText.includes(emoji)) {
                        expanderKey = key;
                        break;
                    }
                }
                
                if (!expanderKey) return;
                
                // Check if expanded
                const toggleIcon = expander.querySelector('[data-testid="stExpanderToggleIcon"]');
                const isExpanded = expander.hasAttribute('open') || 
                                 (toggleIcon && toggleIcon.getAttribute('aria-expanded') === 'true');
                
                state[expanderKey] = isExpanded;
            });
            
            return state;
        }

        function enforceSingleOpen(preferredExpander = null) {
            const expanders = Array.from(document.querySelectorAll('[data-testid="stExpander"]'));
            if (expanders.length === 0) return;
            
            // Determine which expander should remain open
            let target = preferredExpander;
            const openOnes = expanders.filter(exp => exp.hasAttribute('open') || exp.getAttribute('open') === 'true');
            if (!target && openOnes.length > 0) {
                target = openOnes[openOnes.length - 1];
            }
            if (!target && openOnes.length === 0) {
                target = expanders.find(exp => (exp.textContent || '').includes('🤖')) || null;
            }
            
            // If nothing is open, do nothing (allows "all folded")
            if (!target) return;
            
            expanders.forEach(exp => {
                if (exp !== target) {
                    exp.removeAttribute('open');
                    const toggleIcon = exp.querySelector('[data-testid="stExpanderToggleIcon"]');
                    if (toggleIcon) {
                        toggleIcon.setAttribute('aria-expanded', 'false');
                    }
                }
            });
        }
        
        function updateState() {
            const currentState = getExpanderState();
            const stateChanged = JSON.stringify(currentState) !== JSON.stringify(lastState);
            
            if (stateChanged) {
                lastState = currentState;
                
                // Store in localStorage for persistence
                try {
                    localStorage.setItem('mp_sidebar_expanded', JSON.stringify(currentState));
                } catch(e) {}
                
                // Update URL with state (triggers Streamlit rerun)
                const stateJson = encodeURIComponent(JSON.stringify(currentState));
                const currentUrl = new URL(window.location);
                currentUrl.searchParams.set('expander_state', stateJson);
                
                // Use history.replaceState to avoid adding to history
                window.history.replaceState({}, '', currentUrl);
                
                // Trigger Streamlit rerun by dispatching a custom event
                window.dispatchEvent(new Event('popstate'));
            }
        }
        
        // Watch for expander clicks
        document.addEventListener('click', function(e) {
            const expanderEl = e.target.closest('[data-testid="stExpander"]');
            const toggleIcon = e.target.closest('[data-testid="stExpanderToggleIcon"]');
            if (expanderEl || toggleIcon) {
                const targetExpander = expanderEl || (toggleIcon ? toggleIcon.closest('[data-testid="stExpander"]') : null);
                clearTimeout(updateTimer);
                // Slight delay so the native toggle state updates first
                setTimeout(() => {
                    enforceSingleOpen(targetExpander);
                    updateTimer = setTimeout(updateState, 200);
                }, 80);
            }
        }, true);
        
        // Watch for DOM changes
        const observer = new MutationObserver(function() {
            clearTimeout(updateTimer);
            updateTimer = setTimeout(function() {
                enforceSingleOpen();
                updateState();
            }, 300);
        });
        
        function setupTracking() {
            const sidebar = document.querySelector('section[data-testid="stSidebar"]');
            if (sidebar) {
                observer.observe(sidebar, {
                    childList: true,
                    subtree: true,
                    attributes: true,
                    attributeFilter: ['open', 'aria-expanded']
                });
                
                // Load saved state from localStorage
                try {
                    const saved = localStorage.getItem('mp_sidebar_expanded');
                    if (saved) {
                        lastState = JSON.parse(saved);
                    }
                } catch(e) {}
                
                // Initial state check
                setTimeout(function() {
                    enforceSingleOpen();
                    updateState();
                }, 500);
            } else {
                setTimeout(setupTracking, 200);
            }
        }
        
        setupTracking();
    })();
    </script>
    """
    st.components.v1.html(expander_tracker_html, height=0)

    # Inject JavaScript to remove help tooltips (DeltaGenerator, etc.)
    # Using st.markdown to run in main page context (not iframe)
    help_remover_script = """
    <script>
    // Immediately run when script loads
    (function() {
        var removedCount = 0;
        
        function removeAllHelpElements() {
            var sidebar = document.querySelector('section[data-testid="stSidebar"]');
            if (!sidebar) return;
            
            // Find ALL elements that might be help tooltips
            var allElements = sidebar.querySelectorAll('*');
            for (var i = 0; i < allElements.length; i++) {
                var el = allElements[i];
                var text = (el.textContent || '').trim();
                var className = el.className || '';
                
                // Check if element has help-related classes or data-testid
                var isHelpElement = false;
                if (el.getAttribute && el.getAttribute('data-testid') === 'stHelp') isHelpElement = true;
                if (typeof className === 'string') {
                    if (className.includes('stHelp') || 
                        className.includes('1t7d4j1') || 
                        className.includes('e1rz36mz4')) {
                        isHelpElement = true;
                    }
                }
                
                // Also check for DeltaGenerator text (long technical text)
                if (text.length > 50 && (text.includes('DeltaGenerator') || text.includes('LockedCursor'))) {
                    isHelpElement = true;
                }
                
                if (isHelpElement && el.parentNode) {
                    try {
                        el.parentNode.removeChild(el);
                        removedCount++;
                    } catch(e) {}
                }
            }
        }
        
        // Run immediately
        removeAllHelpElements();
        
        // Keep running continuously
        setInterval(function() {
            removeAllHelpElements();
        }, 10);  // Every 10ms
        
        // Also watch for DOM changes
        var observer = new MutationObserver(function(mutations) {
            removeAllHelpElements();
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
        
        // Persist forever - runs every 5ms
        setInterval(removeAllHelpElements, 5);
    })();
    </script>
    """
    # Add a third persistent layer that runs FOREVER
    persistent_help_remover = """
    <script>
    (function() {
        function isHelpElement(el) {
            var text = (el.textContent || '').trim();
            var className = el.className || '';
            
            if (el.getAttribute && el.getAttribute('data-testid') === 'stHelp') return true;
            if (typeof className === 'string') {
                if (className.includes('stHelp') || 
                    className.includes('1t7d4j1') || 
                    className.includes('e1rz36mz4')) {
                    return true;
                }
            }
            if (text.length > 30 && (text.includes('DeltaGenerator') || text.includes('LockedCursor'))) {
                return true;
            }
            return false;
        }
        
        function removeAll() {
            var all = document.querySelectorAll('*');
            for (var i = 0; i < all.length; i++) {
                if (isHelpElement(all[i]) && all[i].parentNode) {
                    try { all[i].parentNode.removeChild(all[i]); } catch(e) {}
                }
            }
        }
        
        // Run forever
        setInterval(removeAll, 1); // Every 1ms
    })();
    </script>
    """
    st.markdown(persistent_help_remover, unsafe_allow_html=True)

    with st.sidebar:
        st.title(get_text("app_title"))
        st.caption(get_text("app_subtitle"))
        
        # View & language: Simple Mode, Language, Preview Mode in one section
        with st.expander(f"⚙️ {get_text('view_language')}", expanded=st.session_state.get("view_language_expanded", False)):
            settings_col1, settings_col2 = st.columns(2)
            with settings_col1:
                simple_mode = st.toggle(f"✨ {get_text('simple_mode')}", value=st.session_state.get("simple_mode", True), key="simple_mode")
            with settings_col2:
                current_lang = st.session_state.get("ui_language", "en")
                is_chinese = current_lang == "zh"
                lang_toggle = st.toggle("🌐 中文", value=is_chinese, key="lang_toggle", help="Switch language / 切换语言")
                new_lang = "zh" if lang_toggle else "en"
                if new_lang != current_lang:
                    st.session_state.ui_language = new_lang
                    st.session_state.components_wechat_only = False
                    if not st.session_state.get("ai_busy"):
                        key = st.session_state.get("last_ai_status_key", "ai_status_idle")
                        action_label = st.session_state.get("last_ai_status_action", "")
                        if key == "ai_status_last_action" and action_label:
                            st.session_state.last_ai_status = get_text(key).format(action=action_label)
                        else:
                            st.session_state.last_ai_status = get_text(key)
                    st.rerun()
            view = st.radio(
                f"📱 {get_text('preview_mode')}",
                [get_text('mobile_preview'), get_text('pc_preview')],
                horizontal=True,
                help=get_text("preview_mode_help"),
                key="preview_view_radio"
            )
            st.session_state.preview_view = "Mobile" if view == get_text('mobile_preview') else "PC"

        # Initialize sidebar expander state memory
        if "sidebar_expanded" not in st.session_state:
            st.session_state.sidebar_expanded = {
                "ai_assistant": False,  # Folded by default
                "files_templates": False,
                "add_components": not simple_mode,
                "appearance": not simple_mode,
                "plugins": False,
                "image_assets": False
            }
        
        
        # 1. AI ASSISTANT (Most important - at the top)
        ai_expanded = st.session_state.sidebar_expanded.get("ai_assistant", not simple_mode)
        with st.expander(f"🤖 {get_text('ai_assistant')}", expanded=ai_expanded):
            # Initialize providers
            if HAS_PROVIDER_MANAGER:
                init_providers()
                manager = get_manager()
                providers = manager.get_providers()
                security_info = manager.get_security_info()
            else:
                manager = None
                providers = []
                security_info = {"icon": "🔴", "name": "Security", "desc": "Not available", "risk": "N/A"}

            # Security level indicator
            st.caption(f"{security_info['icon']} {security_info['name']}: {security_info['desc']}")

            if not HAS_PROVIDER_MANAGER or not providers:
                # Fallback to old implementation
                prev_engine = st.session_state.get("last_engine", "None")
                other_engines = ["Gemini", "OpenAI", "OpenRouter"]
                engine_options = ["None", "Ollama (Local)"] + sorted(other_engines)
                prev_ai_cfg = st.session_state.get("ai_cfg", {"engine": "None", "key": "", "url": "", "model": ""})
                engine_default_idx = engine_options.index(prev_ai_cfg.get("engine", "None")) if prev_ai_cfg.get("engine", "None") in engine_options else engine_options.index("None")

                engine = st.selectbox(get_text("ai_engine"), engine_options, index=engine_default_idx, key="ai_engine_select")
                ai_cfg = {"engine": engine, "key": prev_ai_cfg.get("key", ""), "url": prev_ai_cfg.get("url", ""), "model": prev_ai_cfg.get("model", "")}

                if engine != "None":
                    if engine == "OpenRouter":
                        ai_cfg["key"] = st.text_input(get_text("api_key"), type="password", key="openrouter_api_key")
                        ai_cfg["url"] = "https://openrouter.ai/api/v1"
                        ai_cfg["model"] = st.text_input(get_text("model"), value="openai/gpt-4o-mini", key="openrouter_model")
                    elif engine == "OpenAI":
                        ai_cfg["key"] = st.text_input(get_text("api_key"), type="password", key="openai_api_key")
                        ai_cfg["url"] = "https://api.openai.com/v1"
                        ai_cfg["model"] = st.text_input(get_text("model"), value="gpt-4o-mini", key="openai_model")
                    elif engine == "Gemini":
                        ai_cfg["key"] = st.text_input(get_text("api_key"), type="password", key="gemini_api_key")
                        ai_cfg["url"] = "https://generativelanguage.googleapis.com/v1beta/openai"
                        ai_cfg["model"] = st.text_input(get_text("model"), value="gemini-1.5-pro-latest", key="gemini_model")
                    elif engine == "Ollama (Local)":
                        ai_cfg["url"] = st.text_input("Ollama URL", value="http://localhost:11434/v1", key="ollama_url")
                        ai_cfg["model"] = st.text_input(get_text("model"), value="llama3", key="ollama_model")

                    if st.button(f"🔌 {get_text('connect')}", use_container_width=True):
                        alive, msg = check_connection(engine, ai_cfg.get("url", ""), ai_cfg.get("key", ""))
                        if alive:
                            st.toast(msg, icon="✅")
                        else:
                            st.toast(msg, icon="❌")

                st.session_state.ai_cfg = ai_cfg
                st.session_state.ai_content_type = None if engine == "None" else "Auto-detect"
                st.session_state.context_text = ""

            else:
                # Cherry Studio-style provider selector
                provider_options = [(p.id, f"{_get_provider_icon(p.provider_type)} {p.name}") for p in providers]
                provider_ids = [p[0] for p in provider_options]
                provider_labels = [p[1] for p in provider_options]

                selected_idx = 0
                current_id = st.session_state.get("selected_provider_id")
                if current_id and current_id in provider_ids:
                    selected_idx = provider_ids.index(current_id)

                selected_provider_id = st.selectbox(
                    f"🤖 {get_text('provider')}",
                    options=provider_ids,
                    format_func=lambda x: next((l for i, l in enumerate(provider_labels) if provider_ids[i] == x), x),
                    index=selected_idx,
                    key="provider_select"
                )
                st.session_state.selected_provider_id = selected_provider_id

                if selected_provider_id:
                    provider = manager.get_provider(selected_provider_id)
                    if provider:
                        # Show connection status
                        api_key = manager.get_api_key(selected_provider_id)
                        alive, status_msg = manager.check_connection(provider, api_key)
                        st.caption(status_msg)

                        # 4 Essential Elements from Cherry Studio:
                        # 1. Provider Name (shown in selector, read-only)
                        # 2. API Key
                        # 3. API Host
                        # 4. Models

                        # Element 2: API Key
                        if provider.provider_type != "ollama":
                            # Use session_state to track key changes
                            key_session_key = f"apikey_value_{selected_provider_id}"
                            if key_session_key not in st.session_state:
                                st.session_state[key_session_key] = manager.get_api_key(selected_provider_id) or ""

                            def save_api_key():
                                new_key = st.session_state[key_session_key]
                                if new_key:
                                    manager.set_api_key(selected_provider_id, new_key)
                                    st.toast(get_text("toast_saved"), icon="✅")
                                else:
                                    manager.storage.delete_key(selected_provider_id)

                            st.text_input(
                                "🔑 API Key",
                                value=st.session_state[key_session_key],
                                type="password",
                                placeholder="sk-...",
                                key=key_session_key,
                                help="Press Enter or click outside to save",
                                on_change=save_api_key
                            )

                        # Element 3: API Host
                        api_host = st.text_input(
                            f"🌐 {get_text('api_host')}",
                            value=provider.api_host,
                            placeholder="https://api.openai.com/v1",
                            key=f"host_{selected_provider_id}"
                        )
                        if api_host != provider.api_host:
                            manager.update_provider(selected_provider_id, api_host=api_host)
                            st.rerun()

                        # Element 4: Models
                        model_options = provider.models if provider.models else ["No models configured"]
                        current_model_idx = 0
                        if provider.default_model and provider.default_model in model_options:
                            current_model_idx = model_options.index(provider.default_model)

                        selected_model = st.selectbox(
                            f"📋 {get_text('model')}",
                            options=model_options,
                            index=current_model_idx,
                            key=f"model_{selected_provider_id}"
                        )
                        if selected_model != provider.default_model:
                            manager.update_provider(selected_provider_id, default_model=selected_model)

                        # Fetch models button
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button(get_text("fetch_models"), use_container_width=True, key=f"fetch_{selected_provider_id}", help=get_text("fetch_models")):
                                with st.spinner(get_text("fetching")):
                                    success, models, msg = manager.fetch_models(provider, api_key)
                                    if success and models:
                                        manager.update_provider(selected_provider_id, models=models)
                                        st.toast(msg, icon="✅")
                                        # Rerun to refresh the UI with updated models
                                        st.rerun()
                                    else:
                                        st.toast(msg, icon="ℹ️")
                        with col2:
                            st.caption(get_text("models_available").format(count=len(provider.models)))

                        # Test connection button
                        if st.button(f"🔌 {get_text('test_connection')}", use_container_width=True, key=f"test_{selected_provider_id}"):
                            alive, msg = manager.check_connection(provider, api_key)
                            if alive:
                                st.toast(msg, icon="✅")
                            else:
                                st.toast(msg, icon="❌")

                        # Get config for AI calls
                        config = get_provider_config(selected_provider_id)
                        st.session_state.ai_cfg = config
                        st.session_state.ai_content_type = "Auto-detect"
                        st.session_state.context_text = ""
        
        # 2. FILES & TEMPLATES
        files_expanded = st.session_state.sidebar_expanded.get("files_templates", False)
        with st.expander(f"📂 {get_text('files_templates')}", expanded=files_expanded):
            file_tab, template_tab = st.tabs([f"📁 {get_text('files')}", f"📄 {get_text('templates')}"])
            
            with file_tab:
                # File Management Section
                files = [f for f in os.listdir("projects") if f.endswith(".md") and not f.startswith(".")] if os.path.exists("projects") else []
                files = sorted(files, key=lambda x: os.path.getmtime(f"projects/{x}"), reverse=True)
                
                if files:
                    # Search box for files
                    file_search = st.text_input(f"🔍 {get_text('search_files')}", key="file_search", placeholder=get_text('search_files'))
                    filtered_files = [f for f in files if file_search.lower() in f.lower()] if file_search else files
                    
                    if filtered_files:
                        # File selection with better display
                        sel_file = st.selectbox(
                            get_text("select_file"),
                            ["New File"] + filtered_files,
                            format_func=lambda x: "📄 " + x.replace(".md", "") if x != "New File" else "➕ New File",
                            key="file_selector"
                        )
                        
                        # File actions
                        if sel_file != "New File":
                            file_col1, file_col2, file_col3 = st.columns([1, 1, 1])
                            with file_col1:
                                if st.button(get_text("load_button"), use_container_width=True, key="load_file_btn"):
                                    loaded_content, error = load_project(sel_file)
                                    if error:
                                        if ErrorHandler:
                                            ErrorHandler.show_error_with_details(error)
                                        else:
                                            st.toast(error, icon="❌")
                                    elif loaded_content:
                                        st.session_state.content = loaded_content
                                        st.session_state.reset_editor = True
                                        project_name = sel_file.replace(".md", "")
                                        st.session_state.current_project_name = project_name
                                        clear_auto_save(project_name)
                                        if loaded_content:
                                            st.session_state.undo_stack = [loaded_content]
                                            st.session_state.redo_stack = []
                                        # Reset preview cache to force re-render after file load
                                        st.session_state.last_preview_content_hash = None
                                        if PerformanceOptimizer and st.session_state.get("performance_optimizer"):
                                            # Clear the preview cache
                                            optimizer = st.session_state.performance_optimizer
                                            optimizer.preview_cache = {}
                                            optimizer.last_preview_hash = None
                                            optimizer.last_preview_time = 0
                                        st.toast(get_text("toast_file_loaded").format(file_name=sel_file), icon="✅")
                                        time.sleep(0.5)
                                        st.rerun()
                            
                            with file_col2:
                                if st.button(get_text("delete_button"), use_container_width=True, key="delete_file_btn"):
                                    try:
                                        os.remove(f"projects/{sel_file}")
                                        version_file = get_version_file_path(sel_file.replace(".md", ""))
                                        if os.path.exists(version_file):
                                            os.remove(version_file)
                                        st.toast(get_text("toast_file_deleted").format(file_name=sel_file), icon="✅")
                                        time.sleep(0.5)
                                        st.rerun()
                                    except Exception as e:
                                        st.toast(get_text("toast_delete_failed").format(error=e), icon="❌")
                            
                            with file_col3:
                                if st.button(get_text("history_button"), use_container_width=True, key="version_history_btn"):
                                    st.session_state.show_version_history = sel_file.replace(".md", "")
                                    st.rerun()
                            
                            # Show file info
                            file_path = f"projects/{sel_file}"
                            if os.path.exists(file_path):
                                file_size = os.path.getsize(file_path)
                                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                                file_info_text = get_text("file_info").format(
                                    size=f"{file_size:,}",
                                    date=file_mtime.strftime('%Y-%m-%d %H:%M')
                                )
                                st.caption(file_info_text)
                    else:
                        st.toast(get_text("no_files_search"), icon="ℹ️")
                else:
                    st.toast(get_text("no_files_yet"), icon="ℹ️")
                
                st.divider()
                
                # Save Section
                st.subheader(f"💾 {get_text('save_current')}")
                save_name = st.text_input(get_text("file_name"), value=st.session_state.get("current_project_name", ""), key="save_name_input", placeholder=get_text("file_name_placeholder"))
                save_col1, save_col2 = st.columns([1, 1])
                with save_col1:
                    if st.button(get_text("save_button"), use_container_width=True, key="save_btn"):
                        if save_name:
                            if "content" in st.session_state:
                                result = save_project(save_name, st.session_state.content)
                                if result.startswith("✅"):
                                    st.toast(result, icon="✅")
                                    if save_name:
                                        clear_auto_save(save_name)
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    if ErrorHandler:
                                        ErrorHandler.show_error_with_details(result)
                                    else:
                                        st.toast(result, icon="❌")
                            else:
                                st.toast(get_text("toast_no_content_to_save"), icon="⚠️")
                        else:
                            st.toast(get_text("toast_enter_file_name"), icon="⚠️")
                
                with save_col2:
                    # Version History Settings
                    # Streamlit automatically updates session_state when checkbox value changes
                    st.checkbox(f"📜 {get_text('version_history')}", value=st.session_state.get("version_history_enabled", True), key="version_history_enabled")
                
                force_save_col1, force_save_col2 = st.columns([1, 1])
                with force_save_col1:
                    if st.button(get_text("force_save"), use_container_width=True, key="force_save_btn", help=get_text("force_save_help")):
                        if save_name:
                            if "content" in st.session_state:
                                result = save_project(save_name, st.session_state.content)
                                if result.startswith("✅"):
                                    st.toast(result, icon="✅")
                                    clear_auto_save(save_name)
                                else:
                                    st.toast(result, icon="❌")
                            else:
                                st.toast(get_text("toast_no_content_to_save"), icon="⚠️")
                        else:
                            st.toast(get_text("toast_enter_file_name"), icon="⚠️")
                with force_save_col2:
                    st.caption(get_text("force_save_help"))
            
            with template_tab:
                # Template Selection Section
                template_categories = {
                    "📝 Quick Start": ["Empty Draft", "⚡ Quick Update", "📌 Simple Notice"],
                    "📢 Product & Announcements": ["📢 Product Launch", "🎉 Feature Announcement", "📱 App Update"],
                    "📰 Content & News": ["📰 Weekly Newsletter", "📝 Blog Post", "📊 Industry Report"],
                    "🎯 Marketing & Promotions": ["🎯 Promotional Campaign", "💼 Case Study", "🎁 Special Offer"],
                    "📚 Educational": ["📚 Tutorial Guide", "🎓 How-To Article", "📖 FAQ Document"],
                    "🎪 Events": ["🎪 Event Announcement", "📅 Webinar Invitation", "🎊 Company Milestone"],
                    "👥 Internal & Team": ["📋 Meeting Summary", "📢 Internal Announcement", "🎯 Project Update"],
                    "💬 Customer & Support": ["💬 Customer Testimonial", "🆘 Support Guide", "🎁 Welcome Message"],
                    "🎨 Special Formats": ["📸 Photo Story", "🎬 Video Post", "📊 Data Report", "💡 Tip of the Day"]
                }
                
                # Show total template count
                total_templates = len(TEMPLATES) if TEMPLATES else 0
                st.caption(f"📚 {total_templates} {get_text('templates_available')}")
                
                # Category selector with counts
                category_options = [f"All Templates ({total_templates})"]
                for cat, templates in template_categories.items():
                    count = len([t for t in templates if t in TEMPLATES])
                    category_options.append(f"{cat} ({count})")
                
                selected_category_idx = st.selectbox(
                    get_text("category"),
                    category_options,
                    index=0,
                    key="template_category"
                )
                
                # Extract category name without count
                if "All Templates" in selected_category_idx:
                    selected_category = "All Templates"
                else:
                    selected_category = selected_category_idx.rsplit(" (", 1)[0]
                
                # Filter templates
                if selected_category == "All Templates":
                    available_templates = list(TEMPLATES.keys())
                else:
                    available_templates = template_categories[selected_category]
                
                # Template search
                template_search = st.text_input(f"🔍 {get_text('search_templates')}", key="template_search", placeholder=get_text('search_templates'))
                if template_search:
                    available_templates = [t for t in available_templates if template_search.lower() in t.lower()]
                
                if available_templates:
                    # Template selector
                    sel_template = st.selectbox(
                        get_text("select_template"),
                        available_templates,
                        index=0,
                        key="template_selector"
                    )
                    
                    # Template preview and use button
                    template_col1, template_col2 = st.columns([2, 1])
                    with template_col1:
                        if sel_template != "Empty Draft" and sel_template in TEMPLATES:
                            template_preview = TEMPLATES[sel_template]
                            preview_text = template_preview[:300] + "..." if len(template_preview) > 300 else template_preview
                            with st.expander(f"👁️ {get_text('preview')}", expanded=True):
                                st.code(preview_text, language="markdown")
                    
                    with template_col2:
                        if st.button(f"📄 {get_text('use_template')}", use_container_width=True, key="use_template_btn"):
                            if sel_template and sel_template in TEMPLATES:
                                template_content = TEMPLATES[sel_template]
                                st.session_state.content = template_content
                                st.session_state.reset_editor = True
                                # Reset preview cache to force re-render
                                st.session_state.last_preview_content_hash = None
                                if PerformanceOptimizer and st.session_state.get("performance_optimizer"):
                                    optimizer = st.session_state.performance_optimizer
                                    optimizer.preview_cache = {}
                                    optimizer.last_preview_hash = None
                                    optimizer.last_preview_time = 0

                                st.session_state.current_project_name = None
                                if template_content:
                                    st.session_state.undo_stack = [template_content]
                                    st.session_state.redo_stack = []
                                st.toast(f"✅ Loaded: {sel_template}")
                                st.rerun()
                            elif sel_template:
                                st.toast(get_text("toast_template_not_found").format(template=sel_template, count=len(TEMPLATES)), icon="❌")
                            else:
                                st.toast(get_text("no_templates_match"), icon="ℹ️")
            
            # Version History Modal
            if st.session_state.get("show_version_history"):
                project_name = st.session_state.show_version_history
                st.divider()
                st.subheader(f"📜 {get_text('version_history')}: {project_name}")
                versions = get_version_history(project_name)
                
                if versions:
                    # Show version list
                    for idx, version in enumerate(reversed(versions)):
                        version_time = datetime.fromtimestamp(version.get("timestamp", 0))
                        version_size = version.get("size", 0)
                        
                        ver_col1, ver_col2, ver_col3 = st.columns([3, 1, 1])
                        with ver_col1:
                            st.write(f"**Version {len(versions) - idx}** - {version_time.strftime('%Y-%m-%d %H:%M:%S')}")
                            st.caption(f"Size: {version_size:,} bytes")
                        with ver_col2:
                            if st.button("📂 Restore", key=f"restore_v{idx}", use_container_width=True):
                                restored = restore_version(project_name, len(versions) - 1 - idx)
                                if restored:
                                    st.session_state.content = restored
                                    st.session_state.reset_editor = True
                                    # Reset preview cache to force re-render
                                    st.session_state.last_preview_content_hash = None
                                    if PerformanceOptimizer and st.session_state.get("performance_optimizer"):
                                        optimizer = st.session_state.performance_optimizer
                                        optimizer.preview_cache = {}
                                        optimizer.last_preview_hash = None
                                        optimizer.last_preview_time = 0

                                    st.toast(get_text("toast_version_restored"), icon="✅")
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    st.toast(get_text("toast_restore_failed"), icon="❌")
                        with ver_col3:
                            if st.button("👁️ View", key=f"view_v{idx}", use_container_width=True):
                                st.session_state.view_version_index = len(versions) - 1 - idx
                                st.session_state.view_version_project = project_name
                    
                    # Storage info
                    storage_size = get_version_storage_size(project_name)
                    st.caption(f"💾 Version history storage: {storage_size:,} bytes ({storage_size/1024:.1f} KB)")
                    
                    if st.button("🗑️ Clear History", key="clear_version_history"):
                        version_file = get_version_file_path(project_name)
                        if os.path.exists(version_file):
                            os.remove(version_file)
                        st.toast(get_text("toast_version_history_cleared"), icon="✅")
                        time.sleep(0.5)
                        st.rerun()
                else:
                    st.toast(get_text("toast_no_version_history"), icon="ℹ️")
                
                if st.button("❌ Close", key="close_version_history"):
                    st.session_state.show_version_history = None
                    st.rerun()
            
            # Migration Tool removed - users keep ## for headings, use ::: card for cards
            
        # 2. COMPONENTS (All component buttons in one expander)
        components_expanded = st.session_state.sidebar_expanded.get("add_components", not simple_mode)
        with st.expander(f"🧩 {get_text('add_components')}", expanded=components_expanded):
            st.caption(get_text("click_to_insert"))
            wechat_only = st.checkbox(
                get_text("wechat_only_switch"),
                key="components_wechat_only",
                value=st.session_state.get("components_wechat_only", False),
                help=get_text("click_to_insert_hint"),
            )
            
            # Group components by category (with translations)
            component_groups = {
                get_text("layout"): [
                    {
                        "name": get_text("comp_hero"),
                        "syntax": "::: hero\n# Title\nSubtitle\n:::",
                        "wechat_supported": True,
                    },
                    {
                        "name": get_text("comp_2col"),
                        "syntax": "::: col-2\nLeft\n--split--\nRight\n:::",
                        "wechat_supported": True,
                    },
                    {
                        "name": get_text("comp_3col"),
                        "syntax": "::: col-3\nOne\n--split--\nTwo\n--split--\nThree\n:::",
                        "wechat_supported": True,
                    },
                ],
                get_text("content"): [
                    {
                        "name": get_text("comp_steps"),
                        "syntax": "::: steps\n1. Step One\n2. Step Two\n:::",
                        "wechat_supported": True,
                    },
                    {
                        "name": get_text("comp_timeline"),
                        "syntax": "::: timeline\n2024 Start\n2025 Launch\n:::",
                        "wechat_supported": True,
                    },
                    {
                        "name": get_text("comp_table"),
                        "syntax": "::: table\nHeader 1 | Header 2 | Header 3\nRow 1 Col 1 | Row 1 Col 2 | Row 1 Col 3\n:::",
                        "wechat_supported": True,
                    },
                    {
                        "name": get_text("comp_card"),
                        "syntax": "::: card\n## Card Title\nCard content here.\n:::",
                        "wechat_supported": True,
                    },
                    {
                        "name": get_text("comp_center"),
                        "syntax": "::: center\nCentered text here\n:::",
                        "wechat_supported": True,
                    },
                ],
                get_text("interactive"): [
                    {
                        "name": get_text("comp_reveal"),
                        "syntax": "::: reveal\nSecret Content\n--cover--\n👆\n:::",
                        "wechat_supported": True,
                    },
                    {
                        "name": get_text("comp_badge"),
                        "syntax": "[badge: NEW]",
                        "wechat_supported": True,
                    },
                    {
                        "name": get_text("comp_button"),
                        "syntax": "\n[Button Label](https://link.com)\n",
                        "wechat_supported": True,
                    },
                ],
                get_text("media"): [
                    {
                        "name": get_text("comp_image"),
                        "syntax": "[IMG: describe your image]",
                        "wechat_supported": True,
                    },
                    {
                        "name": get_text("comp_video"),
                        "syntax": '::: video src="https://example.com/video.mp4" poster="" caption="" autoplay=false muted=false loop=false :::',
                        "wechat_supported": False,  # WeChat/WeCom does not render video component
                    },
                ],
            }
            
            # Helper function to insert component at cursor position
            # Defined outside try block so both component and plugin sections can access it
            def insert_component_at_cursor(syntax):
                """Insert component syntax - JavaScript will handle insertion at cursor"""
                # Store syntax for JS to insert - DON'T update Python state yet
                # JavaScript will insert and then we'll read it back
                st.session_state.pending_component_insert = syntax
                # Note: No need to call st.rerun() here - Streamlit automatically reruns after callbacks
            
            try:
                # Show grouped built-in components (now with translated names)
                layout_text = get_text("layout")
                content_text = get_text("content")
            
                for group_name, components in component_groups.items():
                    if not simple_mode or group_name in [layout_text, content_text, get_text("media")]:
                        filtered_components = [
                            comp for comp in components if (not wechat_only or comp["wechat_supported"])
                        ]
                        if not filtered_components:
                            continue
                        st.markdown(f"**{group_name}**")
                        
                        # Display in grid (3 columns)
                        cols_per_row = 3 if len(filtered_components) >= 3 else max(1, len(filtered_components))
                        for i in range(0, len(filtered_components), cols_per_row):
                            cols = st.columns(cols_per_row)
                            for j, col in enumerate(cols):
                                if i + j < len(filtered_components):
                                    comp_name = filtered_components[i + j]["name"]
                                    comp_syntax = filtered_components[i + j]["syntax"]

                                    def add_component(syntax=comp_syntax):
                                        if "content" not in st.session_state: 
                                            st.session_state.content = ""
                                        insert_component_at_cursor(syntax)
                                    col.button(comp_name, on_click=add_component, use_container_width=True, help=comp_name)
                        st.markdown("")  # Spacing between groups
                
                # Add plugin components section
                if get_plugin_registry and not simple_mode:
                    try:
                        registry = get_plugin_registry()
                        plugins = registry.get_plugins_by_category()
                        
                        if plugins:
                            st.markdown("**🔌 Plugins**")
                            
                            # Show all plugins in a grid
                            plugin_list = [
                                plugin
                                for plugin in list(plugins)
                                if (not wechat_only or plugin.compatibility.get("wechat", False))
                            ]
                            if not plugin_list:
                                st.markdown("_No compatible plugins._")
                            
                            cols_per_row = 2
                            for i in range(0, len(plugin_list), cols_per_row):
                                cols = st.columns(cols_per_row)
                                for j, col in enumerate(cols):
                                    if i + j < len(plugin_list):
                                        plugin = plugin_list[i + j]
                                        if plugin.insertion_tool:
                                            plugin_display_name = get_plugin_name(plugin.name)
                                            
                                            def add_plugin_component(plugin_syntax=plugin.insertion_tool):
                                                if "content" not in st.session_state: 
                                                    st.session_state.content = ""
                                                # Use the same insertion logic as regular components
                                                insert_component_at_cursor(plugin_syntax)
                                        
                                            plugin_description = get_plugin_description(plugin.name, plugin.description)
                                            col.button(
                                                f"{plugin_display_name}",
                                                on_click=add_plugin_component,
                                                use_container_width=True,
                                                help=f"{plugin_description or get_text('plugin_component')}"
                                            )
                    except Exception as e:
                        pass  # Silently fail for plugins
                            
            except Exception as e:
                st.toast(get_text("toast_components_unavailable"), icon="❌")

        # 3. APPEARANCE (Grouped settings)
        appearance_expanded = st.session_state.sidebar_expanded.get("appearance", not simple_mode)
        with st.expander(f"🎨 {get_text('appearance')}", expanded=appearance_expanded):
            t_name = st.selectbox(
                get_text("theme"), 
                list(STYLES.keys()),
                help=get_text("choose_theme_help")
            )
        active_theme = STYLES[t_name]
        st.session_state.active_theme = active_theme 
        
        # Get theme and view (use session state if expander was collapsed)
        if st.session_state.get("active_theme"):
            active_theme = st.session_state.active_theme
        else:
            t_name = list(STYLES.keys())[0]
            active_theme = STYLES[t_name]
            st.session_state.active_theme = active_theme
        
        view = st.session_state.get("preview_view", "Mobile")
        
        # 5. PLUGINS (Plugin System) - Simplified UX
        if get_plugin_registry and not simple_mode:
            plugins_expanded = st.session_state.sidebar_expanded.get("plugins", False)
            with st.expander(f"🔌 {get_text('plugins')}", expanded=plugins_expanded):
                try:
                    registry = get_plugin_registry()
                    plugins = registry.get_plugins_by_category()
                    
                    if plugins:
                        st.toast(f"✅ **{len(plugins)} {get_text('plugins_active')}**", icon="✅")
                        st.caption(get_text("plugin_components_hint"))
                        
                        # Quick actions
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"🔄 {get_text('reload_plugins')}", use_container_width=True, help=get_text("reload_plugins_help")):
                                try:
                                    from plugin_system import reload_plugin_registry
                                    reload_plugin_registry()
                                    st.toast(get_text("toast_reloaded"), icon="✅")
                                    time.sleep(0.5)
                                    st.rerun()
                                except Exception as e:
                                    st.toast(f"Failed: {e}", icon="❌")
                        with col2:
                            if st.button(f"📚 {get_text('guide')}", use_container_width=True, help=get_text("view_plugin_guide_help")):
                                st.session_state.show_plugin_docs = True
                                st.rerun()
                        
                        st.divider()
                        st.markdown(f"**📦 {get_text('installed_plugins')}**")
                        
                        # Show plugins in a simple list
                        for plugin in plugins:
                            compat = "✅ WeChat" if plugin.compatibility.get("wechat", False) else "🌐 HTML only"
                            plugin_display_name = get_plugin_name(plugin.name)
                            plugin_description = get_plugin_description(plugin.name, plugin.description)
                            with st.expander(f"**{plugin_display_name}** - {compat}", expanded=False):
                                if plugin_description:
                                    st.caption(plugin_description)
                                if plugin.insertion_tool:
                                    st.code(plugin.insertion_tool, language="markdown")
                                    st.caption(f"💡 {get_text('syntax_inserted')}")
                    else:
                        # No plugins - show simple getting started
                        st.toast(get_text("toast_no_plugins"), icon="🚀")
                        st.markdown("""
                        **Want to add custom components?**
                        
                        1. Go to `plugins/` folder
                        2. Copy `example_callout.py` 
                        3. Edit it to create your component
                        4. Click "🔄 Reload" above
                        5. Your component appears in "Add Components"!
                        """)
                        
                        if st.button(f"📚 {get_text('view_full_guide')}", use_container_width=True):
                            st.session_state.show_plugin_docs = True
                            st.rerun()
                    
                    # Migration tool removed - users keep ## for headings
                    
                    # Plugin Documentation (shown in Plugins section)
                    if st.session_state.get("show_plugin_docs", False):
                        st.divider()
                        is_zh = st.session_state.get("ui_language") == "zh"
                        st.subheader("📚 插件文档" if is_zh else "📚 Plugin Documentation")
                        
                        if is_zh:
                            doc_tabs = st.tabs(["概述", "创建插件", "示例", "微信兼容性"])
                        else:
                            doc_tabs = st.tabs(["Overview", "Creating Plugins", "Examples", "WeChat Compatibility"])
                        
                        with doc_tabs[0]:
                            if is_zh:
                                st.markdown("""
                                ## 什么是插件？
                                
                                插件允许你创建自定义 Markdown 组件，扩展 MarkPolish Studio 的功能。
                                
                                ### 优势
                                - ✨ 无需修改核心代码即可添加新组件
                                - 🔄 可与团队共享组件
                                - 🎨 根据需求自定义
                                - 🚀 动态扩展功能
                                
                                ### 插件分类
                                - **布局**：影响页面结构的组件
                                - **内容**：文字、标注、引用等
                                - **交互**：需要用户交互的组件（仅 HTML）
                                - **媒体**：图片、视频、相册
                                - **数据**：图表、表格、分析
                                """)
                            else:
                                st.markdown("""
                                ## What are Plugins?
                            
                            Plugins allow you to create custom markdown components that extend MarkPolish Studio's functionality.
                            
                            ### Benefits
                            - ✨ Add new components without modifying core code
                            - 🔄 Share components with your team
                            - 🎨 Customize for your specific needs
                            - 🚀 Extend functionality dynamically
                            
                            ### Plugin Categories
                            - **Layout**: Components that affect page structure
                            - **Content**: Text, callouts, quotes, etc.
                            - **Interactive**: Components with user interaction (HTML only)
                            - **Media**: Images, videos, galleries
                            - **Data**: Charts, tables, analytics
                            """)
                        
                        with doc_tabs[1]:
                            if is_zh:
                                st.markdown("""
                                ## 创建插件
                                
                                ### 第一步：复制示例
                                1. 进入 `plugins/` 文件夹
                                2. 复制 `example_callout.py` 作为模板
                                3. 重命名为你的插件名（如 `my_component.py`）
                                
                                ### 第二步：定义元数据
                                ```python
                                PLUGIN_METADATA = {
                                    "name": "my_component",
                                    "syntax": r'(?is):::\s*mycomponent\\n(.*?)\\n:::',
                                    "description": "组件功能描述",
                                    "category": "Content",
                                    "compatibility": {
                                        "wechat": True,  # 是否支持微信？
                                        "html": True     # 是否支持 HTML？
                                    },
                                    "insertion_tool": "::: mycomponent\\n内容\\n:::"
                                }
                                ```
                                
                                ### 第三步：实现渲染函数
                                ```python
                                def render(match, styles, mode="wechat"):
                                    content = match.group(1)
                                    # 在这里构建 HTML
                                    return f'<div>{content}</div>'
                                ```
                                
                                ### 第四步：测试
                                1. 保存插件文件
                                2. 点击插件区域的"🔄 刷新"
                                3. 你的组件将出现在组件列表中
                                """)
                            else:
                                st.markdown("""
                                ## Creating a Plugin
                            
                            ### Step 1: Copy the Example
                            1. Go to the `plugins/` folder
                            2. Copy `example_callout.py` as a template
                            3. Rename it to your plugin name (e.g., `my_component.py`)
                            
                            ### Step 2: Define Metadata
                            ```python
                            PLUGIN_METADATA = {
                                "name": "my_component",
                                "syntax": r'(?is):::\s*mycomponent\\n(.*?)\\n:::',
                                "description": "What your component does",
                                "category": "Content",
                                "compatibility": {
                                    "wechat": True,  # Works in WeChat?
                                    "html": True     # Works in HTML?
                                },
                                "insertion_tool": "::: mycomponent\\nYour content\\n:::"
                            }
                            ```
                            
                            ### Step 3: Implement Render Function
                            ```python
                            def render(match, styles, mode="wechat"):
                                content = match.group(1)
                                # Build your HTML here
                                return f'<div>{content}</div>'
                            ```
                            
                            ### Step 4: Test
                            1. Save your plugin file
                            2. Click "🔄 Reload Plugins" in the Plugins section
                            3. Your component will appear in the component list
                            """)
                        
                        with doc_tabs[2]:
                            if is_zh:
                                st.markdown("""
                                ## 示例插件
                            
                                ### 简单标注
                            ```python
                            PLUGIN_METADATA = {
                                "name": "callout",
                                "syntax": r':::\s*callout\\n(.*?)\\n:::',
                                "compatibility": {"wechat": True, "html": True}
                            }
                            
                            def render(match, styles, mode):
                                content = match.group(1)
                                return f'<div style="border-left: 4px solid {styles["primary"]}; padding: 10px;">{content}</div>'
                            ```
                                """)
                            else:
                                st.markdown("""
                                ## Example Plugins
                            
                                ### Simple Callout
                            ```python
                            PLUGIN_METADATA = {
                                    "name": "callout",
                                    "syntax": r':::\s*callout\\n(.*?)\\n:::',
                                    "compatibility": {"wechat": True, "html": True}
                            }
                            
                            def render(match, styles, mode):
                                    content = match.group(1)
                                    return f'<div style="border-left: 4px solid {styles["primary"]}; padding: 10px;">{content}</div>'
                            ```
                            """)
                        
                        with doc_tabs[3]:
                            if is_zh:
                                st.markdown("""
                                ## 微信兼容性指南
                                
                                ### ✅ 微信支持的功能
                                - 基础 HTML 标签（div, span, p, h1-h6, img, a）
                                - 内联 CSS（颜色、字体、基础布局）
                                - 静态图片（base64 或托管 URL）
                                - 简单布局（flexbox、基础定位）
                                
                                ### ❌ 微信不支持的功能
                                - JavaScript（无交互组件）
                                - 高级 CSS（动画、变换、滤镜）
                                - 外部资源（字体、脚本）
                                - iframe
                                - 复杂 SVG 动画
                                
                                ### 最佳实践
                                1. **在微信模式下测试** 后再标记为兼容
                                2. **使用内联样式** 而非 class
                                3. **避免 JavaScript** - 使用纯 CSS 方案
                                4. **保持简单** - 微信对 CSS 支持有限
                                5. **提供降级方案** - 组件不可用时显示提示
                                """)
                            else:
                                st.markdown("""
                                ## WeChat Compatibility Guide
                            
                            ### ✅ What Works in WeChat
                            - Basic HTML tags (div, span, p, h1-h6, img, a)
                            - Inline CSS (colors, fonts, basic layout)
                            - Static images (base64 or hosted URLs)
                            - Simple layouts (flexbox, basic positioning)
                            
                            ### ❌ What Doesn't Work
                            - JavaScript (no interactive components)
                            - Advanced CSS (animations, transforms, filters)
                            - External resources (fonts, scripts)
                            - iframes
                            - Complex SVG animations
                            
                            ### Best Practices
                            1. **Test in WeChat mode** before marking as compatible
                            2. **Use inline styles** instead of classes
                            3. **Avoid JavaScript** - use CSS-only solutions
                            4. **Keep it simple** - WeChat has limited CSS support
                            5. **Provide fallbacks** - show a message if component can't work
                                """)
                        
                        close_text = "❌ 关闭文档" if is_zh else "❌ Close Documentation"
                        if st.button(close_text, key="close_plugin_docs", use_container_width=True):
                            st.session_state.show_plugin_docs = False
                            st.rerun()
                        
                except Exception as e:
                    st.toast(f"❌ {get_text('toast_plugin_error').format(error=e)}", icon="❌")
                    if ErrorHandler:
                        ErrorHandler.log_error("plugin_ui", e)
        
        # 6. IMAGES & ASSETS (Grouped)
        images_expanded = st.session_state.sidebar_expanded.get("image_assets", False)
        with st.expander(f"🖼️ {get_text('image_assets')}", expanded=images_expanded):
            
            # When daily limit was reached during preview/PDF, switch provider to Picsum (Stock) and toast
            limit_reached = st.session_state.pop("ai_image_limit_reached", None)
            if limit_reached:
                st.session_state.img_provider = "Picsum (Stock)"
                st.session_state["img_provider_select"] = "Picsum (Stock)"
                st.session_state.last_preview_content_hash = None
                st.session_state["ai_image_limit_show_toast"] = (limit_reached, "Picsum (Stock)")
                st.rerun()
            # Show toast on the run after we switched (so it survives rerun)
            toast_data = st.session_state.pop("ai_image_limit_show_toast", None)
            if toast_data:
                prev_provider, fallback_label = toast_data
                st.toast(get_text("ai_image_limit_switched").format(provider=prev_provider, fallback=fallback_label), icon="⚠️")
            
            # Function to handle image provider change and re-render
            def on_image_provider_change():
                new_provider = st.session_state.get("img_provider_select")
                old_provider = st.session_state.get("img_provider", "ModelScope (AI)")
                st.session_state.img_provider = new_provider
                
                # Only force re-render if the provider actually changed
                if new_provider != old_provider:
                    # Force preview re-render by updating content hash
                    if "content" in st.session_state:
                        st.session_state.last_preview_content_hash = None
                    # Also clear any cached preview
                    if PerformanceOptimizer and st.session_state.get("performance_optimizer"):
                        st.session_state.performance_optimizer.preview_cache = {}
            
            img_provider = st.selectbox(
                get_text("image_source"),
                ["ModelScope (AI)", "Z-Image-Turbo (AI)", "Picsum (Stock)", "Placeholder (Text)",
                 "Gradient (Blue)", "Gradient (Purple)", "Gradient (Sunset)",
                 "Gradient (Ocean)", "Gradient (Forest)", "Gradient (Aurora)",
                 "Gradient (Fire)", "Gradient (Midnight)",
                 "Pattern (Dots)", "Pattern (Lines)"],
                help=get_text("image_source_help"),
                key="img_provider_select",
                on_change=on_image_provider_change
            )
            
            # Daily quota: show immediately below image source when ModelScope or Z-Image-Turbo is selected
            # Prefer session state (updated when we increment) so count updates right after AI generation
            if img_provider in ("ModelScope (AI)", "Z-Image-Turbo (AI)"):
                try:
                    from ai_image_usage import get_remaining, get_limit
                    remaining = st.session_state.get("ai_image_quota_remaining", {}).get(img_provider)
                    if remaining is None:
                        remaining = get_remaining(img_provider)
                        if remaining is not None:
                            st.session_state.setdefault("ai_image_quota_remaining", {})[img_provider] = remaining
                    limit = get_limit(img_provider)
                    r = remaining if remaining is not None else "--"
                    l = limit if limit else (50 if img_provider == "ModelScope (AI)" else 10)
                    st.caption("📊 " + get_text("ai_image_quota").format(remaining=r, limit=l))
                except Exception:
                    st.caption("📊 " + get_text("ai_image_quota").format(remaining="--", limit=50 if img_provider == "ModelScope (AI)" else 10))
            
            # Update session state if changed (for backward compatibility)
            if st.session_state.get("img_provider") != img_provider:
                st.session_state.img_provider = img_provider
            
            # Warn when ModelScope (魔搭) is selected but API key is missing or module not found
            if img_provider == "ModelScope (AI)":
                _load_env()  # ensure .env is loaded before key check
                try:
                    from z_image import get_modelscope_api_key
                    key = get_modelscope_api_key() or os.getenv("MODELSCOPE_API_KEY") or os.getenv("MODELSCOPE_SDK_TOKEN")
                except ImportError:
                    st.error("AI image module (z_image.py) not found. Add z_image.py to the project folder and restart.")
                    key = None
                if key is not None and not (key and str(key).strip()):
                    st.warning("Set MODELSCOPE_API_KEY in Secrets (Cloud) or .env (local) to use ModelScope (魔搭).")
            # Warn when Z-Image-Turbo is selected but API key is missing or module not found
            if img_provider == "Z-Image-Turbo (AI)":
                _load_env()
                try:
                    from z_image import get_dashscope_api_key
                    key = get_dashscope_api_key() or os.getenv("DASHSCOPE_API_KEY")
                except ImportError:
                    st.error("AI image module (z_image.py) not found. Add z_image.py to the project folder and restart.")
                    key = None
                if key is not None and not (key and str(key).strip()):
                    st.warning("Set DASHSCOPE_API_KEY in Secrets (Cloud) or .env (local) to use Z-Image-Turbo.")

            # Aspect ratio for AI images and for Picsum / Placeholder
            if img_provider in ("Z-Image-Turbo (AI)", "ModelScope (AI)", "Picsum (Stock)", "Placeholder (Text)"):
                img_ratio = st.selectbox(
                    get_text("image_ratio"),
                    options=["1:1", "16:9", "9:16"],
                    index=0,
                    help=get_text("image_ratio_help"),
                    key="img_ratio_select",
                )
                if "img_ratio" not in st.session_state or st.session_state.get("img_ratio") != img_ratio:
                    st.session_state.img_ratio = img_ratio
            else:
                img_ratio = st.session_state.get("img_ratio", "1:1")

            # Refresh AI images: clear cache so [IMG: prompt] re-generates on next preview
            if img_provider in ("Z-Image-Turbo (AI)", "ModelScope (AI)"):
                if st.button("🔄 Refresh AI images", help="Clear cache and re-generate all [IMG: ...] images on next preview", use_container_width=True, key="refresh_ai_images"):
                    if "ai_image_cache" in st.session_state:
                        st.session_state["ai_image_cache"] = {}
                    st.session_state["last_preview_content_hash"] = None
                    if st.session_state.get("performance_optimizer"):
                        st.session_state.performance_optimizer.preview_cache = {}
                    st.toast("AI image cache cleared. Preview again to re-generate.", icon="✅")
            
            # Image Library (nested in Images & Assets)
            st.markdown(f"**📚 {get_text('image_library')}**")
            library_images = get_image_library()
            if library_images:
                st.caption(get_text("images_in_library").format(count=len(library_images)))
                
                # Display images in grid
                cols_per_row = 3
                for i in range(0, len(library_images), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j, col in enumerate(cols):
                        if i + j < len(library_images):
                            img_info = library_images[i + j]
                            img_data = load_image_from_library(img_info["filename"])
                            
                            if img_data:
                                # Display thumbnail
                                col.image(img_data, use_container_width=True)
                                
                                # Image name and actions
                                display_name = img_info.get("original_name", img_info["filename"])[:20]
                                col.caption(display_name)
                                
                                # Insert and delete buttons
                                btn_col1, btn_col2 = col.columns(2)
                                with btn_col1:
                                    if st.button("➕", key=f"insert_{img_info['filename']}", help="Insert into editor"):
                                        if "content" not in st.session_state:
                                            st.session_state.content = ""
                                        # Use original name for reference
                                        ref_name = img_info.get("original_name", img_info["filename"])
                                        # Load into session state if not already there
                                        if "local_images" not in st.session_state:
                                            st.session_state.local_images = {}
                                        st.session_state.local_images[ref_name] = img_data
                                        st.session_state.content += f"\n[LOCAL: {ref_name}]\n"
                                        st.rerun()
                                with btn_col2:
                                    if st.button("🗑️", key=f"del_{img_info['filename']}", help="Delete"):
                                        if delete_image_from_library(img_info["filename"]):
                                            st.toast(get_text("toast_deleted"), icon="✅")
                                            st.rerun()
            else:
                st.toast(get_text("no_images_library"), icon="ℹ️")
        
            
            # Upload new image
            st.markdown(f"**📤 {get_text('upload_image')}**")
            uploaded_img = st.file_uploader(
                get_text("choose_image_file"), 
                type=['png', 'jpg', 'jpeg', 'gif'], 
                label_visibility="collapsed",
                help=get_text("file_upload_limit")
            )
            # Inject JavaScript to replace Streamlit's hardcoded file uploader text
            drag_drop_text = get_text("drag_drop").replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            browse_files_text = get_text("browse_files").replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            file_upload_limit_text = get_text("file_upload_limit").replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            # Custom visible Chinese labels (always rendered) — we hide Streamlit's built-ins
            st.markdown(f"""
            <script>
            (function() {{
                const dragDropText = '{drag_drop_text}';
                const browseFilesText = '{browse_files_text}';
                const fileLimitText = '{file_upload_limit_text}';
                
                function replaceFileUploaderText() {{
                    // Method 1: Target specific "Browse files" button by testid
                    const browseButtons = document.querySelectorAll('[data-testid="stBaseButton-secondary"]');
                    browseButtons.forEach(btn => {{
                        if (btn.textContent && btn.textContent.trim() === 'Browse files') {{
                            btn.textContent = browseFilesText;
                            // Also replace in child text nodes
                            const walker = document.createTreeWalker(btn, NodeFilter.SHOW_TEXT, null, false);
                            let textNode;
                            while (textNode = walker.nextNode()) {{
                                if (textNode.textContent.includes('Browse files')) {{
                                    textNode.textContent = browseFilesText;
                                }}
                            }}
                        }}
                    }});
                    
                    // Method 2: Find all buttons and replace "Browse files" text
                    const allButtons = document.querySelectorAll('button');
                    allButtons.forEach(btn => {{
                        if (btn.textContent && btn.textContent.trim() === 'Browse files') {{
                            btn.textContent = browseFilesText;
                        }}
                    }});
                    
                    // Method 3: Find all file uploader areas
                    const uploadAreas = document.querySelectorAll('[data-testid="stFileUploader"]');
                    uploadAreas.forEach(uploadArea => {{
                        if (!uploadArea) return;
                    
                    // Force-set button and label texts (avoid relying on original English)
                    const buttons = uploadArea.querySelectorAll('button');
                    buttons.forEach(btn => {{
                        if (btn.textContent !== browseFilesText) {{
                            btn.textContent = browseFilesText;
                        }}
                    }});
                    
                    const labelNodes = uploadArea.querySelectorAll('span, p, div');
                    labelNodes.forEach(el => {{
                        const txt = (el.textContent || '').trim();
                        if (txt.startsWith('Drag and drop') || txt === dragDropText) {{
                            el.textContent = '';
                        }}
                        if (/^Limit 200MB per file/i.test(txt) || txt === fileLimitText) {{
                            el.textContent = '';
                        }}
                    }});
                        
                        // Find and replace all text nodes recursively
                        function replaceTextInNode(node) {{
                            if (node.nodeType === Node.TEXT_NODE) {{
                                if (node.textContent.includes('Drag and drop file here')) {{
                                node.textContent = '';
                                }}
                                if (node.textContent.includes('Browse files')) {{
                                node.textContent = browseFilesText;
                                }}
                                if (node.textContent.includes('Limit 200MB per file')) {{
                                node.textContent = '';
                                }}
                            }} else if (node.nodeType === Node.ELEMENT_NODE) {{
                                // Also check element textContent
                                if (node.textContent && node.textContent.trim()) {{
                                    if (node.textContent.includes('Drag and drop file here')) {{
                                        const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT, null, false);
                                        let textNode;
                                        while (textNode = walker.nextNode()) {{
                                            if (textNode.textContent.includes('Drag and drop file here')) {{
                                            textNode.textContent = '';
                                            }}
                                        }}
                                    }}
                                    if (node.textContent.includes('Browse files')) {{
                                        const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT, null, false);
                                        let textNode;
                                        while (textNode = walker.nextNode()) {{
                                            if (textNode.textContent.includes('Browse files')) {{
                                            textNode.textContent = browseFilesText;
                                            }}
                                        }}
                                    }}
                                    if (node.textContent.includes('Limit 200MB per file')) {{
                                        const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT, null, false);
                                        let textNode;
                                        while (textNode = walker.nextNode()) {{
                                            if (textNode.textContent.includes('Limit 200MB per file')) {{
                                            textNode.textContent = '';
                                            }}
                                        }}
                                    }}
                                }}
                                
                                // Recursively process child nodes
                                Array.from(node.childNodes).forEach(child => replaceTextInNode(child));
                            }}
                        }}
                        
                        // Process the entire upload area
                        replaceTextInNode(uploadArea);
                    }});
                }}
                
                // Use MutationObserver to watch for DOM changes - observe entire body
                const observer = new MutationObserver(function(mutations) {{
                    let shouldRun = false;
                    mutations.forEach(mutation => {{
                        if (mutation.type === 'childList' || mutation.type === 'characterData') {{
                            shouldRun = true;
                        }}
                    }});
                    if (shouldRun) {{
                        setTimeout(replaceFileUploaderText, 10);
                    }}
                }});
                
                // Observe document body for all changes (more aggressive)
                observer.observe(document.body, {{ 
                    childList: true, 
                    subtree: true, 
                    characterData: true,
                    attributes: false
                }});
                
                // Also observe all upload areas individually
                document.querySelectorAll('[data-testid="stFileUploader"]').forEach(uploadArea => {{
                    observer.observe(uploadArea, {{ 
                        childList: true, 
                        subtree: true, 
                        characterData: true,
                        attributes: false
                    }});
                }});
                
                // Run immediately and repeatedly with more delays
                replaceFileUploaderText();
                [0, 50, 100, 200, 300, 500, 1000, 2000, 3000, 5000].forEach(delay => {{
                    setTimeout(replaceFileUploaderText, delay);
                }});
                
                // Also run after Streamlit reruns
                if (window.parent && window.parent.postMessage) {{
                    const originalPostMessage = window.parent.postMessage;
                    window.parent.postMessage = function(...args) {{
                        originalPostMessage.apply(this, args);
                        setTimeout(replaceFileUploaderText, 100);
                    }};
                }}
                
                // Run on every frame for a longer period after load
                let frameCount = 0;
                function frameCheck() {{
                    if (frameCount < 300) {{ // Check for ~5 seconds at 60fps
                        replaceFileUploaderText();
                        frameCount++;
                        requestAnimationFrame(frameCheck);
                    }}
                }}
                requestAnimationFrame(frameCheck);
                
                // Also add a continuous interval for 10 seconds
                let intervalCount = 0;
                const longInterval = setInterval(() => {{
                    replaceFileUploaderText();
                    intervalCount++;
                    if (intervalCount > 100) {{ // 10 seconds at 100ms intervals
                        clearInterval(longInterval);
                    }}
                }}, 100);
            }})();
            </script>
            """, unsafe_allow_html=True)
        if uploaded_img:
            save_to_lib = st.checkbox(get_text("save_to_image_library"), value=True, key="save_to_lib")
            shortcode, error = process_image(uploaded_img, save_to_library=save_to_lib)
            if error:
                if ErrorHandler:
                    ErrorHandler.show_error_with_details(error)
                else:
                    st.toast(error, icon="❌")
            elif shortcode:
                st.toast(get_text("image_uploaded"), icon="✅")
                st.code(shortcode, language="text")
                if save_to_lib:
                    st.toast(get_text("image_saved_to_library"), icon="ℹ️")
            else:
                st.toast(shortcode if shortcode else "Upload failed", icon="❌")

    # Restore auto-save prompt
    if st.session_state.get("show_restore_prompt", False):
        restore_content = st.session_state.get("restore_content", "")
        restore_time = st.session_state.get("restore_time", 0)
        if restore_time:
            try:
                if hasattr(restore_time, "timestamp"):
                    ts_val = restore_time.timestamp()
                else:
                    ts_val = float(restore_time)
                time_str = datetime.fromtimestamp(ts_val).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                time_str = "recently"
        else:
            time_str = "recently"
        
        with st.container():
            st.toast(f"📋 Auto-saved content found from {time_str}. Restore?", icon="ℹ️")
            col_restore, col_dismiss = st.columns(2)
            with col_restore:
                if st.button("✅ Restore", use_container_width=True):
                    st.session_state.content = restore_content
                    st.session_state.reset_editor = True  # Flag to reset editor on rerun
                    st.session_state.show_restore_prompt = False
                    st.rerun()
            with col_dismiss:
                if st.button("❌ Dismiss", use_container_width=True, key="dismiss_restore"):
                    st.session_state.show_restore_prompt = False
                    st.session_state.restore_prompt_dismissed = True  # Mark as dismissed to prevent re-showing
                    # Clear restore data to prevent it from showing again
                    if "restore_content" in st.session_state:
                        del st.session_state.restore_content
                    if "restore_time" in st.session_state:
                        del st.session_state.restore_time
                    st.rerun()

    col1, col2 = st.columns([1, 1])

    with col1:
        # Editor Column
        current_content = st.session_state.get("content", "")
        
        # Initialize editor_content if it doesn't exist or if content was updated externally
        if "editor_content" not in st.session_state:
            st.session_state.editor_content = current_content
        
        st.subheader(f"✒️ {get_text('editor')}")

        # Inline markdown syntax help
        with st.expander(f"📖 {get_text('markdown_help')}", expanded=False):
            help_col1, help_col2 = st.columns(2)
            
            with help_col1:
                st.markdown("**Basic Formatting**")
                st.code("""# H1 Header
## H2 Header
### H3 Header

**bold text**
*italic text*
~~strikethrough~~

`inline code`

[Link text](https://example.com)
![Image alt](image.jpg)""", language="markdown")
                
                st.markdown("**Lists**")
                st.code("""- Unordered item
- Another item
  - Nested item

1. Ordered item
2. Another item
   1. Nested item""", language="markdown")
            
            with help_col2:
                st.markdown("**Advanced**")
                st.code("""> Blockquote text
> Can span multiple lines

```python
# Code block
def hello():
    print("Hello")
```

| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |""", language="markdown")
                
                st.markdown("**Special Components**")
                st.code("""::: hero
# Title
Subtitle
:::

::: center
Centered text or paragraph
:::

::: col-2
Left column
--split--
Right column
:::

[badge: NEW]
[Button Label](https://link.com)
[IMG: describe your image]

# Responsive video (raw HTML)
<video src="https://example.com/video.mp4" poster="" controls style="width:100%;height:auto;display:block;"></video>

# Video component (responsive)
::: video src="https://example.com/video.mp4" poster="" caption="" autoplay=false muted=false loop=false :::""", language="markdown")
            
            st.caption(f"💡 {get_text('syntax_tip')}")
        
        # Markdown validation (optional, shown if enabled)
        if st.session_state.get("show_validation", False) and current_content:
            if ErrorHandler:
                is_valid, issues = ErrorHandler.validate_markdown_syntax(current_content)
                if not is_valid:
                    with st.expander("⚠️ Markdown Validation Issues", expanded=True):
                        for issue in issues:
                            st.toast(issue, icon="⚠️")
                        st.caption("💡 These issues may affect rendering. Fix them for best results.")

        # Initialize undo stack with current content if empty
        if not st.session_state.undo_stack and current_content:
            st.session_state.undo_stack = [current_content]
        
        # Sync editor_content from content if needed (before widget creation)
        # This handles cases where content was updated externally (undo/redo, load file, etc.)
        if st.session_state.get("reset_editor", False):
            # Delete editor_content to force it to sync from content
            if "editor_content" in st.session_state:
                del st.session_state.editor_content
            st.session_state.reset_editor = False
        
        # Initialize editor_content from content if it doesn't exist
        if "editor_content" not in st.session_state:
            st.session_state.editor_content = current_content
        
        # Apply any pending snippet insert before rendering the textarea
        if st.session_state.get("pending_insert"):
            base_text = st.session_state.get("editor_content") or st.session_state.get("content", "")
            st.session_state.editor_content = base_text + st.session_state.pending_insert
            st.session_state.pending_insert = None
        
        # Apply component insertion before rendering the textarea (BEFORE widget creation!)
        if st.session_state.get("pending_component_insert"):
            import json
            snippet = st.session_state.pending_component_insert
            
            # Get current editor content
            current_content = st.session_state.get("editor_content", "")
            
            # Try to get cursor position from session state or query params
            cursor_start = st.session_state.get("_cursor_start")
            cursor_end = st.session_state.get("_cursor_end")
            
            # Fallback: try to get from query params
            if cursor_start is None or cursor_end is None:
                query_params = st.query_params
                if cursor_start is None:
                    cursor_start = query_params.get("_cursor_start", None)
                    if cursor_start is not None:
                        try:
                            cursor_start = int(cursor_start)
                        except:
                            cursor_start = None
                if cursor_end is None:
                    cursor_end = query_params.get("_cursor_end", None)
                    if cursor_end is not None:
                        try:
                            cursor_end = int(cursor_end)
                        except:
                            cursor_end = None
            
            # Default to end of content if no cursor position
            if cursor_start is None:
                cursor_start = len(current_content)
            if cursor_end is None:
                cursor_end = len(current_content)
            
            # Insert component at cursor position
            pos = max(cursor_start, cursor_end)
            new_content = current_content[:pos] + "\n\n" + snippet + "\n" + current_content[pos:]
            
            # Update session state BEFORE widget creation (this is the key!)
            # Delete first to avoid "cannot modify after widget instantiated" error
            if "editor_content" in st.session_state:
                del st.session_state.editor_content
            st.session_state.editor_content = new_content
            st.session_state.content = new_content
            
            # Update cursor position after insertion
            new_pos = pos + len("\n\n" + snippet + "\n")
            st.session_state._cursor_start = new_pos
            st.session_state._cursor_end = new_pos
            st.session_state.js_insertion_completed = True
            
            # Clear the flag
            st.session_state.pending_component_insert = None

        # Text area outside form to allow content change detection
        # NOTE: We don't pass value= parameter to avoid Streamlit warning about
        # both setting session state and passing value. The key="editor_content"
        # ensures Streamlit reads from session_state.editor_content automatically.
        is_readonly = False
        txt = st.text_area(
            "MD", 
            value=None,  # Let Streamlit read from session_state via key
            height=600, 
            label_visibility="collapsed",
            key="editor_content",
            disabled=is_readonly
        )
        
        # CRITICAL: After textarea renders, check if user changed it
        # If txt differs from session_state, update session_state (this handles JS insertions)
        if txt != st.session_state.get("editor_content"):
            st.session_state.editor_content = txt
            st.session_state.content = txt
            if st.session_state.get("js_insertion_completed"):
                st.session_state.js_insertion_completed = False
        
        # Simple cursor tracker - stores position in data attributes
        import streamlit.components.v1 as components
        cursor_tracker_js = """
        <script>
        (function() {
            const mainWindow = window.parent !== window ? window.parent : window;
            const mainDoc = mainWindow.document;
            
            function findEditorTextarea() {
                const textareas = mainDoc.querySelectorAll('textarea');
                for (const ta of textareas) {
                    const h = parseInt(getComputedStyle(ta).height);
                    if (h > 400) return ta;
                }
                let maxH = 0, candidate = null;
                for (const ta of textareas) {
                    const h = parseInt(getComputedStyle(ta).height);
                    if (h > maxH) { maxH = h; candidate = ta; }
                }
                return maxH > 200 ? candidate : null;
            }
            
            function updateCursor() {
                const textarea = findEditorTextarea();
                if (!textarea) return;
                const start = textarea.selectionStart || 0;
                const end = textarea.selectionEnd || 0;
                textarea.setAttribute('data-cursor-start', start);
                textarea.setAttribute('data-cursor-end', end);
                // Persist cursor position to URL so Python can read it on rerun
                try {
                    const url = new URL(mainWindow.location.href);
                    url.searchParams.set('_cursor_start', start);
                    url.searchParams.set('_cursor_end', end);
                    mainWindow.history.replaceState({}, '', url.toString());
                } catch (e) {
                    console.warn('Could not update cursor params:', e);
                }
            }
            
            function attachTracker() {
                const textarea = findEditorTextarea();
                if (!textarea) {
                    setTimeout(attachTracker, 200);
                    return;
                }
                ['click', 'keyup', 'mouseup', 'focus', 'input'].forEach(ev => {
                    textarea.addEventListener(ev, updateCursor, true);
                });
                textarea.addEventListener('blur', function() {
                    updateCursor();
                }, true);
                updateCursor();
            }
            setTimeout(attachTracker, 300);
        })();
        </script>
        """
        components.html(cursor_tracker_js, height=0)
        
        # Position cursor after component insertion (if insertion happened)
        if st.session_state.get("js_insertion_completed"):
            import json
            new_pos = st.session_state.get("_cursor_start", 0)
            
            # Inject JavaScript to position cursor in the textarea (UI update only)
            cursor_js = f"""
            <script>
            (function() {{
                try {{
                    const mainWindow = window.parent !== window ? window.parent : window;
                    const mainDoc = mainWindow.document;
                    
                    function findEditorTextarea() {{
                        const textareas = mainDoc.querySelectorAll('textarea');
                        for (const ta of textareas) {{
                            const h = parseInt(getComputedStyle(ta).height);
                            if (h > 400) return ta;
                        }}
                        let maxH = 0, candidate = null;
                        for (const ta of textareas) {{
                            const h = parseInt(getComputedStyle(ta).height);
                            if (h > maxH) {{ maxH = h; candidate = ta; }}
                        }}
                        return maxH > 200 ? candidate : null;
                    }}
                    
                    function positionCursor() {{
                        const textarea = findEditorTextarea();
                        if (!textarea) {{
                            setTimeout(positionCursor, 50);
                            return;
                        }}
                        
                        const newPos = {new_pos};
                        
                        // Position cursor
                        try {{
                            textarea.setSelectionRange(newPos, newPos);
                            textarea.focus();
                            textarea.setAttribute('data-cursor-start', newPos);
                            textarea.setAttribute('data-cursor-end', newPos);
                            console.log('✅ Cursor positioned at', newPos);
                        }} catch(e) {{
                            console.warn('Could not position cursor:', e);
                        }}
                    }}
                    
                    setTimeout(positionCursor, 150);
                }} catch(e) {{
                    console.warn('Cursor positioning error:', e);
                }}
            }})();
            </script>
            """
            components.html(cursor_js, height=0)
            st.session_state.js_insertion_completed = False
        
        # --- Editor Status Bar ---
        editor_text = st.session_state.get("editor_content", "")
        
        # Calculate stats
        word_count = len(editor_text.split()) if editor_text.strip() else 0
        char_count = len(editor_text)
        # Reading time: ~200 words per minute for Chinese, ~250 for English
        read_minutes = max(1, round(word_count / 200)) if word_count > 0 else 0
        
        # Auto-save status
        save_status = st.session_state.get("auto_save_status", "saved")
        if save_status == "saving":
            save_icon = f"💾 {get_text('saving')}"
        elif save_status == "error":
            save_icon = f"⚠️ {get_text('save_error')}"
        else:
            save_icon = f"✓ {get_text('saved')}"
        
        # Editor status (no wrapper div)
        status_col1, status_col2, status_col3 = st.columns([2, 2, 1])
        with status_col1:
            st.caption(f"📝 {word_count:,} {get_text('words')} · {char_count:,} {get_text('chars')}")
        with status_col2:
            st.caption(f"⏱️ ~{read_minutes} {get_text('min_read')}")
        with status_col3:
            st.caption(save_icon)
        
        # Check for content changes (for auto-save and undo stack)
        if "editor_content" in st.session_state:
            editor_txt = st.session_state.editor_content
            # Check if content actually changed
            content_hash = hash(editor_txt)
            if content_hash != st.session_state.get("last_content_hash"):
                # Content changed - update session state
                st.session_state.content = editor_txt
                
                # Push to undo stack (only if content actually changed)
                if editor_txt:
                    st.session_state.undo_stack = push_to_undo_stack(
                        editor_txt, 
                        st.session_state.undo_stack
                    )
                    # Clear redo stack on new edit
                    st.session_state.redo_stack = []
                
                st.session_state.last_content_hash = content_hash
                # Trigger debounced auto-save
                st.session_state.pending_autosave = True
                st.session_state.autosave_timer = time.time()
                st.session_state.auto_save_status = "saving"
        
        # Process pending auto-save (debounced - 2 seconds after last change)
        if st.session_state.get("pending_autosave", False):
            # Initialize timer if not set
            if "autosave_timer" not in st.session_state or st.session_state.autosave_timer is None:
                st.session_state.autosave_timer = time.time()
            
            elapsed = time.time() - st.session_state.autosave_timer
            if elapsed >= 2:  # 2 second debounce
                content_to_save = st.session_state.get("editor_content", current_content)
                if content_to_save and st.session_state.auto_save_enabled:
                    success, result = auto_save(content_to_save, st.session_state.current_project_name)
                    if success:
                        st.session_state.last_auto_save_time = result
                        st.session_state.auto_save_status = "saved"
                    else:
                        st.session_state.auto_save_status = "error"
                st.session_state.pending_autosave = False
                st.session_state.autosave_timer = None
        
        # Check for periodic auto-save (every 30 seconds)
        current_time = time.time()
        time_since_last_save = current_time - st.session_state.last_auto_save_time
        if time_since_last_save > 30 and not st.session_state.get("pending_autosave", False):
            content_to_save = st.session_state.get("editor_content", current_content)
            if st.session_state.auto_save_enabled and content_to_save:
                success, result = auto_save(content_to_save, st.session_state.current_project_name)
                if success:
                    st.session_state.last_auto_save_time = result
                    st.session_state.auto_save_status = "saved"
                else:
                    st.session_state.auto_save_status = "error"
        
        # Handle keyboard actions
        keyboard_action = st.session_state.get("keyboard_action")
        if keyboard_action:
            content_for_action = st.session_state.get("editor_content", current_content)
            if keyboard_action == "save":
                if st.session_state.current_project_name:
                    result = save_project(st.session_state.current_project_name, content_for_action)
                    if result.startswith("✅"):
                        st.toast(get_text("toast_saved"), icon="✅")
                    else:
                        if ErrorHandler:
                            ErrorHandler.show_error_with_details(result)
                        else:
                            st.toast(result, icon="❌")
                else:
                    success, result = auto_save(content_for_action, None)
                    if success:
                        st.session_state.last_auto_save_time = result
                        st.session_state.auto_save_status = "saved"
                        st.toast(get_text("toast_auto_saved"), icon="💾")
                st.session_state.keyboard_action = None
            elif keyboard_action == "undo":
                if st.session_state.undo_stack and len(st.session_state.undo_stack) > 1:
                    new_content = undo_action(
                        st.session_state.undo_stack,
                        st.session_state.redo_stack,
                        content_for_action
                    )
                    st.session_state.content = new_content
                    st.session_state.reset_editor = True  # Flag to reset editor on rerun
                    st.session_state.keyboard_action = None
                    st.rerun()
            elif keyboard_action == "redo":
                if st.session_state.redo_stack:
                    new_content = redo_action(
                        st.session_state.undo_stack,
                        st.session_state.redo_stack,
                        content_for_action
                    )
                    st.session_state.content = new_content
                    st.session_state.reset_editor = True  # Flag to reset editor on rerun
                    st.session_state.keyboard_action = None
                    st.rerun()
        
        # Keyboard shortcuts - use custom component if available
        if HAS_KEYBOARD_LISTENER:
            create_keyboard_listener()
        
        # Quick action buttons (keyboard shortcuts via buttons)
        kb_col1, kb_col2, kb_col3 = st.columns(3)
        with kb_col1:
            if st.button(
                f"💾 {get_text('quick_save')}",
                use_container_width=True,
                key="kb_save",
                help=f"{get_text('save_current')} • Shortcut: ⌘/Ctrl+S"
            ):
                content_to_save = st.session_state.get("editor_content", current_content)
                if st.session_state.current_project_name:
                    result = save_project(st.session_state.current_project_name, content_to_save)
                    if result.startswith("✅"):
                        st.toast(get_text("toast_saved"), icon="✅")
                    else:
                        if ErrorHandler:
                            ErrorHandler.show_error_with_details(result)
                        else:
                            st.toast(result, icon="❌")
                else:
                    success, result = auto_save(content_to_save, None)
                    if success:
                        st.session_state.last_auto_save_time = result
                        st.session_state.auto_save_status = "saved"
                        st.toast(get_text("toast_auto_saved"), icon="✅")
        with kb_col2:
            undo_disabled = not (st.session_state.undo_stack and len(st.session_state.undo_stack) > 1)
            if st.button(
                f"↶ {get_text('undo')}",
                use_container_width=True,
                key="kb_undo",
                disabled=undo_disabled,
                help=f"{get_text('undo_help')} • Shortcut: ⌘/Ctrl+Z"
            ):
                if not undo_disabled:
                    content_for_undo = st.session_state.get("editor_content", current_content)
                    new_content = undo_action(
                        st.session_state.undo_stack,
                        st.session_state.redo_stack,
                        content_for_undo
                    )
                    st.session_state.content = new_content
                    st.session_state.reset_editor = True  # Flag to reset editor on rerun
                    st.rerun()
        with kb_col3:
            redo_disabled = not st.session_state.redo_stack
            if st.button(
                f"↷ {get_text('redo')}",
                use_container_width=True,
                key="kb_redo",
                disabled=redo_disabled,
                help=f"{get_text('redo_help')} • Shortcut: ⌘/Ctrl+Shift+Z"
            ):
                if not redo_disabled:
                    content_for_redo = st.session_state.get("editor_content", current_content)
                    new_content = redo_action(
                        st.session_state.undo_stack,
                        st.session_state.redo_stack,
                        content_for_redo
                    )
                    st.session_state.content = new_content
                    st.session_state.reset_editor = True  # Flag to reset editor on rerun
                    st.rerun()

        # Real-time preview - no form needed!
        # Preview updates automatically as you type
        
        # Get current text from editor
        current_txt = st.session_state.get("editor_content", current_content)
        
        # Sync content to session state for preview
        if current_txt != st.session_state.get("content", ""):
            st.session_state.content = current_txt
        
        # Get AI config and content type from session state
        ai_cfg = st.session_state.get("ai_cfg", {"engine": "None", "key": "", "url": "", "model": ""})
        ai_content_type = st.session_state.get("ai_content_type", None)
        prev_engine = st.session_state.get("last_engine", "None")
        
        # Enhanced AI Actions
        if "ai_busy" not in st.session_state:
            st.session_state.ai_busy = False
        if "pending_ai_action" not in st.session_state:
            st.session_state.pending_ai_action = None
        if "last_ai_action_ts" not in st.session_state:
            st.session_state.last_ai_action_ts = 0.0
        if "last_ai_status" not in st.session_state:
            st.session_state.last_ai_status = get_text("ai_status_idle")
        if "last_ai_status_key" not in st.session_state:
            st.session_state.last_ai_status_key = "ai_status_idle"
        if "last_ai_status_action" not in st.session_state:
            st.session_state.last_ai_status_action = ""
        if "last_failed_ai_action" not in st.session_state:
            st.session_state.last_failed_ai_action = None
        if "last_titles_result" not in st.session_state:
            st.session_state.last_titles_result = ""
        # Initialize context_text if not present (fixes NameError)
        if "context_text" not in st.session_state:
            st.session_state.context_text = ""
        # Extract context_text for use in AI actions
        context_text = st.session_state.context_text
        MAX_AI_INPUT_CHARS = 8000

        def set_ai_status(key: str, action_label: str = ""):
            st.session_state.last_ai_status_key = key
            st.session_state.last_ai_status_action = action_label
            if key == "ai_status_last_action" and action_label:
                st.session_state.last_ai_status = get_text(key).format(action=action_label)
            else:
                st.session_state.last_ai_status = get_text(key)

        pending_ai_action = st.session_state.get("pending_ai_action")
        if st.session_state.ai_busy and pending_ai_action:
            current_txt = st.session_state.get("editor_content", current_content)

            if pending_ai_action == "generate_titles":
                if not current_txt:
                    st.toast(get_text("ai_input_required"))
                    st.session_state.pending_ai_action = None
                    st.session_state.ai_busy = False
                    st.session_state.last_ai_action_ts = time.time()
                    set_ai_status("ai_status_failed")
                else:
                    try:
                        with st.spinner(get_text("brainstorming_titles")):
                            titles, stat = run_ai(current_txt, "", ai_cfg, task_type="titles", content_type=ai_content_type)
                        
                        # Check if AI returned an error message
                        if stat.startswith("⚠️") or stat.startswith("❌"):
                            raise Exception(stat)
                        
                        # Store titles in session state for persistent display
                        st.session_state.generated_titles = titles
                        detected_lang = detect_language(current_txt) if current_txt else "English"
                        st.toast(get_text("detected_language").format(lang=detected_lang), icon="ℹ️")
                        
                        set_ai_status("ai_status_success")
                        st.session_state.last_failed_ai_action = None
                    except Exception as e:
                        error_msg = str(e)
                        st.toast(f"❌ {error_msg}", icon="❌")
                        set_ai_status("ai_status_failed")
                        st.session_state.last_failed_ai_action = {"name": "generate_titles", "require_text": True}
                        if ErrorHandler:
                            ErrorHandler.log_error("ai_titles", e, {"engine": ai_cfg.get('engine'), "model": ai_cfg.get('model')})
                    finally:
                        st.session_state.pending_ai_action = None
                        st.session_state.ai_busy = False

            elif pending_ai_action == "expand_content":
                if not current_txt:
                    st.toast(get_text("ai_input_required"))
                    st.session_state.pending_ai_action = None
                    st.session_state.ai_busy = False
                    st.session_state.last_ai_action_ts = time.time()
                    set_ai_status("ai_status_failed")
                else:
                    try:
                        st.session_state.undo_stack = push_to_undo_stack(
                            current_txt,
                            st.session_state.undo_stack
                        )
                        st.session_state.redo_stack = []

                        with st.spinner(get_text("expanding_content")):
                            res, msg = run_ai(current_txt, context_text, ai_cfg, task_type="expand", content_type=ai_content_type)
                            
                            # Check if AI returned an error message
                            if msg.startswith("⚠️") or msg.startswith("❌"):
                                raise Exception(msg)
                            
                            st.session_state.content = res
                            st.session_state.reset_editor = True  # Trigger editor reset
                            if res:
                                st.session_state.undo_stack = push_to_undo_stack(
                                    res,
                                    st.session_state.undo_stack
                                )
                            st.toast(f"✅ {get_text('toast_expand_applied').format(msg=msg)}")
                            time.sleep(0.5)
                        set_ai_status("ai_status_success")
                        st.session_state.last_failed_ai_action = None
                    except Exception as e:
                        error_msg = str(e)
                        st.toast(f"❌ {error_msg}", icon="❌")
                        set_ai_status("ai_status_failed")
                        st.session_state.last_failed_ai_action = {"name": "expand_content", "require_text": True}
                        # Log detailed error for debugging
                        if ErrorHandler:
                            ErrorHandler.log_error("ai_expand", e, {
                                "engine": ai_cfg.get('engine'), 
                                "model": ai_cfg.get('model'),
                                "url": ai_cfg.get('url'),
                                "content_length": len(current_txt) if current_txt else 0,
                                "context_length": len(context_text) if context_text else 0
                            })
                        # Debug: Show what we tried to send
                        st.error(f"Debug: Engine={ai_cfg.get('engine')}, Model={ai_cfg.get('model')}, URL={ai_cfg.get('url')}")
                    finally:
                        st.session_state.pending_ai_action = None
                        st.session_state.ai_busy = False

            elif pending_ai_action == "smart_format":
                if not current_txt:
                    st.toast(get_text("ai_input_required"))
                    st.session_state.pending_ai_action = None
                    st.session_state.ai_busy = False
                    st.session_state.last_ai_action_ts = time.time()
                    set_ai_status("ai_status_failed")
                else:
                    try:
                        st.session_state.undo_stack = push_to_undo_stack(
                            current_txt,
                            st.session_state.undo_stack
                        )
                        st.session_state.redo_stack = []
                    
                        available_plugins = []
                        if get_plugin_registry:
                            try:
                                registry = get_plugin_registry()
                                available_plugins = registry.get_plugins_by_category()
                            except Exception:
                                pass
                        
                        with st.spinner(get_text("formatting_content")):
                            res, msg = run_ai(current_txt, context_text, ai_cfg, task_type="format", 
                                              content_type=ai_content_type, available_plugins=available_plugins)
                            
                            # Check if AI returned an error message
                            if msg.startswith("⚠️") or msg.startswith("❌"):
                                raise Exception(msg)
                            
                            st.session_state.content = res
                            st.session_state.reset_editor = True  # Trigger editor reset
                            if res:
                                st.session_state.undo_stack = push_to_undo_stack(
                                    res,
                                    st.session_state.undo_stack
                                )
                            st.toast(msg)
                            time.sleep(0.5)
                        set_ai_status("ai_status_success")
                        st.session_state.last_failed_ai_action = None
                    except Exception as e:
                        error_msg = str(e)
                        st.toast(f"❌ {error_msg}", icon="❌")
                        set_ai_status("ai_status_failed")
                        st.session_state.last_failed_ai_action = {"name": "smart_format", "require_text": True}
                        if ErrorHandler:
                            ErrorHandler.log_error("ai_format", e, {
                                "engine": ai_cfg.get('engine'), 
                                "model": ai_cfg.get('model'),
                                "url": ai_cfg.get('url'),
                                "content_length": len(current_txt) if current_txt else 0
                            })
                        # Debug: Show what we tried to send
                        st.error(f"Debug: Engine={ai_cfg.get('engine')}, Model={ai_cfg.get('model')}, URL={ai_cfg.get('url')}")
                    finally:
                        st.session_state.pending_ai_action = None
                        st.session_state.ai_busy = False

            elif pending_ai_action == "suggest_components":
                if not current_txt:
                    st.toast(get_text("ai_input_required"))
                    st.session_state.pending_ai_action = None
                    st.session_state.ai_busy = False
                    st.session_state.last_ai_action_ts = time.time()
                    set_ai_status("ai_status_failed")
                else:
                    try:
                        available_plugins = []
                        if get_plugin_registry:
                            try:
                                registry = get_plugin_registry()
                                available_plugins = registry.get_plugins_by_category()
                            except Exception:
                                pass
                        
                        with st.spinner(get_text("analyzing_structure")):
                            suggestions_raw, stat = run_ai(current_txt, "", ai_cfg, task_type="suggest_components", 
                                                          content_type=ai_content_type, available_plugins=available_plugins)
                        
                        import json
                        suggestions_list = []
                        try:
                            json_str = suggestions_raw.strip()
                            if json_str.startswith("```"):
                                json_str = json_str.split("```")[1]
                                if json_str.startswith("json"):
                                    json_str = json_str[4:]
                            json_str = json_str.strip()
                            suggestions_list = json.loads(json_str)
                        except Exception:
                            suggestions_lower = suggestions_raw.lower()
                            component_names = ["hero", "col-2", "col-3", "steps", "timeline", "card"]
                            if get_plugin_registry:
                                try:
                                    registry = get_plugin_registry()
                                    plugins = registry.get_plugins_by_category()
                                    for plugin in plugins:
                                        component_names.append(plugin.name)
                                except Exception:
                                    pass
                            for comp in component_names:
                                if comp in suggestions_lower:
                                    suggestions_list.append({"component": comp, "position": "end"})
                        
                        st.session_state.component_suggestions = suggestions_list
                        st.session_state.component_suggestions_content = current_txt  # Store content snapshot

                        if suggestions_list:
                            st.toast(get_text("found_suggestions").format(count=len(suggestions_list)), icon="✅")
                        else:
                            st.toast(get_text("no_suggestions"), icon="ℹ️")
                        set_ai_status("ai_status_success")
                        st.session_state.last_failed_ai_action = None
                    except Exception:
                        st.toast(get_text("ai_action_failed"), icon="❌")
                        set_ai_status("ai_status_failed")
                        st.session_state.last_failed_ai_action = {"name": "suggest_components", "require_text": True}
                    finally:
                        st.session_state.pending_ai_action = None
                        st.session_state.ai_busy = False

            elif pending_ai_action == "polish_with_context":
                if not current_txt:
                    st.toast(get_text("ai_input_required"))
                    st.session_state.pending_ai_action = None
                    st.session_state.ai_busy = False
                    st.session_state.last_ai_action_ts = time.time()
                    set_ai_status("ai_status_failed")
                else:
                    try:
                        st.session_state.undo_stack = push_to_undo_stack(
                            current_txt,
                            st.session_state.undo_stack
                        )
                        st.session_state.redo_stack = []

                        with st.spinner(get_text("polishing_content")):
                            res, msg = run_ai(current_txt, context_text, ai_cfg, task_type="polish", content_type=ai_content_type)
                            
                            # Check if AI returned an error message
                            if msg.startswith("⚠️") or msg.startswith("❌"):
                                raise Exception(msg)
                            
                            st.session_state.content = res
                            st.session_state.reset_editor = True
                            if res:
                                st.session_state.undo_stack = push_to_undo_stack(
                                    res,
                                    st.session_state.undo_stack
                                )
                            st.toast(f"✅ {get_text('toast_format_applied').format(msg=msg)}")
                            time.sleep(0.5)
                        set_ai_status("ai_status_success")
                        st.session_state.last_failed_ai_action = None
                    except Exception as e:
                        error_msg = str(e)
                        st.toast(f"❌ {error_msg}", icon="❌")
                        set_ai_status("ai_status_failed")
                        st.session_state.last_failed_ai_action = {"name": "polish_with_context", "require_text": True}
                        if ErrorHandler:
                            ErrorHandler.log_error("ai_polish", e, {
                                "engine": ai_cfg.get('engine'), 
                                "model": ai_cfg.get('model'),
                                "url": ai_cfg.get('url'),
                                "content_length": len(current_txt) if current_txt else 0,
                                "context_length": len(context_text) if context_text else 0
                            })
                        # Debug: Show what we tried to send
                        st.error(f"Debug: Engine={ai_cfg.get('engine')}, Model={ai_cfg.get('model')}, URL={ai_cfg.get('url')}")
                    finally:
                        st.session_state.pending_ai_action = None
                        st.session_state.ai_busy = False
            # After handling the pending AI action, re-render the page with fresh state
            st.rerun()

        ai_busy = st.session_state.ai_busy
        st.subheader(f"🤖 {get_text('ai_actions')}")

        def ai_preflight():
            engine = ai_cfg.get("engine", "None")
            key = ai_cfg.get("key", "")
            if engine == "None":
                # Rely on inline status; no extra alert
                return False, None
            if engine in {"OpenAI", "OpenRouter", "Gemini"} and not key:
                return False, "Please add API key for selected engine."
            return True, None

        def trigger_ai_action(action_name: str, require_text: bool = False):
            now = time.time()
            if st.session_state.ai_busy:
                st.toast(get_text("ai_action_in_progress"))
                return
            if now - st.session_state.get("last_ai_action_ts", 0) < 0.4:
                st.toast(get_text("ai_action_debounced"))
                return
            ok, reason = ai_preflight()
            if not ok:
                if reason:
                    st.toast(reason)
                return
            if require_text and (not current_txt or not current_txt.strip()):
                st.toast(get_text("ai_input_required"))
                return
            if current_txt and len(current_txt) > MAX_AI_INPUT_CHARS:
                st.toast(get_text("ai_input_too_long"))
                return
            st.session_state.pending_ai_action = action_name
            st.session_state.ai_busy = True
            st.session_state.last_ai_action_ts = now
            set_ai_status("ai_status_last_action", action_label=action_name)
            st.rerun()

        ai_ready, ai_reason = ai_preflight()
        ai_col1, ai_col2 = st.columns(2)
        
        with ai_col1:
            if st.button(get_text("generate_titles"), use_container_width=True, disabled=ai_busy or not ai_ready, help=get_text("help_generate_titles")):
                trigger_ai_action("generate_titles", require_text=True)
            
            # Display generated titles below button (like components)
            if "generated_titles" in st.session_state and st.session_state.generated_titles:
                st.divider()
                st.subheader(f"📋 {get_text('generate_titles')}")
                
                # Show titles in horizontal layout
                titles = st.session_state.generated_titles
                title_lines = [line.strip() for line in titles.split('\n') if line.strip()]
                
                for idx, title in enumerate(title_lines):
                    clean_title = re.sub(r'^[\d\.\)\s]+', '', title).strip()
                    if clean_title:
                        # Truncate long titles
                        display_title = clean_title[:30] + "..." if len(clean_title) > 30 else clean_title
                        
                        t_col1, t_col2 = st.columns([4, 1])
                        with t_col1:
                            st.write(f"**{idx + 1}.** {display_title}")
                        with t_col2:
                            if st.button("📋", key=f"copy_title_{idx}", help="Copy"):
                                st.toast("Copied!", icon="✅")
                
                # Clear titles button
                if st.button(get_text("clear_suggestions").replace("Suggestions", "Titles"), use_container_width=True):
                    st.session_state.generated_titles = ""
                    st.rerun()
            
            if st.button(get_text("expand_content"), use_container_width=True, disabled=ai_busy or not ai_ready, help=get_text("help_expand_content")):
                trigger_ai_action("expand_content", require_text=True)
        
        with ai_col2:
            if st.button(get_text("smart_format"), use_container_width=True, disabled=ai_busy or not ai_ready, help=get_text("help_smart_format")):
                trigger_ai_action("smart_format", require_text=True)
            
            if st.button(get_text("suggest_components"), use_container_width=True, disabled=ai_busy or not ai_ready, help=get_text("help_suggest_components")):
                trigger_ai_action("suggest_components", require_text=True)

            if not ai_ready and ai_reason:
                st.caption(f"⚠️ {ai_reason}")
            
            # Display stored suggestions with insert buttons (persists across reruns)
            if "component_suggestions" in st.session_state and st.session_state.component_suggestions:
                with st.container():
                    st.divider()
                    st.subheader(get_text("suggested_components"))
                    
                    # Build component map with built-in components
                    component_map = {
                        "hero": "::: hero\n# Title\nSubtitle\n:::",
                        "col-2": "::: col-2\nLeft content\n--split--\nRight content\n:::",
                        "col-3": "::: col-3\nOne\n--split--\nTwo\n--split--\nThree\n:::",
                        "steps": "::: steps\n1. Step One\n2. Step Two\n:::",
                        "timeline": "::: timeline\n2024 Event\n2025 Event\n:::",
                        "card": "::: card\n## Card Title\nCard content here.\n:::"
                    }
                    
                    # Add plugin components to the map
                    if get_plugin_registry:
                        try:
                            registry = get_plugin_registry()
                            plugins = registry.get_plugins_by_category()
                            for plugin in plugins:
                                if plugin.insertion_tool:
                                    component_map[plugin.name] = plugin.insertion_tool
                        except:
                            pass
                    
                    # Show buttons for each suggestion
                    for idx, suggestion in enumerate(st.session_state.component_suggestions):
                        comp_name = suggestion.get("component", "")
                        position = suggestion.get("position", "end")
                        
                        if comp_name in component_map:
                            comp_template = component_map[comp_name]
                            comp_display_name = comp_name.replace("-", " ").title()
                            
                            sug_col1, sug_col2 = st.columns([3, 1])
                            with sug_col1:
                                st.write(f"**{comp_display_name}** - *{position}*")
                            with sug_col2:
                                if st.button("➕", key=f"insert_comp_{idx}", use_container_width=True, help=get_text("insert_component")):
                                    # Get current content
                                    current_content = st.session_state.get("content", "")
                                    
                                    # Insert at the suggested position
                                    new_content = insert_component_at_position(
                                        current_content, comp_template, position
                                    )
                                    
                                    st.session_state.content = new_content
                                    st.session_state.reset_editor = True
                                    
                                    # Remove this suggestion from the list
                                    st.session_state.component_suggestions.pop(idx)
                                    
                                    inserted_msg = get_text("component_inserted").format(name=comp_display_name, position=position)
                                    st.toast(inserted_msg)
                                    time.sleep(0.3)
                                    st.rerun()
                    
                    # Clear all suggestions button
                    if st.button(get_text("clear_suggestions"), use_container_width=True):
                        st.session_state.component_suggestions = []
                        st.rerun()

        # AI status cue (compact, inline style)
        engine_label = st.session_state.get("ai_cfg", {}).get("engine", "None")
        status_text = st.session_state.get("last_ai_status", get_text("ai_status_idle"))
        engine_set = engine_label and engine_label != "None"
        lang = st.session_state.get("ui_language", "en")
        if engine_set:
            engine_display = engine_label
            warning = ""
        else:
            if lang == "zh":
                engine_display = "引擎未设置"
                warning = " • ⚠️ 请先设置 AI 引擎"
            else:
                engine_display = "Engine: not set"
                warning = " • ⚠️ Please set AI Engine in sidebar"
        st.caption(f"🤖 {engine_display} • {status_text}{warning}")

        # AI Polish with Context button
        disable_ai_actions = ai_busy or not engine_set
        if st.button(get_text("polish_with_context"), use_container_width=True, help=get_text("help_polish_with_context"), disabled=disable_ai_actions):
            trigger_ai_action("polish_with_context", require_text=True)

        # Retry affordance when last action failed
        # Show last generated titles if available
        if st.session_state.get("last_titles_result"):
            st.toast(st.session_state.last_titles_result, icon="ℹ️")
        if (not st.session_state.ai_busy) and st.session_state.get("last_failed_ai_action"):
            failed_info = st.session_state.last_failed_ai_action
            action_name = failed_info.get("name")
            require_text_flag = failed_info.get("require_text", False)
            if st.button(get_text("ai_retry"), use_container_width=True, disabled=ai_busy):
                trigger_ai_action(action_name, require_text=require_text_flag)

        # In-app quick help
        with st.expander("❓ AI Help / 帮助", expanded=False):
            st.markdown("- EN: Set AI engine in sidebar (OpenRouter/Ollama) before running actions.")
            st.markdown("- EN: Editor must have text for Expand/Format/Suggest/Polish/Titles.")
            st.markdown("- EN: Buttons disable while AI runs; retry appears if it fails.")
            st.markdown("- 中文：在侧边栏先选择 AI 引擎（OpenRouter/Ollama）。")
            st.markdown("- 中文：编辑器需有内容才能使用扩展/格式/建议/润色/生成标题。")
            st.markdown("- 中文：运行中按钮会禁用，失败后可点击重试。")

    with col2:
        st.subheader(f"👁️ {view} Preview")
        
        # Get content from editor (prefer editor_content as it's the most up-to-date)
        content_to_render = st.session_state.get("editor_content") or st.session_state.get("content", "")
        
        # Get image provider and ratio from session state (use widget value when available so ratio changes apply immediately)
        img_provider = st.session_state.get("img_provider", "ModelScope (AI)")
        img_ratio = st.session_state.get("img_ratio_select", st.session_state.get("img_ratio", "1:1"))
        
        # Initialize wechat_final to ensure it's always defined
        wechat_final = None
        
        # Performance optimization: Debounced + cached preview rendering (content + theme + view)
        should_render_preview = True
        cached_preview = None
        
        if PerformanceOptimizer and st.session_state.get("performance_optimizer"):
            optimizer = st.session_state.performance_optimizer
            
            theme_key = f"{active_theme.get('bg', '')}|{active_theme.get('primary', '')}"
            # Include img_provider and img_ratio so changing ratio/provider re-renders preview with correct image size
            cache_key = f"{content_to_render}|{theme_key}|{view}|{img_provider}|{img_ratio}"
            cache_hash = hash(cache_key)
            
            cached_preview = optimizer.get_cached_preview(cache_key)
            last_hash = st.session_state.get("last_preview_content_hash")
            
            if cache_hash == last_hash and cached_preview:
                should_render_preview = False
            else:
                if optimizer.should_update_preview(cache_key):
                    st.session_state.last_preview_content_hash = cache_hash
                    should_render_preview = True
                else:
                    if cached_preview:
                        should_render_preview = False
        
        # Render preview if there's content
        # Large content guard (skip auto-render on very large input)
        content_hash_raw = hash(content_to_render)
        if st.session_state.get("last_preview_force_hash") != content_hash_raw:
            st.session_state.preview_force_render = False
            st.session_state.last_preview_force_hash = content_hash_raw
        size_bytes = len(content_to_render.encode("utf-8")) if content_to_render else 0
        is_large_preview = size_bytes > 120_000  # ~120KB

        has_content = content_to_render and content_to_render.strip()
        if has_content:
            if is_large_preview and not st.session_state.get("preview_force_render", False):
                size_kb = round(size_bytes / 1024)
                st.toast(get_text("toast_large_preview"), icon="⚠️")
                if st.button("Render preview", use_container_width=True, key="render_large_preview"):
                    st.session_state.preview_force_render = True
                    st.rerun()
                wechat_final = None
            else:
                st.session_state.preview_force_render = False
            # Try to use cached preview first (if available and should_render_preview is False)
            if st.session_state.get("preview_force_render", False) or not is_large_preview:
                # Try to use cached preview first (if available and should_render_preview is False)
                if not should_render_preview and cached_preview:
                    wechat_final = cached_preview
                else:
                    # Render fresh preview
                    try:
                        inline_styles = get_inline_styles(active_theme)
                        parsed_md = parse_doc(content_to_render, inline_styles, img_provider=img_provider, img_ratio=img_ratio, mode="wechat")
                
                        # Ensure parsed_md is not empty - if parse_doc returns empty, use original content
                        if not parsed_md or not parsed_md.strip():
                            parsed_md = content_to_render
                
                        # parsed_md contains HTML from plugins/components mixed with markdown
                        # markdown.markdown() escapes HTML, so we need to preserve HTML blocks
                        import re as re_module
                
                        # Strategy: Extract HTML blocks, process markdown, then merge back
                        # Use HTML comments as placeholders (markdown preserves them)
                        html_blocks = []
                
                        # Find all complete HTML elements (including ::: components)
                        def extract_html(match):
                            html_block = match.group(0)
                            # Use HTML comment as placeholder (markdown preserves comments)
                            placeholder = f"<!--MPHTML{len(html_blocks)}-->"
                            html_blocks.append(html_block)
                            return placeholder
                
                        # Improved pattern: handles nested tags, ::: components, and various HTML structures
                        # Pattern now better handles divs with inline styles and nested content
                        html_pattern = r':::[^:]+:::[^\n]*\n(?:[^\n]+\n)*?:::\s*:::[^\n]*|<(section|div|span|video)[^>]*>.*?</\1>|<(section|div|span|video)[^>]*/\s*>|<div[^>]*style="[^"]*"[^>]*>.*?</div>'
                        text_for_markdown = re_module.sub(html_pattern, extract_html, parsed_md, flags=re_module.DOTALL | re_module.IGNORECASE)
                
                        # Process markdown (HTML comments are preserved)
                        raw_html = markdown.markdown(text_for_markdown, extensions=['nl2br', 'extra'])
                
                        # Restore HTML blocks - replace placeholders with actual HTML
                        wechat_html_inner = raw_html
                        for i, html_block in enumerate(html_blocks):
                            placeholder = f"<!--MPHTML{i}-->"
                            wechat_html_inner = wechat_html_inner.replace(placeholder, html_block)
                
                        wechat_html_inner = deep_inject_styles(wechat_html_inner, inline_styles)
                        
                        # Add comprehensive CSS for WeChat export
                        primary = active_theme.get('primary', '#4A90E2')
                        card_bg = active_theme.get('card', '#fff')
                        radius = active_theme.get('radius', '12px')
                        # Component table header text color: based on THEME background brightness
                        bg_wc = str(active_theme.get('bg', '#ffffff')).lstrip('#')
                        if len(bg_wc) == 6:
                            r_wc = int(bg_wc[0:2], 16)
                            g_wc = int(bg_wc[2:4], 16)
                            b_wc = int(bg_wc[4:6], 16)
                            lum_wc = 0.2126 * r_wc + 0.7152 * g_wc + 0.0722 * b_wc
                            is_dark_wc = lum_wc < 128
                        else:
                            is_dark_wc = False
                        header_color_wc = "#000000" if is_dark_wc else "white"
                        
                        wechat_css = f"""
                        <style>
                        .mp-wechat {{font-family: inherit; line-height: 1.75; color: inherit;}}
                        .mp-wechat p {{margin-bottom: 16px;}}
                        .mp-wechat h1 {{color: {primary}; font-size: 24px; font-weight: bold; margin: 30px 0 20px 0;}}
                        .mp-wechat h2 {{color: {primary}; font-size: 18px; font-weight: bold; margin: 30px 0 15px 0; border-bottom: 2px solid {primary}20; padding-bottom: 8px;}}
                        .mp-wechat h3 {{font-size: 17px; font-weight: bold; margin: 20px 0 10px 0;}}
                        .mp-wechat li {{margin-bottom: 8px;}}
                        .mp-wechat ul, .mp-wechat ol {{padding-left: 20px; margin-bottom: 16px;}}
                        .mp-wechat strong {{font-weight: bold; color: {primary};}}
                        .mp-wechat img {{max-width: 100%; height: auto; display: block; margin: 12px auto; border-radius: {radius};}}
                        /* AI images: frame aspect ratio matches selection (16:9 wide, 9:16 tall) */
                        .mp-wechat img[data-mp-ratio="1:1"] {{aspect-ratio: 1; object-fit: contain; width: 100%; max-width: 100%; height: auto;}}
                        .mp-wechat img[data-mp-ratio="16:9"] {{aspect-ratio: 16/9; object-fit: contain; width: 100%; max-width: 100%; height: auto;}}
                        .mp-wechat img[data-mp-ratio="9:16"] {{aspect-ratio: 9/16; object-fit: contain; width: 100%; max-width: 100%; height: auto;}}
                        .mp-wechat .mp-hero {{background: {card_bg}; padding: 35px 20px; text-align: center !important; border-radius: {radius}; margin: 0 0 25px 0; box-shadow: inherit;}}
                        .mp-wechat .mp-card {{background: {card_bg}; border-left: 4px solid {primary}; padding: 15px; margin: 20px 0; border-radius: {radius}; box-shadow: inherit;}}
                        .mp-wechat .mp-card h3 {{margin-top: 0; color: {primary};}}
                        .mp-wechat .mp-center {{text-align: center !important; margin: 16px 0; width: 100%; box-sizing: border-box; background: transparent !important; box-shadow: none !important; padding: 0 !important; border: none !important; border-radius: 0 !important;}}
                        .mp-wechat .mp-center *,
                        .mp-wechat .mp-center p,
                        .mp-wechat .mp-center h1,
                        .mp-wechat .mp-center h2,
                        .mp-wechat .mp-center h3 {{text-align: center !important; background: transparent !important; box-shadow: none !important;}}
                        .mp-wechat .mp-grid {{display: flex; gap: 10px; flex-wrap: wrap; margin: 20px 0;}}
                        .mp-wechat .mp-col {{flex: 1; background: {card_bg}; padding: 10px; border-radius: {radius}; box-shadow: inherit; min-width: 0;}}
                        .mp-wechat .mp-step {{display: flex; gap: 12px; margin-bottom: 15px; align-items: center;}}
                        .mp-wechat .mp-step__num {{width: 28px; height: 28px; min-width: 28px; border-radius: 50%; background: {primary}; color: {active_theme.get('bg', '#fff')}; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px;}}
                        .mp-wechat .mp-timeline {{margin: 20px 0; padding-left: 15px;}}
                        .mp-wechat .mp-timeline__item {{position: relative; padding-left: 20px; padding-bottom: 20px; border-left: 2px solid {primary};}}
                        .mp-wechat .mp-timeline__dot {{position: absolute; left: -7px; top: 4px; width: 12px; height: 12px; border-radius: 50%; background: {primary};}}
                        .mp-wechat .mp-badge {{display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; background: {primary}20; color: {primary};}}
                        .mp-wechat .mp-btn-wrap {{text-align: center; margin: 30px 0;}}
                        .mp-wechat .mp-btn {{display: inline-block; padding: 10px 25px; background: {primary}; color: #fff; border-radius: {radius}; text-decoration: none; font-weight: bold;}}
                        .mp-wechat .mp-video {{position: relative; width: 100%; max-width: 900px; margin: 12px auto;}}
                        .mp-wechat .mp-video video {{width: 100%; height: auto; display: block;}}
                        .mp-wechat .mp-table {{width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);}}
                        .mp-wechat .mp-table th {{background: {primary}; color: {header_color_wc} !important; padding: 14px 16px; text-align: left; border: none; font-weight: 600; font-size: 14px;}}
                        .mp-wechat .mp-table td {{padding: 12px 16px; text-align: left; border-bottom: 1px solid #eee;}}
                        
                        /* Standard Markdown tables */
                        .mp-wechat table {{width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; border: 1px solid #ddd;}}
                        .mp-wechat table th,.mp-wechat table td {{border: 1px solid #ddd; padding: 10px 14px; text-align: left;}}
                        .mp-wechat table th {{background: {primary}; color: {header_color_wc}; font-weight: bold;}}
                        .mp-wechat .mp-reveal {{position: relative; margin: 20px 0; cursor: pointer; overflow: hidden; border-radius: {radius};}}
                        .mp-wechat .mp-reveal__content {{padding: 15px; border: 1px dashed #ccc; border-radius: 8px; background: #fff; min-height: 100px;}}
                        /* Preserve inline styles from components */
                        .mp-wechat section[style] {{border-radius: {radius}; padding: 16px; margin: 16px 0;}}
                        .mp-wechat div[style*="background"] {{border-radius: {radius};}}
                        </style>
                        """
                        
                        # Wrapper div: add gentle padding for WeChat paste
                        wrapper_bg = active_theme.get('bg', '#fff')
                        wrapper_style = f"background-color: {wrapper_bg}; padding: 16px; margin: 0; box-sizing: border-box;"
                        wechat_html_inner = f'{wechat_css}<div class="mp-wechat">{wechat_html_inner}</div>'
                        wechat_final = f'<div style="{wrapper_style}">{wechat_html_inner}</div>'
                
                        # Cache the preview (include theme, view, img_provider, img_ratio in cache key)
                        if PerformanceOptimizer and st.session_state.get("performance_optimizer"):
                            theme_key = f"{active_theme.get('bg', '')}|{active_theme.get('primary', '')}"
                            cache_key = f"{content_to_render}|{theme_key}|{view}|{img_provider}|{img_ratio}"
                            st.session_state.performance_optimizer.cache_preview(cache_key, wechat_final)
                    except Exception as e:
                        # If rendering fails, try to show at least the raw markdown
                        try:
                            # Fallback: just render the markdown directly
                            raw_html_fallback = markdown.markdown(content_to_render, extensions=['nl2br', 'extra'])
                            inline_styles = get_inline_styles(active_theme)
                            # Don't add wrapper background - let the canvas handle it for proper theme matching
                            # Wrapper div: add gentle padding for WeChat paste
                            wrapper_bg = active_theme.get('bg', '#fff')
                            wrapper_style = f"background-color: {wrapper_bg}; padding: 16px; margin: 0; box-sizing: border-box;"
                            raw_html_fallback = f'<style>.mp-wechat img{{display:block;margin:0 auto;}}</style><div class="mp-wechat">{raw_html_fallback}</div>'
                            wechat_final = f'<div style="{wrapper_style}">{raw_html_fallback}</div>'
                        except:
                            # Last resort: show error message
                            wechat_final = f'<div style="padding: 40px; text-align: center; color: #999;"><p>Preview error. Content: {len(content_to_render)} chars</p></div>'
        else:
            # No content - show placeholder
            wechat_final = None
            st.session_state.preview_force_render = False
        
        # Ensure parsed_md is always defined for standard HTML generation
        if 'parsed_md' not in locals():
            if content_to_render and content_to_render.strip():
                inline_styles = get_inline_styles(active_theme)
                parsed_md = parse_doc(content_to_render, inline_styles, img_provider=img_provider, img_ratio=img_ratio, mode="wechat")
            else:
                parsed_md = ""
        
        t = active_theme
        # For standard HTML, also need to preserve HTML blocks
        # Improved regex to handle both nested tags and self-contained components
        import re as re_module_std
        html_blocks_std = []
        def extract_html_std(match):
            html_block = match.group(0)
            placeholder = f"<!--MPHTML{len(html_blocks_std)}-->"
            html_blocks_std.append(html_block)
            return placeholder
        
        # Match both complete elements with closing tags AND self-closing or single-line components
        # This handles: <section>...</section>, <div class="x">...</div>, ::: components :::
        html_pattern_std = r':::[^:]+:::[^\n]*\n(?:[^\n]+\n)*?:::\s*:::[^\n]*|<(section|div|span|video)[^>]*>.*?</\1>|<(section|div|span|video)[^>]*/\s*>'
        parsed_md_for_std = re_module_std.sub(html_pattern_std, extract_html_std, parsed_md, flags=re_module_std.DOTALL | re_module_std.IGNORECASE)
        standard_html_content = markdown.markdown(parsed_md_for_std, extensions=['nl2br', 'extra'])
        for i, html_block in enumerate(html_blocks_std):
            standard_html_content = standard_html_content.replace(f"<!--MPHTML{i}-->", html_block)
        
        # Comprehensive component CSS that matches actual component output
        primary = t['primary']
        card_bg = t.get('card', '#fff')
        radius = t.get('radius', '12px')
        shadow = t.get('shadow', '0 4px 12px rgba(0,0,0,0.08)')
        # Component table header text color: based on THEME background brightness
        bg_std = str(t.get('bg', '#ffffff')).lstrip('#')
        if len(bg_std) == 6:
            r_std = int(bg_std[0:2], 16)
            g_std = int(bg_std[2:4], 16)
            b_std = int(bg_std[4:6], 16)
            lum_std = 0.2126 * r_std + 0.7152 * g_std + 0.0722 * b_std
            is_dark_std = lum_std < 128
        else:
            is_dark_std = False
        header_color_std = "#000000" if is_dark_std else "white"
        component_header_text_color = header_color_std
        
        component_css = f"""
        body{{font-family:{t['font']};padding:20px;max-width:800px;margin:0 auto;line-height:1.75;color:{t['text']};background:{t['bg']};}}
        img{{max-width:100%;height:auto;display:block;margin:12px auto;border-radius:{radius};}}
        a{{color:{primary};text-decoration:none;}}
        p{{margin:0 0 16px 0;line-height:1.75;}}
        h1{{font-size:24px;font-weight:bold;color:{primary};margin:30px 0 20px 0;line-height:1.4;}}
        h2{{font-size:18px;font-weight:bold;color:{primary};margin:30px 0 15px 0;border-bottom:2px solid {primary}20;padding-bottom:8px;}}
        h3{{font-size:17px;font-weight:bold;margin:20px 0 10px 0;}}
        ul,ol{{padding-left:20px;margin:0 0 16px 0;}}
        li{{margin:0 0 8px 0;line-height:1.75;}}
        strong{{font-weight:bold;color:{primary};}}
        
        /* Hero Component */
        .mp-hero{{background:{card_bg};padding:35px 20px;text-align:center !important;border-radius:{radius};margin:0 0 25px 0;box-shadow:{shadow};box-sizing:border-box;}}
        .mp-hero h1{{text-align:center !important;margin-top:0 !important;}}
        
        /* Card Component */
        .mp-card{{background:{card_bg};border-left:4px solid {primary};padding:15px;margin:20px 0;border-radius:{radius};box-shadow:{shadow};box-sizing:border-box;}}
        .mp-card h3{{margin-top:0;font-size:16px;color:{primary};}}
        
        /* Center Align Component - Plain text, no background/shadow */
        .mp-center{{text-align:center !important;margin:16px 0;width:100%;box-sizing:border-box;background:transparent !important;box-shadow:none !important;padding:0 !important;border:none !important;border-radius:0 !important;}}
        .mp-center *,
        .mp-center p,
        .mp-center h1,
        .mp-center h2,
        .mp-center h3{{text-align:center !important;background:transparent !important;box-shadow:none !important;}}
        
        /* Grid Layout */
        .mp-grid{{display:flex;gap:10px;margin:20px 0;flex-wrap:wrap;}}
        .mp-col{{flex:1 1 0;min-width:200px;background:{card_bg};padding:10px;border-radius:{radius};box-shadow:{shadow};box-sizing:border-box;}}
        
        /* Video Component */
        .mp-video{{position:relative;width:100%;max-width:900px;margin:12px auto;}}
        .mp-video video{{width:100%;height:auto;display:block;}}
        .mp-video__caption{{font-size:13px;color:#666;margin-top:6px;text-align:center;}}
        
        /* Button Component */
        .mp-btn-wrap{{text-align:center;margin:30px 0;}}
        .mp-btn{{display:inline-block;padding:10px 25px;background:{primary};color:#fff;border-radius:{radius};text-decoration:none;font-weight:bold;}}
        
        /* Steps Component */
        .mp-steps{{margin:20px 0;}}
        .mp-step{{display:flex;gap:12px;margin-bottom:15px;align-items:center;}}
        .mp-step__num{{width:28px;height:28px;min-width:28px;border-radius:50%;background:{primary};color:{t.get('bg', '#fff')};display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:14px;}}
        .mp-step__content{{flex:1;}}
        
        /* Timeline Component */
        .mp-timeline{{margin:20px 0;padding-left:15px;}}
        .mp-timeline__item{{position:relative;padding-left:20px;padding-bottom:20px;border-left:2px solid {primary};}}
        .mp-timeline__dot{{position:absolute;left:-7px;top:4px;width:12px;height:12px;border-radius:50%;background:{primary};}}
        
        /* Badge Component */
        .mp-badge{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:bold;vertical-align:middle;margin-right:5px;background:{primary}20;color:{primary};}}
        
        /* Reveal Component */
        .mp-reveal{{position:relative;margin:20px 0;cursor:pointer;overflow:hidden;border-radius:{radius};}}
        .mp-reveal__content{{padding:15px;border:1px dashed #ccc;border-radius:8px;background:#fff;min-height:100px;display:flex;align-items:center;justify-content:center;text-align:center;}}
        
        /* Table Component */
        .mp-table{{width:100%;border-collapse:collapse;margin:20px 0;font-size:14px;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1);}}
        .mp-table th{{background:{primary};color:{component_header_text_color};padding:14px 16px;text-align:left;border:none;font-weight:600;font-size:14px;}}
        .mp-table td{{padding:12px 16px;text-align:left;border-bottom:1px solid #eee;}}
        .mp-table tr:nth-child(even){{background:{card_bg}40;}}
        
        /* Standard Markdown tables */
        table{{width:100%;border-collapse:collapse;margin:20px 0;font-size:14px;border:1px solid #ddd;}}
        table th,table td{{border:1px solid #ddd;padding:10px 14px;text-align:left;}}
        table th{{background:{primary};color:{component_header_text_color};font-weight:bold;}}
        table tr:nth-child(even) td{{background:{card_bg}40;}}
        
        /* Section/div with inline styles (WeChat mode components) */
        section[style*="background"],div[style*="background"]{{border-radius:{radius};padding:16px;margin:16px 0;}}
        """
        standard_full = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{component_css}</style></head><body>{standard_html_content}</body></html>"""
        
        # Performance indicator (subtle, only when using cache)
        preview_status = ""
        if not should_render_preview and cached_preview:
            preview_status = "⚡ Cached"
        else:
            preview_status = "⬤ Updated"
        st.session_state.last_render_ts = time.time()
        
        t1, t2, t3 = st.tabs([get_text("tab_visual"), get_text("tab_wechat_code"), get_text("tab_standard_html")])
        if preview_status:
            last_render_ts = st.session_state.get("last_render_ts")
            if last_render_ts:
                last_render_str = datetime.fromtimestamp(last_render_ts).strftime("%Y-%m-%d %H:%M:%S")
                st.caption(f"{preview_status} • Rendered: {last_render_str}")
            else:
                st.caption(preview_status)
        with t1:
            import random
            k = random.randint(0,10000)
            if preview_status:
                st.caption(get_text("preview_cached"))
            # Ensure wechat_final has content, show placeholder if empty
            if not wechat_final:
                # No preview generated - check if we have content to render
                if content_to_render and content_to_render.strip():
                    # Content exists but preview failed - force render one more time
                    try:
                        inline_styles = get_inline_styles(active_theme)
                        parsed_md = parse_doc(content_to_render, inline_styles, img_provider=img_provider, img_ratio=img_ratio, mode="wechat")
                        
                        # Ensure parsed_md is not empty - if parse_doc returns empty, use original content
                        if not parsed_md or not parsed_md.strip():
                            parsed_md = content_to_render
                        
                        import re as re_module_final
                        html_blocks_final = []
                        def extract_html_final(match):
                            html_block = match.group(0)
                            placeholder = f"<!--MPHTML{len(html_blocks_final)}-->"
                            html_blocks_final.append(html_block)
                            return placeholder
                        
                        # Improved pattern to handle ::: components and various HTML structures
                        html_pattern_final = r':::[^:]+:::[^\n]*\n(?:[^\n]+\n)*?:::\s*:::[^\n]*|<(section|div|span|video)[^>]*>.*?</\1>|<(section|div|span|video)[^>]*/\s*>'
                        text_for_markdown_final = re_module_final.sub(html_pattern_final, extract_html_final, parsed_md, flags=re_module_final.DOTALL | re_module_final.IGNORECASE)
                        raw_html_final = markdown.markdown(text_for_markdown_final, extensions=['nl2br', 'extra'])
                        wechat_html_inner_final = raw_html_final
                        for i, html_block in enumerate(html_blocks_final):
                            placeholder = f"<!--MPHTML{i}-->"
                            wechat_html_inner_final = wechat_html_inner_final.replace(placeholder, html_block)
                        wechat_html_inner_final = deep_inject_styles(wechat_html_inner_final, inline_styles)
                        
                        # Add CSS for fallback case too
                        primary = active_theme.get('primary', '#4A90E2')
                        card_bg = active_theme.get('card', '#fff')
                        radius = active_theme.get('radius', '12px')
                        fallback_css = f"""
                        <style>
                        .mp-fallback {{font-family: inherit; line-height: 1.75; color: inherit;}}
                        .mp-fallback p {{margin-bottom: 16px;}}
                        .mp-fallback h1 {{color: {primary}; font-size: 24px; font-weight: bold;}}
                        .mp-fallback h2 {{color: {primary}; font-size: 18px; font-weight: bold;}}
                        .mp-fallback .mp-hero {{background: {card_bg}; padding: 35px 20px; text-align: center !important; border-radius: {radius};}}
                        .mp-fallback .mp-hero h1 {{text-align: center !important;}}
                        .mp-fallback .mp-card {{background: {card_bg}; border-left: 4px solid {primary}; padding: 15px; margin: 20px 0; border-radius: {radius};}}
                        .mp-fallback .mp-center {{text-align: center !important; margin: 16px 0; width: 100%; box-sizing: border-box; background: transparent !important; box-shadow: none !important; padding: 0 !important; border: none !important; border-radius: 0 !important;}}
                        .mp-fallback .mp-center *,
                        .mp-fallback .mp-center p,
                        .mp-fallback .mp-center h1,
                        .mp-fallback .mp-center h2,
                        .mp-fallback .mp-center h3 {{text-align: center !important; background: transparent !important; box-shadow: none !important;}}
                        .mp-fallback .mp-grid {{display: flex; gap: 10px; flex-wrap: wrap;}}
                        .mp-fallback .mp-col {{flex: 1; background: {card_bg}; padding: 10px; border-radius: {radius};}}
                        .mp-fallback .mp-step {{display: flex; gap: 12px; margin-bottom: 15px;}}
                        .mp-fallback .mp-step__num {{width: 28px; height: 28px; border-radius: 50%; background: {primary}; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: bold;}}
                        .mp-fallback .mp-timeline {{margin: 20px 0; padding-left: 15px;}}
                        .mp-fallback .mp-timeline__item {{position: relative; padding-left: 20px; border-left: 2px solid {primary};}}
                        .mp-fallback .mp-timeline__dot {{position: absolute; left: -7px; top: 4px; width: 12px; height: 12px; border-radius: 50%; background: {primary};}}
                        .mp-fallback img {{max-width: 100%; height: auto;}}
                        .mp-fallback img[data-mp-ratio="1:1"] {{aspect-ratio: 1; object-fit: contain; width: 100%; max-width: 100%; height: auto;}}
                        .mp-fallback img[data-mp-ratio="16:9"] {{aspect-ratio: 16/9; object-fit: contain; width: 100%; max-width: 100%; height: auto;}}
                        .mp-fallback img[data-mp-ratio="9:16"] {{aspect-ratio: 9/16; object-fit: contain; width: 100%; max-width: 100%; height: auto;}}
                        </style>
                        """
                        wechat_html_inner_final = f'<div class="mp-fallback">{wechat_html_inner_final}</div>'
                        wrapper_bg = active_theme.get('bg', '#fff')
                        wrapper_style = f"background-color: {wrapper_bg}; padding: 0; margin: 0; box-sizing: border-box;"
                        wechat_final = f'{fallback_css}<div style="{wrapper_style}">{wechat_html_inner_final}</div>'
                    except Exception as e:
                        # If rendering fails, try simple markdown render
                        try:
                            raw_html_simple = markdown.markdown(content_to_render, extensions=['nl2br', 'extra'])
                            inline_styles = get_inline_styles(active_theme)
                            wrapper_bg = active_theme.get('bg', '#fff')
                            wrapper_style = f"background-color: {wrapper_bg}; padding: 0; margin: 0; box-sizing: border-box;"
                            wechat_final = f'<div style="{wrapper_style}">{raw_html_simple}</div>'
                        except:
                            # Last resort: show placeholder
                            no_content_text = get_text("no_content")
                            wechat_final = f'<div style="padding: 40px; text-align: center; color: #999;"><p>{no_content_text}</p></div>'
                else:
                    # No content - show placeholder
                    no_content_text = get_text("no_content")
                    wechat_final = f'<div style="padding: 40px; text-align: center; color: #999;"><p>{no_content_text}</p></div>'
            elif wechat_final.strip() == "":
                # Empty string - show placeholder
                no_content_text = get_text("no_content")
                wechat_final = f'<div style="padding: 40px; text-align: center; color: #999;"><p>{no_content_text}</p></div>'
            else:
                # Check if the content inside the div is actually empty (just empty div tags)
                import re as re_check
                # Remove all HTML tags and check if there's any text content
                text_content = re_check.sub(r'<[^>]+>', '', wechat_final).strip()
                has_image = "<img" in wechat_final.lower()
                if (not text_content or text_content == "") and not has_image:
                    # Empty content (and no images) - show placeholder
                    no_content_text = get_text("no_content")
                    wechat_final = f'<div style="padding: 40px; text-align: center; color: #999;"><p>{no_content_text}</p></div>'
            # Always show mobile frame when view is "Mobile"
            # Get theme values from active_theme (see themes.py for structure)
            bg_color = active_theme.get('bg', '#FAFAFA')
            card_color = active_theme.get('card', '#FFFFFF')
            text_color = active_theme.get('text', '#1D1D1F')
            muted_color = active_theme.get('muted', '#6B7280')
            primary_color = active_theme.get('primary', '#007AFF')
            accent_color = active_theme.get('accent', '#E5E5EA')
            font_family = active_theme.get('font', "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif")
            border_radius = active_theme.get('radius', '16px')
            shadow = active_theme.get('shadow', '0 1px 3px rgba(0,0,0,0.06)')
            # Component table header text color: based on THEME background brightness
            # Light theme (light bg) → white header text
            # Dark theme (dark bg) → black header text
            bg_hex = str(bg_color).lstrip('#')
            if len(bg_hex) == 6:
                r = int(bg_hex[0:2], 16)
                g = int(bg_hex[2:4], 16)
                b = int(bg_hex[4:6], 16)
                luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
                is_dark = luminance < 128
            else:
                is_dark = False
            component_header_text_color = "#000000" if is_dark else "white"
            
            # Mobile frame dimensions - iPhone 17 Pro style
            # Use session state which always has English values
            is_mobile = (st.session_state.get("preview_view", "Mobile") == "Mobile")
            
            # Build complete HTML with embedded styles
            preview_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body, html {{ 
    margin: 0; 
    padding: 0; 
    background: transparent;
    font-family: {font_family};
    overflow: visible;
    min-height: 100%;
}}
::-webkit-scrollbar {{ display: none; }}

/* iPhone 17 Pro Frame */
.iphone-frame {{
    width: 100%;
    max-width: 390px;
    aspect-ratio: 390 / 780;
    height: auto;
    margin: 4px auto;
    position: relative;
    background: linear-gradient(145deg, #2a2a2e 0%, #1a1a1e 50%, #0a0a0e 100%);
    border-radius: 58px;
    padding: 10px;
    box-sizing: border-box;
    box-shadow: 
        0 50px 100px -20px rgba(0,0,0,0.5),
        0 30px 60px -30px rgba(0,0,0,0.6),
        inset 0 2px 4px rgba(255,255,255,0.1),
        inset 0 -2px 4px rgba(0,0,0,0.3),
        0 0 0 1px rgba(255,255,255,0.05);
}}
/* Dynamic Island only (no peninsula) */
.iphone-frame::after {{
    content: '';
    position: absolute;
    top: 22px;
    left: 50%;
    transform: translateX(-50%);
    width: 126px;
    height: 36px;
    background: #000;
    border-radius: 20px;
    z-index: 201;
    box-shadow: inset 0 0 3px rgba(255,255,255,0.05);
}}
/* Screen bezel */
.screen-bezel {{
    width: 100%;
    height: 100%;
    background: {bg_color};
    border-radius: 48px;
    overflow: hidden;
    position: relative;
}}
/* Side buttons - Volume */
.iphone-frame .vol-up,
.iphone-frame .vol-down {{
    position: absolute;
    left: -3px;
    width: 4px;
    background: linear-gradient(90deg, #3a3a3e, #2a2a2e);
    border-radius: 2px 0 0 2px;
}}
.iphone-frame .vol-up {{ top: 140px; height: 35px; }}
.iphone-frame .vol-down {{ top: 185px; height: 35px; }}
/* Side buttons - Power */
.iphone-frame .power {{
    position: absolute;
    right: -3px;
    top: 170px;
    width: 4px;
    height: 70px;
    background: linear-gradient(90deg, #2a2a2e, #3a3a3e);
    border-radius: 0 2px 2px 0;
}}
/* Silent switch */
.iphone-frame .silent {{
    position: absolute;
    left: -3px;
    top: 100px;
    width: 4px;
    height: 25px;
    background: linear-gradient(90deg, #3a3a3e, #2a2a2e);
    border-radius: 2px 0 0 2px;
}}

/* PC View */
.pc-frame {{
    width: 100%;
    height: 750px;
    border: 1px solid #ddd;
    border-radius: 12px;
    background: {bg_color};
    overflow: hidden;
}}

.preview-content {{
    width: 100%;
    height: 100%;
    overflow-y: auto;
    overflow-x: hidden;
    -webkit-overflow-scrolling: touch;
    padding-top: {'50px' if is_mobile else '0'};
    background: {bg_color};
    -ms-overflow-style: none;
    scrollbar-width: none;
}}

/* Canvas - theme defaults */
.mp-canvas {{ 
    padding: 16px !important;
    min-height: 100%;
    background: {bg_color};
    color: {text_color};
    font-family: {font_family};
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    word-wrap: break-word;
    line-height: 1.75;
    overflow-x: hidden !important;
}}

/* Default text styles (NO !important - component inline styles override these) */
.mp-canvas p {{ 
    color: {text_color}; 
    font-family: {font_family};
    line-height: 1.75;
    margin-bottom: 16px;
}}
.mp-canvas li {{ 
    color: {text_color}; 
    font-family: {font_family};
    line-height: 1.75;
}}
.mp-canvas h1 {{ 
    color: {primary_color}; 
    font-family: {font_family};
    font-size: 24px;
    font-weight: bold;
    margin: 30px 0 20px 0;
}}
.mp-canvas h2 {{ 
    color: {primary_color}; 
    font-family: {font_family};
    font-size: 18px;
    font-weight: bold;
    margin: 30px 0 15px 0;
}}
.mp-canvas h3 {{ 
    color: {text_color}; 
    font-family: {font_family};
    font-size: 17px;
    font-weight: bold;
    margin: 20px 0 10px 0;
}}

/* Hero Component - override general h1 for hero sections */
.mp-canvas .mp-hero,
.mp-canvas section[style*="text-align: center"] {{
    background: {card_bg};
    padding: 35px 20px;
    text-align: center !important;
    border-radius: {border_radius};
    margin: 0 0 25px 0;
    box-shadow: {shadow};
    box-sizing: border-box;
    width: 100%;
}}
.mp-canvas .mp-hero h1,
.mp-canvas section[style*="text-align: center"] h1 {{
    text-align: center !important;
    margin-top: 0 !important;
    color: {primary_color};
    font-size: 24px;
    font-weight: bold;
}}

/* Card Component */
.mp-canvas .mp-card {{
    background: {card_bg};
    border-left: 4px solid {primary_color};
    padding: 15px;
    margin: 20px 0;
    border-radius: {border_radius};
    box-shadow: {shadow};
}}
.mp-canvas strong {{ 
    color: {primary_color}; 
    font-weight: bold;
}}
.mp-canvas blockquote {{
    border-left: 4px solid {primary_color};
    padding-left: 15px;
    color: {muted_color};
    font-style: italic;
    background: {accent_color};
    padding: 10px 10px 10px 15px;
    margin: 20px 0;
    border-radius: 0 {border_radius} {border_radius} 0;
}}
.mp-canvas a {{
    color: {primary_color};
    text-decoration: none;
}}
.mp-canvas a:hover {{
    text-decoration: underline;
}}

/* Image constraints - KEEP !important to prevent overflow */
.mp-canvas img, img {{
    max-width: 100% !important;
    height: auto !important;
    display: block;
    object-fit: contain;
    margin: 12px 0;
    border-radius: {border_radius};
}}

/* Container basics */
.mp-canvas > div {{
    max-width: 100%;
    box-sizing: border-box;
}}

/* Component wrappers - ensure isolation */
.mp-canvas .mp-steps-wrapper,
.mp-canvas .mp-timeline-wrapper {{
    display: block !important;
    clear: both !important;
    width: 100% !important;
    position: relative !important;
    overflow: visible !important;
}}

/* Steps component */
.mp-canvas .mp-steps-wrapper div[style*="display: flex"] {{
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
}}
.mp-canvas span[style*="border-radius: 50%"] {{
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    flex-shrink: 0 !important;
}}

/* Timeline component */
.mp-canvas .mp-timeline-wrapper div[style*="position: relative"] {{
    position: relative !important;
    display: block !important;
    width: 100% !important;
}}
.mp-canvas .mp-timeline-wrapper span[style*="position: absolute"] {{
    position: absolute !important;
    display: block !important;
}}
.mp-canvas .mp-timeline-wrapper div[style*="border-left"] {{
    border-left-style: solid !important;
    border-left-width: 2px !important;
}}

/* Grid layout (col-2, col-3) */
.mp-canvas section[style*="display: flex"] {{
    display: flex !important;
    gap: 10px !important;
    flex-wrap: wrap !important;
}}
.mp-canvas section[style*="display: flex"] > div {{
    flex: 1 1 auto !important;
    min-width: 100px !important;
}}

/* Hero/Card - constrain width, let backgrounds show */
.mp-canvas section,
.mp-canvas > div {{
    max-width: 100% !important;
    box-sizing: border-box !important;
}}

/* Standard Markdown tables (GFM | syntax) - borders and alignment */
.mp-canvas table {{
    width: 100% !important;
    border-collapse: collapse !important;
    margin: 20px 0 !important;
    font-size: 14px !important;
    border: 1px solid #ddd !important;
}}
.mp-canvas table th,
.mp-canvas table td {{
    border: 1px solid #ddd !important;
    padding: 10px 14px !important;
    text-align: left !important;
}}
    .mp-canvas table th {{
        background-color: {primary_color} !important;
        color: {component_header_text_color} !important;
        font-weight: bold !important;
    }}
    .mp-canvas .mp-table[data-mp-table="true"] {{
        width: 100% !important;
        border-collapse: collapse !important;
        margin: 20px 0 !important;
        font-size: 14px !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }}
    .mp-canvas .mp-table[data-mp-table="true"] th {{
        background-color: {primary_color} !important;
        color: {component_header_text_color} !important;
        font-weight: 600 !important;
        padding: 14px 16px !important;
        text-align: left !important;
        border: none !important;
        font-size: 14px !important;
    }}
    .mp-canvas .mp-table[data-mp-table="true"] td {{
        padding: 12px 16px !important;
        text-align: left !important;
        border-bottom: 1px solid #eee !important;
        border: none !important;
    }}
    .mp-canvas .mp-table[data-mp-table="true"] tr:nth-child(even) {{
        background-color: {card_bg}40 !important;
    }}
    .mp-canvas .mp-table[data-mp-table="true"] tr:hover {{
        background-color: {card_bg}60 !important;
    }}
    .mp-canvas table tbody tr:nth-child(even) td {{
        background-color: {accent_color} !important;
    }}
.mp-canvas table th[align="center"],
.mp-canvas table td[align="center"] {{
    text-align: center !important;
}}
.mp-canvas table th[align="right"],
.mp-canvas table td[align="right"] {{
    text-align: right !important;
}}
</style>
</head>
<body>
{'<div class="iphone-frame"><div class="vol-up"></div><div class="vol-down"></div><div class="power"></div><div class="silent"></div><div class="screen-bezel">' if is_mobile else '<div class="pc-frame">'}
<div class="preview-content">
<div class="mp-canvas">{wechat_final}</div>
</div>
{'</div></div>' if is_mobile else '</div>'}
</body>
</html>
<!-- {{k}} -->"""
            # Calculate height for mobile (frame + padding) or use fixed for desktop
            preview_height = 850 if not is_mobile else 820
            st.components.v1.html(preview_html, height=preview_height, scrolling=True)
            # Refresh sidebar quota immediately after an AI image was generated this run
            if st.session_state.pop("ai_image_quota_just_updated", False):
                st.rerun()
        with t2:
            clean_code = clean_for_wechat(wechat_final)
            
            # Copy button with hidden textarea + toast styled like existing app toasts
            copy_button_text = get_text('copy_wechat_html')
            toast_copied_text = get_text("toast_copied")
            toast_failed_text = get_text("toast_copy_failed")
            copy_component = f"""
            <div style="margin-bottom: 10px;">
                <textarea id="wechat-html-copy" style="position: absolute; left: -9999px; opacity: 0;">{clean_code.replace('</textarea>', '&lt;/textarea&gt;')}</textarea>
                <button onclick="copyWeChatHTML()" style="
                    background-color: #007AFF;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 500;
                    margin-bottom: 10px;
                ">{copy_button_text}</button>
            </div>
            <script>
            function showCopyToastWechat(ok) {{
                const doc = window.parent && window.parent.document ? window.parent.document : document;
                const id = 'copy-toast-wechat';
                let toast = doc.getElementById(id);
                if (!toast) {{
                    toast = doc.createElement('div');
                    toast.id = id;
                    toast.style.position = 'fixed';
                    toast.style.top = '20px';
                    toast.style.right = '20px';
                    toast.style.background = '#f6f6f6';
                    toast.style.color = '#222';
                    toast.style.border = '1px solid #e6e6e6';
                    toast.style.borderRadius = '14px';
                    toast.style.padding = '14px 18px';
                    toast.style.boxShadow = '0 8px 24px rgba(0,0,0,0.12)';
                    toast.style.fontSize = '16px';
                    toast.style.display = 'none';
                    toast.style.alignItems = 'center';
                    toast.style.gap = '10px';
                    toast.style.zIndex = '999999';
                    toast.style.cursor = 'default';
                    toast.innerHTML = `
                      <span id="copy-toast-icon-wechat" style="
                        width: 26px; height: 26px; display: inline-flex; align-items: center; justify-content: center;
                        border-radius: 6px; background: #18a118; color: #fff; font-weight: 700;">✓</span>
                      <span id="copy-toast-text-wechat">{toast_copied_text}</span>
                      <span id="copy-toast-close-wechat" style="margin-left: 8px; color: #888; cursor: pointer;">✕</span>
                    `;
                    doc.body.appendChild(toast);
                    const close = doc.getElementById('copy-toast-close-wechat');
                    if (close) close.onclick = () => (toast.style.display = 'none');
                }}
                const icon = doc.getElementById('copy-toast-icon-wechat');
                const text = doc.getElementById('copy-toast-text-wechat');
                if (ok) {{
                    if (icon) {{
                        icon.style.background = '#18a118';
                        icon.textContent = '✓';
                    }}
                    if (text) text.textContent = `{toast_copied_text}`;
                }} else {{
                    if (icon) {{
                        icon.style.background = '#d93025';
                        icon.textContent = '!';
                    }}
                    if (text) text.textContent = `{toast_failed_text}`;
                }}
                toast.style.display = 'flex';
                clearTimeout(window.__copyToastWechatTimer);
                window.__copyToastWechatTimer = setTimeout(() => (toast.style.display = 'none'), 2000);
            }}
            function copyWeChatHTML() {{
                const textarea = document.getElementById('wechat-html-copy');
                textarea.select();
                textarea.setSelectionRange(0, 99999);
                try {{
                    if (document.execCommand('copy')) {{ showCopyToastWechat(true); return; }}
                    navigator.clipboard.writeText(textarea.value).then(function() {{
                        showCopyToastWechat(true);
                    }}).catch(function() {{
                        showCopyToastWechat(false);
                    }});
                }} catch (e) {{
                    navigator.clipboard.writeText(textarea.value).then(function() {{
                        showCopyToastWechat(true);
                    }}).catch(function() {{
                        showCopyToastWechat(false);
                    }});
                }}
            }}
            </script>
            """
            st.components.v1.html(copy_component, height=60)
            st.code(clean_code, language="html")
        with t3:
            size_bytes_export = len((st.session_state.get("content") or "").encode("utf-8")) if st.session_state.get("content") else 0
            size_kb_export = round(size_bytes_export / 1024)
            st.caption(f"Export size: ~{size_kb_export} KB. WeChat/HTML best under ~120KB.")
            col_copy_std, col_download = st.columns(2)
            with col_copy_std:
                copy_std_text = get_text("copy_html_code")
                toast_copied_text = get_text("toast_copied")
                toast_failed_text = get_text("toast_copy_failed")
                copy_std_component = f"""
                <div style="margin-bottom: 10px;">
                    <textarea id="standard-html-copy" style="position: absolute; left: -9999px; opacity: 0;">{standard_full.replace("</textarea>", "&lt;/textarea&gt;").replace("</script>", "&lt;/script&gt;").replace("<script", "&lt;script")}</textarea>
                    <button onclick="copyStandardHTML()" style="
                        background-color: #007AFF;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: 500;
                    ">{copy_std_text}</button>
                </div>
                <script>
                function showCopyToastStd(ok) {{
                    const doc = window.parent && window.parent.document ? window.parent.document : document;
                    const id = 'copy-toast-std';
                    let toast = doc.getElementById(id);
                    if (!toast) {{
                        toast = doc.createElement('div');
                        toast.id = id;
                        toast.style.position = 'fixed';
                        toast.style.top = '20px';
                        toast.style.right = '20px';
                        toast.style.background = '#f6f6f6';
                        toast.style.color = '#222';
                        toast.style.border = '1px solid #e6e6e6';
                        toast.style.borderRadius = '14px';
                        toast.style.padding = '14px 18px';
                        toast.style.boxShadow = '0 8px 24px rgba(0,0,0,0.12)';
                        toast.style.fontSize = '16px';
                        toast.style.display = 'none';
                        toast.style.alignItems = 'center';
                        toast.style.gap = '10px';
                        toast.style.zIndex = '999999';
                        toast.style.cursor = 'default';
                        toast.innerHTML = `
                          <span id="copy-toast-icon-std" style="
                            width: 26px; height: 26px; display: inline-flex; align-items: center; justify-content: center;
                            border-radius: 6px; background: #18a118; color: #fff; font-weight: 700;">✓</span>
                          <span id="copy-toast-text-std">{toast_copied_text}</span>
                          <span id="copy-toast-close-std" style="margin-left: 8px; color: #888; cursor: pointer;">✕</span>
                        `;
                        doc.body.appendChild(toast);
                        const close = doc.getElementById('copy-toast-close-std');
                        if (close) close.onclick = () => (toast.style.display = 'none');
                    }}
                    const icon = doc.getElementById('copy-toast-icon-std');
                    const text = doc.getElementById('copy-toast-text-std');
                    if (ok) {{
                        if (icon) {{
                            icon.style.background = '#18a118';
                            icon.textContent = '✓';
                        }}
                        if (text) text.textContent = `{toast_copied_text}`;
                    }} else {{
                        if (icon) {{
                            icon.style.background = '#d93025';
                            icon.textContent = '!';
                        }}
                        if (text) text.textContent = `{toast_failed_text}`;
                    }}
                    toast.style.display = 'flex';
                    clearTimeout(window.__copyToastStdTimer);
                    window.__copyToastStdTimer = setTimeout(() => (toast.style.display = 'none'), 2000);
                }}
                function copyStandardHTML() {{
                    const textarea = document.getElementById('standard-html-copy');
                    textarea.select();
                    textarea.setSelectionRange(0, 99999);
                    try {{
                        if (document.execCommand('copy')) {{ showCopyToastStd(true); return; }}
                        navigator.clipboard.writeText(textarea.value).then(function() {{
                            showCopyToastStd(true);
                        }}).catch(function() {{
                            showCopyToastStd(false);
                        }});
                    }} catch (e) {{
                        navigator.clipboard.writeText(textarea.value).then(function() {{
                            showCopyToastStd(true);
                        }}).catch(function() {{
                            showCopyToastStd(false);
                        }});
                    }}
                }}
                </script>
                """
                st.components.v1.html(copy_std_component, height=50)
            with col_download:
                st.download_button(get_text("download_html"), standard_full, "article.html", "text/html", use_container_width=True)
            st.code(standard_full, language="html")

if __name__ == "__main__":
    main()

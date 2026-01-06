# MarkPolish Studio

A powerful Streamlit-based content creation and editing tool for creating beautifully formatted markdown content, especially optimized for WeChat publishing.

## What's New (Latest Updates)

### 🎨 Enhanced Image System
- **8 Beautiful Gradient Styles**: Blue, Purple, Sunset, Ocean, Forest, Aurora, Fire, Midnight
- **Real Pattern Backgrounds**: Polka dots and diagonal lines patterns with grey tones
- **Consistent 16:9 Ratio**: All images now use 800x450 (16:9) aspect ratio
- **Auto-Render**: Preview updates automatically when Image Source changes

### 🤖 AI Actions - Now Fully Working!
- **Generate Titles**: Displays persistently below button with copy functionality
- **Smart Format**: Better error handling and detailed logging
- **Expand Content**: Improved error reporting with debug info
- **Suggest Components**: Insert components with one click
- **Polish with Context**: Conservative mode preserves original format
- **Fixed Ollama Integration**: 
  - Now actually fetches models from local Ollama instance
  - Better connection checking with specific error messages
  - Normalized engine name detection
  - 60-second timeout for local models

### 🐛 Bug Fixes
- Fixed NameError: context_text not defined
- Removed empty div elements from DOM
- Fixed sidebar spacing (gap:0 no longer affects sidebar)
- Better session state initialization
- Comprehensive error logging for debugging

## Features

- 📝 **Rich Markdown Editor** - Create content with markdown syntax and custom components
- 🎨 **Theme Support** - Multiple beautiful themes for different content styles
- 📄 **PDF Export** - Export your content as PDF with professional styling
- 🤖 **AI Integration** - AI-powered content polishing, formatting, and suggestions
- 🖼️ **Image Library** - Manage and reuse images across projects
- 📚 **Template Library** - Pre-built templates for common content types
- 🔌 **Plugin System** - Extend functionality with custom plugins
- 📱 **WeChat Optimized** - Content optimized for WeChat publishing
- 💾 **Auto-save** - Never lose your work with automatic saving
- 🔄 **Version History** - Track changes and restore previous versions
- 🌈 **Beautiful Gradients** - 8 stunning gradient styles for image placeholders
- 📐 **Pattern Backgrounds** - Real SVG-based patterns (dots, lines) for visual appeal

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Project Structure

```
MarkPolish Studio/
├── app.py                 # Main application (UI and orchestration)
├── config.py              # Configuration, templates, and setup
├── file_operations.py     # File save/load, version history, auto-save
├── pdf_generator.py       # PDF generation functionality
├── image_handling.py      # Image processing and library management
├── ai_integration.py      # AI/OpenAI integration
├── content_processing.py  # Content parsing, markdown processing, preview
├── ui_helpers.py         # UI utility functions
├── components.py          # Markdown component system
├── themes.py              # Theme definitions
├── error_handler.py       # Error handling utilities
├── performance.py         # Performance optimization
├── plugin_system.py       # Plugin system
├── keyboard_listener.py   # Keyboard shortcuts
├── migration_tool.py      # Migration utilities
├── requirements.txt       # Python dependencies
├── plugins/               # Custom plugins directory
│   ├── example_callout.py
│   └── README.md
└── projects/              # Project files directory
    └── images/            # Image library
```

## Usage

### Quick Start (EN)
- Create a virtualenv: `python -m venv venv && source venv/bin/activate`
- Install deps: `pip install -r requirements.txt`
- Run: `streamlit run app.py`
- Configure AI in the sidebar (OpenRouter or Ollama); leave as “None” to disable AI.
- Autosave is on; use **💾 Force Save Now** for a manual backup.

### 快速开始 (中文)
- 创建虚拟环境：`python -m venv venv && source venv/bin/activate`
- 安装依赖：`pip install -r requirements.txt`
- 运行：`streamlit run app.py`
- 在侧边栏配置 AI（OpenRouter 或本地 Ollama）；若不使用 AI 可保持 “None”。
- 自动保存始终开启；需要手动备份时点 **💾 立即强制保存**。

### Creating Content

1. **Start a New Project**: Click "New Project" in the sidebar
2. **Use Templates**: Select a template from the Templates tab
3. **Edit Content**: Use the markdown editor to create your content
4. **Preview**: See a live preview of your content
5. **Save**: Save your project with a name

### Markdown Components

MarkPolish Studio supports custom markdown components:

- `::: hero` - Hero sections with centered content
- `::: col-2` - Two-column layout
- `::: col-3` - Three-column layout
- `::: steps` - Step-by-step instructions
- `::: timeline` - Timeline visualization
- `::: card` - Styled card components
- `[IMG: description]` - AI-generated images
- `[LOCAL: filename]` - Local images
- `<video src="https://example.com/video.mp4" controls style="width:100%;height:auto;display:block;"></video>` - Responsive raw video embed (HTML)
- `::: video src="https://example.com/video.mp4" poster="" caption="" autoplay=false muted=false loop=false :::` - Video component (HTML player; WeChat may ignore inline playback)

### Themes

Choose from multiple themes optimized for different content types:
- Apple Minimalist
- Nordic Frost
- Dark Mode
- And more...

### AI Features

#### Supported AI Providers
- **Ollama (Local)** - Run AI models locally with full privacy
- **OpenAI** - GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo
- **OpenRouter** - Access to multiple AI models through single API
- **Gemini** - Google's AI models
- **Anthropic** - Claude models
- **DeepSeek** - Cost-effective AI models

#### AI Actions
- **💡 Generate Titles**: Generate catchy, punchy titles for your content (persists below button with copy functionality)
- **📈 Expand Content**: Add more detail, examples, and context to your content
- **✨ Smart Format**: Improve structure and formatting while preserving content
- **💡 Suggest Components**: Get AI suggestions for markdown components to enhance layout
- **🧠 Polish with Context**: Refine content using optional context notes (conservative mode preserves original format)

#### AI Configuration Tips
- **Ollama**: Ensure Ollama is running locally (http://localhost:11434). Click "Fetch Models" to load available models.
- **Cloud Providers**: Enter your API key in the sidebar. Keys are session-only by default for security.
- **Error Debugging**: AI actions now show detailed error messages with engine, model, and URL info for troubleshooting.

### Image Source Options

Choose from multiple image sources:
- **Pollinations (AI)** - AI-generated images from text prompts
- **Picsum (Stock)** - Random high-quality stock photos
- **Placeholder (Text)** - Text placeholders for layout planning
- **Gradients (8 styles)** - Beautiful CSS gradients: Blue, Purple, Sunset, Ocean, Forest, Aurora, Fire, Midnight
- **Patterns** - Real SVG-based patterns: Dots, Lines

### Export Options

- **HTML Export**: Export as clean HTML
- **PDF Export**: Export as PDF (requires PDF library)
- **WeChat Format**: Optimized for WeChat publishing

### Smoke Test Checklist (EN / 中文)
- File load/delete/history buttons work; file info shows; saving creates/updates the file.
- AI engine set → each AI action runs; buttons disable while running; toasts/spinners show; output updates.
- Empty编辑器/Editor empty → AI actions show “Please add text” toast; no spinner/no crash.
- Rapid double-click on AI buttons is debounced; “another action running” toast appears if busy.
- Language toggle EN/中文 keeps AI config (engine/key/model) unchanged.
- “Suggest Components” returns buttons; insert works and toasts appear; clear suggestions works.
- Force Save works when a filename is provided; autosave still functions.

## Dependencies

### Core Dependencies
- `streamlit` - Web framework
- `markdown` - Markdown processing
- `Pillow` - Image processing
- `requests` - HTTP requests

### Optional Dependencies
- `openai` - AI integration
- `reportlab` - PDF generation (recommended)
- `weasyprint` - Alternative PDF generation
- `xhtml2pdf` - Alternative PDF generation
- `pdfkit` - Alternative PDF generation (requires wkhtmltopdf)

## Configuration

### AI Configuration

Configure AI settings in the sidebar using the new Provider Manager:
- **Provider Selection**: Choose from Ollama (local), OpenAI, OpenRouter, Gemini, Anthropic, or DeepSeek
- **API Host**: Enter the API endpoint URL
- **API Key**: Enter your API key (stored securely with configurable security levels)
- **Model Selection**: Choose from available models (click "Fetch Models" to load from provider)
- **Security Options**: Choose security level for API key storage:
  - Session Only (Level 1): Key lost when browser closes
  - Encrypted Local (Level 2): Key stored encrypted on disk
  - Never Save (Level 0, default for cloud): Key never persisted

### Image Source Options

Choose from multiple image sources for your content:
- **Pollinations (AI)** - AI-generated images from text prompts
- **Picsum (Stock)** - Random high-quality stock photos
- **Placeholder (Text)** - Text placeholders for layout planning
- **Gradients (8 styles)** - Beautiful CSS gradients:
  - Gradient (Blue) - Blue to purple gradient
  - Gradient (Purple) - Purple gradient
  - Gradient (Sunset) - Orange to red gradient
  - Gradient (Ocean) - Cyan to blue gradient
  - Gradient (Forest) - Green gradient
  - Gradient (Aurora) - Aurora borealis style
  - Gradient (Fire) - Red to yellow gradient
  - Gradient (Midnight) - Dark blue gradient
- **Patterns** - Real SVG-based patterns:
  - Pattern (Dots) - Polka dots pattern on grey background
  - Pattern (Lines) - Diagonal lines pattern on grey background

All images use consistent 800x450 (16:9) aspect ratio for visual consistency.

Install at least one PDF library:
```bash
pip install reportlab  # Recommended (pure Python, no system deps)
```

## Plugins

Create custom plugins by:
1. Copy `plugins/example_callout.py` as a template
2. Modify the `PLUGIN_METADATA` dictionary
3. Implement the `render()` function
4. Save in the `plugins/` directory
5. Restart MarkPolish Studio

See `plugins/README.md` for detailed plugin documentation.

## Troubleshooting

### PDF Export Not Working
- Install a PDF library: `pip install reportlab`
- Check error messages in the UI

### AI Features Not Working
- Install OpenAI: `pip install openai`
- Check API key configuration
- Verify network connection
- **For Ollama users**: 
  - Ensure Ollama is running: `ollama serve`
  - Check Ollama URL is correct (default: http://localhost:11434/v1)
  - Click "Test Connection" to verify Ollama is accessible
  - Click "Fetch Models" to load available local models
  - Check browser console for specific error messages (engine, model, URL shown in UI)
- **Common errors**: 
  - "NameError: context_text" - Fixed in V1.1
  - "Ollama models not fetching" - Fixed in V1.1 (now actually fetches from API)
  - "Connection Failed" - Check Ollama is running locally

### Images Not Loading
- Check image file paths
- Ensure images are in `projects/images/` directory
- Check file permissions

## Development

### Code Structure

The codebase is organized into modules:
- **app.py**: Main UI and orchestration
- **ai_provider_manager.py**: NEW - Multi-provider AI management with secure key storage
- **ai_integration.py**: AI features with Ollama fixes and improved prompts
- **content_processing.py**: Content processing
- **file_operations.py**: File management
- **pdf_generator.py**: PDF generation
- **image_handling.py**: Image operations
- **config.py**: Configuration and constants

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License

Copyright (c) 2024-2026 MarkPolish Studio contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Support

For issues, questions, or contributions, please [add your support contact information].

## Version

MarkPolish Studio V1.1 - Content Ops Edition (AI & UI Improvements)


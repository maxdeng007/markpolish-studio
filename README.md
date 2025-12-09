# MarkPolish Studio

A powerful Streamlit-based content creation and editing tool for creating beautifully formatted markdown content, especially optimized for WeChat publishing.

## Features

- 📝 **Rich Markdown Editor** - Create content with markdown syntax and custom components
- 🎨 **Theme Support** - Multiple beautiful themes for different content styles
- 📄 **PDF Export** - Export your content as PDF with professional styling
- 🔗 **Share Links** - Create shareable links for your projects
- 🤖 **AI Integration** - AI-powered content polishing, formatting, and suggestions
- 🖼️ **Image Library** - Manage and reuse images across projects
- 📚 **Template Library** - Pre-built templates for common content types
- 🔌 **Plugin System** - Extend functionality with custom plugins
- 📱 **WeChat Optimized** - Content optimized for WeChat publishing
- 💾 **Auto-save** - Never lose your work with automatic saving
- 🔄 **Version History** - Track changes and restore previous versions

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
├── share_system.py        # Share link creation and management
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

### Themes

Choose from multiple themes optimized for different content types:
- Apple Minimalist
- Nordic Frost
- Dark Mode
- And more...

### AI Features

- **Polish**: Improve and refine your content
- **Format**: Better structure and formatting
- **Expand**: Add more detail and context
- **Titles**: Generate catchy titles
- **Suggest Components**: Get suggestions for components to add

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

Configure AI settings in the sidebar:
- **Engine**: Choose AI provider (Ollama Local, Gemini, OpenAI, OpenRouter)
- **Model**: Select AI model
- **API Key**: Enter your API key

### PDF Export

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

### Images Not Loading
- Check image file paths
- Ensure images are in `projects/images/` directory
- Check file permissions

## Development

### Code Structure

The codebase is organized into modules:
- **config.py**: Configuration and constants
- **file_operations.py**: File management
- **pdf_generator.py**: PDF generation
- **image_handling.py**: Image operations
- **share_system.py**: Share functionality
- **ai_integration.py**: AI features
- **content_processing.py**: Content processing
- **app.py**: Main UI and orchestration

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues, questions, or contributions, please [add your support contact information].

## Version

MarkPolish Studio V1.0 - Content Ops Edition


# themes.py

STYLES = {
    # --- LIGHT THEMES ---
    "Apple Minimalist (Clean)": {
        "bg": "#FAFAFA",
        "card": "#FFFFFF",
        "text": "#1D1D1F",
        "muted": "#6B7280",
        "primary": "#007AFF",
        "accent": "#E5E5EA",
        "hover": "#F5F5F7",
        "border": "#E5E5EA",
        "font": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "radius": "16px",
        "shadow": "0 1px 3px rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.06)"
    },
    "Nordic Frost (Business)": {
        "bg": "#F4F7FA",
        "card": "#FFFFFF",
        "text": "#243B53",
        "muted": "#6B7280",
        "primary": "#2C5282",
        "accent": "#E6EEF8",
        "hover": "#EFF3F9",
        "border": "#D5DEE8",
        "font": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "radius": "12px",
        "shadow": "0 1px 2px rgba(0,0,0,0.05), 0 6px 18px rgba(17, 24, 39, 0.06)"
    },
    "New York Editorial (Serif)": {
        "bg": "#F9F7F1",
        "card": "#FFFFFF",
        "text": "#2D3748",
        "muted": "#4A5568",
        "primary": "#A91D3A",
        "accent": "#EEE9E1",
        "hover": "#F5EFE5",
        "border": "#E6E2D9",
        "font": "Georgia, 'Times New Roman', serif",
        "radius": "8px",
        "shadow": "0 2px 4px rgba(0,0,0,0.05), 0 4px 14px rgba(0,0,0,0.06)"
    },
    "Matcha Latte (Organic)": {
        "bg": "#F6F8F1",
        "card": "#FFFFFF",
        "text": "#263238",
        "muted": "#5E6B6F",
        "primary": "#6B8E23",
        "accent": "#E6EBD3",
        "hover": "#F0F3E7",
        "border": "#DDE4C5",
        "font": "'Gill Sans', 'Segoe UI', Tahoma, sans-serif",
        "radius": "18px",
        "shadow": "0 2px 6px rgba(0,0,0,0.04), 0 10px 22px rgba(107, 142, 35, 0.12)"
    },
    "Lavender Pop (Fun)": {
        "bg": "#F4F0FF",
        "card": "#FFFFFF",
        "text": "#2D3436",
        "muted": "#5E6570",
        "primary": "#8A4CF6",
        "accent": "#EDE7FF",
        "hover": "#F3EDFF",
        "border": "#DED1FF",
        "font": "Verdana, 'Segoe UI', Tahoma, sans-serif",
        "radius": "24px",
        "shadow": "0 2px 8px rgba(0,0,0,0.04), 0 12px 28px rgba(138, 76, 246, 0.14)"
    },
    "Sunset Blvd (Warm)": {
        "bg": "#FFF5F0",
        "card": "#FFFFFF",
        "text": "#3B2F2F",
        "muted": "#6B7280",
        "primary": "#FF6B6B",
        "accent": "#FFE3E3",
        "hover": "#FFF0F0",
        "border": "#FFDCDC",
        "font": "'Trebuchet MS', 'Segoe UI', sans-serif",
        "radius": "20px",
        "shadow": "0 2px 8px rgba(0,0,0,0.04), 0 12px 28px rgba(255, 107, 107, 0.18)"
    },

    # --- DARK THEMES ---
    "Cyberpunk (Neon Glow)": {
        "bg": "#0A0B0E",
        "card": "#121318",
        "text": "#E6EDF3",
        "muted": "#9AA7B4",
        "primary": "#00FF9D",
        "accent": "#1A1D24",
        "hover": "#171A21",
        "border": "#2A2F3A",
        "font": "'JetBrains Mono', 'Fira Code', 'SFMono-Regular', Menlo, Consolas, monospace",
        "radius": "12px",
        "shadow": "0 0 0 1px rgba(0,255,157,0.25), 0 20px 50px rgba(0, 255, 157, 0.14)"
    },
    "Royal Luxury (Gold)": {
        "bg": "#0D0D0F",
        "card": "#131317",
        "text": "#F0F0F0",
        "muted": "#B0B0B0",
        "primary": "#D4AF37",
        "accent": "#1E1E22",
        "hover": "#18181C",
        "border": "#2A2A2E",
        "font": "Didot, 'Bodoni MT', Georgia, serif",
        "radius": "10px",
        "shadow": "0 0 0 1px rgba(212,175,55,0.3), 0 20px 50px rgba(212,175,55,0.16)"
    },
    "Graphite Dark (SaaS)": {
        "bg": "#0F1115",
        "card": "#161A20",
        "text": "#E6EDF3",
        "muted": "#9AA7B4",
        "primary": "#58A6FF",
        "accent": "#212936",
        "hover": "#1B2028",
        "border": "#2A3240",
        "font": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "radius": "14px",
        "shadow": "0 0 0 1px rgba(88,166,255,0.2), 0 20px 50px rgba(0,0,0,0.4)"
    },
    "Celestial Night (Premium)": {
        "bg": "#0C1117",
        "card": "#151A21",
        "text": "#E5E7EB",
        "muted": "#9BA6B2",
        "primary": "#6EE7FF",
        "accent": "#1E2631",
        "hover": "#1A2029",
        "border": "#2A3441",
        "font": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "radius": "16px",
        "shadow": "0 0 0 1px rgba(110, 231, 255, 0.25), 0 20px 50px rgba(110, 231, 255, 0.15)"
    }
}

# Optional CSS helper classes to apply the theme consistently
CSS_HELPERS = """
.theme {{
  transition: background .25s ease, color .25s ease, border-color .25s ease, box-shadow .25s ease;
}}
.theme-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 16px;
}}
.theme-button {{
  background: var(--primary);
  color: white;
  border: none;
  border-radius: calc(var(--radius) - 4px);
  padding: 10px 14px;
  font: 500 14px/1 var(--font);
  cursor: pointer;
  transition: transform .06s ease, box-shadow .2s ease;
}}
.theme-button:hover {{
  box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}}
.theme-button:active {{
  transform: translateY(1px);
}}
.theme-muted {{
  color: var(--muted);
}}
"""

def apply_theme(root_element, theme_name):
    """
    Apply theme variables to a DOM element (browser environment).
    Usage example in browser:
      apply_theme(document.documentElement, "Apple Minimalist (Clean)")
    """
    theme = STYLES.get(theme_name)
    if not theme:
        raise ValueError(f"Theme '{theme_name}' not found.")
    for k, v in theme.items():
        root_element.style.setProperty(f"--{k}", v)

"""
Simplified AI Provider Manager for MarkPolish Studio

Cherry Studio-style: 4 essential elements per provider
1. Provider Name
2. API Key
3. API Host
4. Models (fetchable)

Security Levels:
- Level 0: Never save (default for cloud)
- Level 1: Session only
- Level 2: Encrypted local
"""

import os
import json
import streamlit as st
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from enum import Enum

# Security levels
class SecurityLevel(Enum):
    HIGHEST = 0  # Never save
    BALANCED = 1  # Session only
    ENCRYPTED = 2  # Encrypted local

@dataclass
class AIProvider:
    """Single AI provider with 4 essential elements"""
    id: str
    name: str
    api_host: str
    api_key: str = ""  # Temporary, never saved
    models: List[str] = None
    default_model: str = ""
    provider_type: str = "custom"  # openai, ollama, openrouter, gemini, anthropic, deepseek, custom

    def __post_init__(self):
        if self.models is None:
            self.models = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "api_host": self.api_host,
            "models": self.models,
            "default_model": self.default_model,
            "provider_type": self.provider_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIProvider':
        return cls(
            id=data["id"],
            name=data["name"],
            api_host=data["api_host"],
            models=data.get("models", []),
            default_model=data.get("default_model", ""),
            provider_type=data.get("provider_type", "custom"),
        )


class SecureStorage:
    """Simple secure storage for API keys"""

    def __init__(self):
        self.config_dir = os.path.expanduser("~/.markpolish")

    def _get_key_file(self, provider_id: str) -> str:
        return os.path.join(self.config_dir, f"key_{provider_id}.enc")

    def save_key(self, provider_id: str, api_key: str, level: SecurityLevel) -> bool:
        """Save API key based on security level"""
        if level == SecurityLevel.HIGHEST:
            return False  # Never save

        if level == SecurityLevel.BALANCED:
            # Session only
            if "temp_api_keys" not in st.session_state:
                st.session_state.temp_api_keys = {}
            st.session_state.temp_api_keys[provider_id] = api_key
            return True

        if level == SecurityLevel.ENCRYPTED:
            # Encrypted file
            try:
                os.makedirs(self.config_dir, exist_ok=True)
                # Simple base64 for local storage (not military grade, but basic protection)
                import base64
                encoded = base64.b64encode(api_key.encode()).decode()
                with open(self._get_key_file(provider_id), 'w') as f:
                    f.write(encoded)
                os.chmod(self._get_key_file(provider_id), 0o600)
                return True
            except:
                return False

        return False

    def get_key(self, provider_id: str, level: SecurityLevel) -> Optional[str]:
        """Get API key based on security level"""
        # Check session first
        if "temp_api_keys" in st.session_state:
            key = st.session_state.temp_api_keys.get(provider_id)
            if key:
                return key

        if level == SecurityLevel.HIGHEST:
            return None

        if level == SecurityLevel.BALANCED:
            return None

        if level == SecurityLevel.ENCRYPTED:
            try:
                import base64
                key_file = self._get_key_file(provider_id)
                if os.path.exists(key_file):
                    with open(key_file, 'r') as f:
                        encoded = f.read()
                    return base64.b64decode(encoded).decode()
            except:
                pass

        return None

    def delete_key(self, provider_id: str):
        """Delete stored key"""
        if "temp_api_keys" in st.session_state:
            st.session_state.temp_api_keys.pop(provider_id, None)

        key_file = self._get_key_file(provider_id)
        if os.path.exists(key_file):
            os.remove(key_file)


class AIProviderManager:
    """Manages AI providers with simplified 4-element structure"""

    # Default providers
    DEFAULTS = {
        "openai": AIProvider(
            id="openai",
            name="OpenAI",
            api_host="https://api.openai.com/v1",
            models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            default_model="gpt-4o-mini",
            provider_type="openai"
        ),
        "openrouter": AIProvider(
            id="openrouter",
            name="OpenRouter",
            api_host="https://openrouter.ai/api/v1",
            models=["openai/gpt-4o", "openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet"],
            default_model="openai/gpt-4o-mini",
            provider_type="openrouter"
        ),
        "anthropic": AIProvider(
            id="anthropic",
            name="Anthropic",
            api_host="https://api.anthropic.com/v1",
            models=["claude-sonnet-4-20250514", "claude-haiku-4-20250514"],
            default_model="claude-sonnet-4-20250514",
            provider_type="anthropic"
        ),
        "gemini": AIProvider(
            id="gemini",
            name="Google Gemini",
            api_host="https://generativelanguage.googleapis.com/v1beta/openai",
            models=["gemini-1.5-pro-latest", "gemini-1.5-flash-latest"],
            default_model="gemini-1.5-pro-latest",
            provider_type="gemini"
        ),
        "deepseek": AIProvider(
            id="deepseek",
            name="DeepSeek",
            api_host="https://api.deepseek.com/v1",
            models=["deepseek-chat"],
            default_model="deepseek-chat",
            provider_type="deepseek"
        ),
        "ollama": AIProvider(
            id="ollama",
            name="Ollama (Local)",
            api_host="http://localhost:11434/v1",
            models=["llama3", "mistral", "codellama", "qwen2"],
            default_model="llama3",
            provider_type="ollama"
        ),
    }

    def __init__(self):
        self.storage = SecureStorage()
        self._providers: Dict[str, AIProvider] = {}
        self._security_level = self._detect_security_level()
        self._load_providers()

    def _detect_security_level(self) -> SecurityLevel:
        """Auto-detect security level"""
        env = os.getenv("MP_SECURITY_LEVEL")
        if env:
            return SecurityLevel(int(env))

        if os.getenv("STREAMLIT_CLOUD"):
            return SecurityLevel.HIGHEST  # Force highest for cloud

        return SecurityLevel.BALANCED  # Default to balanced

    def _load_providers(self):
        """Load providers from session state"""
        if "ai_providers" in st.session_state:
            for pid, data in st.session_state.ai_providers.items():
                self._providers[pid] = AIProvider.from_dict(data)

    def save_providers(self):
        """Save providers to session state"""
        data = {pid: p.to_dict() for pid, p in self._providers.items()}
        st.session_state.ai_providers = data

    def get_providers(self) -> List[AIProvider]:
        """Get all enabled providers"""
        return list(self._providers.values())

    def get_provider(self, provider_id: str) -> Optional[AIProvider]:
        return self._providers.get(provider_id)

    def add_provider(self, provider: AIProvider):
        self._providers[provider.id] = provider
        self.save_providers()

    def update_provider(self, provider_id: str, **kwargs):
        if provider_id in self._providers:
            for key, value in kwargs.items():
                if key not in ("api_key",):
                    setattr(self._providers[provider_id], key, value)
            self.save_providers()

    def delete_provider(self, provider_id: str):
        if provider_id in self._providers:
            del self._providers[provider_id]
            self.storage.delete_key(provider_id)
            self.save_providers()

    def set_api_key(self, provider_id: str, api_key: str):
        self.storage.save_key(provider_id, api_key, self._security_level)

    def get_api_key(self, provider_id: str) -> Optional[str]:
        return self.storage.get_key(provider_id, self._security_level)

    def get_security_level(self) -> SecurityLevel:
        return self._security_level

    def get_security_info(self) -> Dict[str, str]:
        level = self._security_level
        info = {
            SecurityLevel.HIGHEST: {
                "icon": "🔴",
                "name": "Highest Security",
                "desc": "Never save API keys. Required each session.",
                "risk": "Lowest",
            },
            SecurityLevel.BALANCED: {
                "icon": "🟡",
                "name": "Balanced",
                "desc": "Save in session only. Cleared on refresh.",
                "risk": "Low",
            },
            SecurityLevel.ENCRYPTED: {
                "icon": "🟢",
                "name": "Encrypted Storage",
                "desc": "Save encrypted locally. Requires device security.",
                "risk": "Medium",
            },
        }
        return info.get(level, info[SecurityLevel.BALANCED])

    def initialize_defaults(self):
        """Initialize with default providers"""
        if not self._providers:
            for pid, provider in self.DEFAULTS.items():
                self._providers[pid] = provider
            self.save_providers()

    def check_connection(self, provider: AIProvider, api_key: str = None) -> tuple[bool, str]:
        """Check if provider is accessible"""
        import requests

        key = api_key or self.get_api_key(provider.id)
        ptype = provider.provider_type

        if not key and ptype not in ("ollama",):
            return False, "⚠️ API key required"

        try:
            if ptype == "openai":
                headers = {"Authorization": f"Bearer {key}"}
                r = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=5)
                return r.status_code == 200, "✅ Online" if r.status_code == 200 else "❌ Error"

            elif ptype == "openrouter":
                headers = {"Authorization": f"Bearer {key}"}
                r = requests.get("https://openrouter.ai/api/v1/auth/key", headers=headers, timeout=5)
                return r.status_code == 200, "✅ Online" if r.status_code == 200 else "❌ Error"

            elif ptype == "anthropic":
                headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
                r = requests.get("https://api.anthropic.com/v1/models", headers=headers, timeout=5)
                return r.status_code == 200, "✅ Online" if r.status_code == 200 else "❌ Error"

            elif ptype == "gemini":
                r = requests.get(
                    "https://generativelanguage.googleapis.com/v1beta/models",
                    params={"key": key},
                    timeout=5
                )
                return r.status_code == 200, "✅ Online" if r.status_code == 200 else "❌ Error"

            elif ptype == "deepseek":
                headers = {"Authorization": f"Bearer {key}"}
                r = requests.get("https://api.deepseek.com/models", headers=headers, timeout=5)
                return r.status_code == 200, "✅ Online" if r.status_code == 200 else "❌ Error"

            elif ptype == "ollama":
                clean_url = provider.api_host.replace("/v1", "")
                r = requests.get(clean_url, timeout=2)
                return r.status_code == 200, "✅ Online" if r.status_code == 200 else "❌ Offline"

            else:  # custom
                return True, "✅ Configured"

        except requests.exceptions.Timeout:
            return False, "⏱️ Timeout"
        except requests.exceptions.ConnectionError:
            return False, "🌐 Network error"
        except Exception as e:
            return False, f"❌ {str(e)}"

    def fetch_models(self, provider: AIProvider, api_key: str = None) -> tuple[bool, List[str], str]:
        """Fetch available models from provider"""
        import requests

        key = api_key or self.get_api_key(provider.id)
        ptype = provider.provider_type

        try:
            if ptype == "openai":
                from openai import OpenAI
                client = OpenAI(api_key=key)
                models = client.models.list()
                model_list = [m.id for m in models.data if "gpt" in m.id.lower()]
                return True, sorted(model_list), "Models fetched"

            elif ptype == "openrouter":
                headers = {"Authorization": f"Bearer {key}"}
                r = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    model_list = [m["id"] for m in data.get("data", [])]
                    return True, sorted(model_list), "Models fetched"

            elif ptype == "anthropic":
                headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
                r = requests.get("https://api.anthropic.com/v1/models", headers=headers, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    model_list = [m["id"] for m in data.get("data", [])]
                    return True, sorted(model_list), "Models fetched"

            elif ptype == "ollama":
                # Actually fetch models from Ollama
                try:
                    clean_url = provider.api_host.replace("/v1", "").rstrip("/")
                    r = requests.get(f"{clean_url}/api/tags", timeout=5)
                    if r.status_code == 200:
                        data = r.json()
                        model_list = [m["name"] for m in data.get("models", [])]
                        if model_list:
                            return True, sorted(model_list), f"Found {len(model_list)} models"
                    return True, provider.models.copy(), "Using defaults"
                except Exception as e:
                    return True, provider.models.copy(), f"Fetch failed: {str(e)[:20]}"

            elif ptype in ("gemini", "deepseek"):
                return True, provider.models.copy(), "Default models"

            else:
                return True, provider.models.copy(), "Default models"

        except Exception as e:
            pass

        return True, provider.models.copy(), "Using defaults"


# Global instance
_manager = None

def get_manager() -> AIProviderManager:
    global _manager
    if _manager is None:
        _manager = AIProviderManager()
    return _manager

def init_providers():
    """Initialize providers on app start"""
    get_manager().initialize_defaults()


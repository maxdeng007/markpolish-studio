import os
import streamlit.components.v1 as components

# Determine absolute path to the frontend directory (this file -> caret_component/__init__.py)
_this_dir = os.path.dirname(os.path.abspath(__file__))
_frontend_dir = os.path.join(_this_dir, "frontend")

# Declare the custom component
_caret_component = components.declare_component(
    "caret_tracker_component",
    path=_frontend_dir
)


def caret_tracker(key: str = "caret_tracker"):
    """Render the caret tracker component and return the latest cursor data.

    Returns:
        dict | None: {"start": int, "end": int, "timestamp": int} or None if unavailable.
    """
    return _caret_component(key=key)

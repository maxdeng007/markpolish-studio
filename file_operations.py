"""
File operations module for MarkPolish Studio
Handles project save/load, version history, auto-save, and undo/redo functionality
"""

import os
import json
import time
import hashlib
import streamlit as st
import difflib
from datetime import datetime, timedelta

# Import error handler if available
try:
    from error_handler import ErrorHandler
except ImportError:
    ErrorHandler = None

# Import performance optimizer if available
try:
    from performance import PerformanceOptimizer
except ImportError:
    PerformanceOptimizer = None


def save_project(name, content):
    """Save project with improved error handling"""
    if not name: 
        return "⚠️ Name required"
    
    filepath = f"projects/{name}.md"
    
    try:
        # Ensure projects directory exists
        os.makedirs("projects", exist_ok=True)
        
        # Save file
        with open(filepath, "w", encoding="utf-8") as f: 
            f.write(content)
    except Exception as e:
        # If save fails, return error message
        if ErrorHandler:
            ErrorHandler.log_error("save_project", e, {"project": name})
            success, message = ErrorHandler.handle_file_error("save", e)
            return message
        return f"❌ Failed to save: {str(e)}"
    
    # Clear auto-save after manual save
    clear_auto_save(name)
    st.session_state.current_project_name = name
    
    # Save version history (don't fail if this errors)
    if st.session_state.get("version_history_enabled", True):
        try:
            save_version(name, content)
        except Exception as e:
            # Log but don't fail the save
            if ErrorHandler:
                ErrorHandler.log_error("save_version", e, {"project": name})
    
    return f"✅ Saved {name}.md"


def load_project(filename):
    """Load project with improved error handling"""
    filepath = f"projects/{filename}"
    
    try:
        if not os.path.exists(filepath):
            if ErrorHandler:
                return None, f"File `{filename}` not found. It may have been moved or deleted."
            return None, "File not found"
        
        with open(filepath, "r", encoding="utf-8") as f: 
            content = f.read()
        return content, None
    
    except Exception as e:
        if ErrorHandler:
            ErrorHandler.log_error("load_project", e, {"filename": filename, "filepath": filepath})
            success, message = ErrorHandler.handle_file_error("load", e, filepath)
            return None, message
        return None, f"Failed to load: {str(e)}"


# --- VERSION HISTORY ---

def get_version_file_path(project_name):
    """Get path to version history file for a project"""
    return f"projects/{project_name}.versions.json"


def save_version(project_name, content):
    """Save a version snapshot with smart storage (stores full content for reliability)"""
    if not project_name:
        return
    
    version_file = get_version_file_path(project_name)
    max_versions = st.session_state.get("max_versions", 50)
    max_age_days = st.session_state.get("max_version_age_days", 30)
    
    # Load existing versions
    versions = []
    if os.path.exists(version_file):
        try:
            with open(version_file, "r", encoding="utf-8") as f:
                versions = json.load(f)
        except:
            versions = []
    
    # Check if content actually changed (compare with last version)
    if versions:
        last_version = versions[-1]
        if last_version.get("full_content") == content:
            # No change, don't save duplicate version
            return
    
    # Determine storage method based on content size (optimize for large files)
    content_size = len(content)
    use_diff_storage = (PerformanceOptimizer and 
                       st.session_state.get("version_use_diffs", True) and 
                       content_size > 5000 and 
                       len(versions) > 0)
    
    # Create new version entry
    new_version = {
        "timestamp": time.time(),
        "size": content_size
    }
    
    if use_diff_storage:
        # Store diff instead of full content for large files
        last_full_content = None
        for v in reversed(versions):
            if v.get("full_content"):
                last_full_content = v.get("full_content")
                break
        
        if last_full_content:
            diff = PerformanceOptimizer.calculate_diff(last_full_content, content)
            if diff and len(diff) < content_size * 0.8:  # Only use diff if it's smaller
                new_version["diff"] = diff
            else:
                # Diff is larger than content, store full content
                new_version["full_content"] = content
        else:
            # No base to diff against, store full content
            new_version["full_content"] = content
    else:
        # Store full content (for small files or first version)
        new_version["full_content"] = content
    
    versions.append(new_version)
    
    # Cleanup old versions
    cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
    versions = [v for v in versions if v.get("timestamp", 0) > cutoff_time]
    
    # Limit number of versions
    if len(versions) > max_versions:
        versions = versions[-max_versions:]
    
    # Save versions
    try:
        with open(version_file, "w", encoding="utf-8") as f:
            json.dump(versions, f, indent=2)
    except Exception as e:
        if ErrorHandler:
            ErrorHandler.log_error("save_version", e, {"project": project_name})
            # Don't show error to user for version history failures
        else:
            st.error(f"Failed to save version: {e}")


def calculate_diff(old_content, new_content):
    """Calculate unified diff between two versions"""
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm='', n=0))
    return ''.join(diff)


def restore_content_from_version(version_data, all_versions=None):
    """Restore full content from a version (using diff or full content) with performance optimization"""
    if "full_content" in version_data:
        return version_data["full_content"]
    
    # If we have diff, reconstruct from base version
    if "diff" in version_data and PerformanceOptimizer and all_versions:
        # Find the base version (last version with full_content before this one)
        version_index = None
        for i, v in enumerate(all_versions):
            if v == version_data:
                version_index = i
                break
        
        if version_index is not None:
            # Find base content
            for i in range(version_index - 1, -1, -1):
                base_version = all_versions[i]
                if base_version.get("full_content"):
                    base_content = base_version.get("full_content")
                    # Apply diff
                    reconstructed = PerformanceOptimizer.apply_diff(base_content, version_data["diff"])
                    if reconstructed:
                        return reconstructed
                    break
            
            # If no base found, try to reconstruct from any full_content version
            for v in reversed(all_versions[:version_index]):
                if v.get("full_content"):
                    base_content = v.get("full_content")
                    reconstructed = PerformanceOptimizer.apply_diff(base_content, version_data["diff"])
                    if reconstructed:
                        return reconstructed
                    break
    
    return version_data.get("full_content", "")


def get_version_history(project_name):
    """Get list of all versions for a project"""
    version_file = get_version_file_path(project_name)
    if not os.path.exists(version_file):
        return []
    
    try:
        with open(version_file, "r", encoding="utf-8") as f:
            versions = json.load(f)
        return versions
    except:
        return []


def restore_version(project_name, version_index):
    """Restore content from a specific version (handles both full content and diffs)"""
    versions = get_version_history(project_name)
    if version_index < 0 or version_index >= len(versions):
        return None
    
    version = versions[version_index]
    # Use optimized restoration that handles diffs
    restored = restore_content_from_version(version, all_versions=versions)
    return restored if restored else None


def get_version_storage_size(project_name):
    """Get storage size of version history file"""
    version_file = get_version_file_path(project_name)
    if os.path.exists(version_file):
        return os.path.getsize(version_file)
    return 0


# --- AUTO-SAVE ---

def auto_save(content, project_name=None):
    """Auto-save content to temporary file
    
    Returns:
        tuple: (success: bool, result: timestamp or None)
    """
    if not project_name:
        project_name = st.session_state.get("current_project_name")
    
    if not project_name:
        return False, None
    
    # Create auto-save filename
    autosave_name = f".autosave_{project_name}.md"
    autosave_path = f"projects/{autosave_name}"
    
    try:
        os.makedirs("projects", exist_ok=True)
        with open(autosave_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Update session state
        timestamp = time.time()
        st.session_state.last_auto_save_time = timestamp
        st.session_state.auto_save_status = "saved"
        return True, timestamp
    except Exception as e:
        if ErrorHandler:
            ErrorHandler.log_error("auto_save", e, {"project": project_name})
        st.session_state.auto_save_status = "error"
        return False, None


def load_auto_save(project_name=None):
    """Load auto-saved content if available and recent (< 24 hours)"""
    if not project_name:
        project_name = st.session_state.get("current_project_name")
    
    if not project_name:
        return None, None
    
    autosave_name = f".autosave_{project_name}.md"
    autosave_path = f"projects/{autosave_name}"
    
    if not os.path.exists(autosave_path):
        return None, None
    
    try:
        # Check if auto-save is recent (within 24 hours)
        file_mtime = os.path.getmtime(autosave_path)
        age_hours = (time.time() - file_mtime) / 3600
        
        if age_hours > 24:
            # Auto-save is too old, delete it
            try:
                os.remove(autosave_path)
            except:
                pass
            return None, None
        
        with open(autosave_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Return content and timestamp
        autosave_time = datetime.fromtimestamp(file_mtime)
        return content, autosave_time
    except Exception as e:
        if ErrorHandler:
            ErrorHandler.log_error("load_auto_save", e, {"project": project_name})
        return None, None


def clear_auto_save(project_name=None):
    """Clear auto-save file"""
    if not project_name:
        project_name = st.session_state.get("current_project_name")
    
    if not project_name:
        return
    
    autosave_name = f".autosave_{project_name}.md"
    autosave_path = f"projects/{autosave_name}"
    
    if os.path.exists(autosave_path):
        try:
            os.remove(autosave_path)
        except Exception as e:
            if ErrorHandler:
                ErrorHandler.log_error("clear_auto_save", e, {"project": project_name})


def cleanup_old_autosave_files():
    """Clean up auto-save files older than 7 days"""
    if not os.path.exists("projects"):
        return
    
    cutoff_time = time.time() - (7 * 24 * 60 * 60)  # 7 days
    
    for filename in os.listdir("projects"):
        if filename.startswith(".autosave_") and filename.endswith(".md"):
            filepath = os.path.join("projects", filename)
            try:
                if os.path.getmtime(filepath) < cutoff_time:
                    os.remove(filepath)
            except Exception:
                pass


# --- UNDO/REDO ---

def push_to_undo_stack(content, undo_stack, max_size=50):
    """Push content to undo stack"""
    # Ensure undo_stack is a list
    if not isinstance(undo_stack, list):
        undo_stack = []
    
    # Calculate hash to avoid duplicates
    content_hash = hashlib.md5(content.encode()).hexdigest()
    
    # Don't add if same as last item (check if last item is a dict with hash)
    if undo_stack:
        last_item = undo_stack[-1]
        # Handle both dict format and legacy string format
        if isinstance(last_item, dict):
            if last_item.get("hash") == content_hash:
                return undo_stack
        elif isinstance(last_item, str):
            # Legacy format: just compare content directly
            if last_item == content:
                return undo_stack
    
    undo_stack.append({
        "content": content,
        "hash": content_hash,
        "timestamp": time.time()
    })
    
    # Limit stack size
    if len(undo_stack) > max_size:
        undo_stack.pop(0)
    
    return undo_stack


def undo_action(undo_stack, redo_stack, current_content):
    """Undo last action"""
    if not undo_stack:
        return current_content
    
    # Move current content to redo stack
    redo_stack.append(current_content)
    
    # Get previous content from undo stack
    previous_content = undo_stack.pop()
    return previous_content.get("content", current_content)


def redo_action(undo_stack, redo_stack, current_content):
    """Redo last undone action"""
    if not redo_stack:
        return current_content
    
    # Move current content to undo stack
    push_to_undo_stack(current_content, undo_stack)
    
    # Get next content from redo stack
    next_content = redo_stack.pop()
    return next_content


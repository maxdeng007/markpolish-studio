"""
Share system module for MarkPolish Studio
Handles share link creation, management, and loading
"""

import os
import json
import time
import hashlib
from file_operations import load_project


def generate_share_id(project_name):
    """Generate a unique share ID for a project"""
    # Create a hash from project name + timestamp for uniqueness
    timestamp = str(time.time())
    combined = f"{project_name}_{timestamp}"
    hash_obj = hashlib.sha256(combined.encode())
    # Use first 12 characters of hash as share ID
    return hash_obj.hexdigest()[:12]


def create_share_link(project_name, permission="read", expires_days=30):
    """Create a shareable link for a project"""
    try:
        share_id = generate_share_id(project_name)
        share_metadata = {
            "share_id": share_id,
            "project_name": project_name,
            "permission": permission,  # "read" or "edit"
            "created_at": time.time(),
            "expires_at": time.time() + (expires_days * 24 * 3600),
            "expires_days": expires_days
        }
        
        # Save share metadata
        share_path = os.path.join("projects", f".share_{share_id}.json")
        with open(share_path, "w", encoding="utf-8") as f:
            json.dump(share_metadata, f)
        
        return share_id, share_metadata
    except Exception as e:
        return None, None


def get_share_metadata(share_id):
    """Get share metadata by share ID"""
    try:
        share_path = os.path.join("projects", f".share_{share_id}.json")
        if not os.path.exists(share_path):
            return None
        
        with open(share_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        # Check if expired
        if time.time() > metadata.get("expires_at", 0):
            return None
        
        return metadata
    except Exception:
        return None


def load_shared_project(share_id):
    """Load a project via share ID"""
    metadata = get_share_metadata(share_id)
    if not metadata:
        return None, None
    
    project_name = metadata.get("project_name")
    if not project_name:
        return None, None
    
    # Load the project content
    content, error = load_project(f"{project_name}.md")
    if error:
        return None, None  # Return None, None on error
    permission = metadata.get("permission", "read")
    
    return content, permission


def get_share_link_url(share_id):
    """Generate the shareable URL query parameter"""
    # Return query parameter - full URL will be constructed with JavaScript
    return f"?share={share_id}"


def list_project_shares(project_name):
    """List all share links for a project"""
    shares = []
    if not os.path.exists("projects"):
        return shares
    
    try:
        for filename in os.listdir("projects"):
            if filename.startswith(".share_") and filename.endswith(".json"):
                share_path = os.path.join("projects", filename)
                try:
                    with open(share_path, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    if metadata.get("project_name") == project_name:
                        # Check if expired
                        if time.time() <= metadata.get("expires_at", 0):
                            shares.append(metadata)
                        else:
                            # Clean up expired share
                            os.remove(share_path)
                except Exception:
                    pass
    except Exception:
        pass
    
    return shares


def delete_share(share_id):
    """Delete a share link"""
    try:
        share_path = os.path.join("projects", f".share_{share_id}.json")
        if os.path.exists(share_path):
            os.remove(share_path)
            return True
    except Exception:
        pass
    return False


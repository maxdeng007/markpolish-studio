"""
Image handling module for MarkPolish Studio
Handles image processing, library management, and image operations
"""

import os
import json
import time
import base64
import hashlib
from io import BytesIO
from PIL import Image
import streamlit as st

# Import error handler if available
try:
    from error_handler import ErrorHandler
except ImportError:
    ErrorHandler = None


def process_image(file, save_to_library=True):
    """Converts uploaded file to Base64 string for embedding and optionally saves to library
    
    Returns:
        Tuple of (shortcode, error_message) where:
        - shortcode: The image shortcode string on success, None on error
        - error_message: Error message string on error, None on success
    """
    if not file: 
        return None, None
    
    try:
        # Read raw bytes for hashing and to avoid pointer issues
        file_bytes = file.read()
        file.seek(0)

        img = Image.open(BytesIO(file_bytes)).convert("RGB")
        if img.width > 800:
            ratio = 800 / img.width
            img = img.resize((800, int(img.height * ratio)))
        
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=70)
        b64 = base64.b64encode(buf.getvalue()).decode()
        
        fid = file.name
        if "local_images" not in st.session_state:
            st.session_state.local_images = {}
        st.session_state.local_images[fid] = f"data:image/jpeg;base64,{b64}"
        
        # Save to image library if requested
        if save_to_library:
            # Ensure images directory exists
            images_dir = os.path.join("projects", "images")
            os.makedirs(images_dir, exist_ok=True)
            
            # Calculate file hash to dedupe uploads
            file_hash = hashlib.md5(file_bytes).hexdigest()

            # Deduplicate: check existing library by hash or original name
            if get_image_library:
                library_images = get_image_library()
                for img_info in library_images:
                    metadata_path = os.path.join(images_dir, f"{img_info['filename']}.json")
                    metadata = {}
                    if os.path.exists(metadata_path):
                        try:
                            with open(metadata_path, "r", encoding="utf-8") as f:
                                metadata = json.load(f)
                        except Exception:
                            pass

                    # Match by hash or original name
                    if metadata.get("file_hash") == file_hash or metadata.get("original_name") == fid:
                        existing_data = load_image_from_library(img_info["filename"])
                        if existing_data:
                            if "local_images" not in st.session_state:
                                st.session_state.local_images = {}
                            # Store under the current reference name so preview finds it
                            st.session_state.local_images[fid] = existing_data
                        return f"[LOCAL: {fid}]", None

            # Create unique filename with timestamp
            timestamp = int(time.time())
            # Preserve file extension
            name_parts = os.path.splitext(fid)
            base_name = "".join(c for c in name_parts[0] if c.isalnum() or c in "._-")[:50]
            ext = name_parts[1] if name_parts[1] else ".jpg"
            # Ensure extension is valid
            if ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif']:
                ext = ".jpg"
            # Include short hash fragment to avoid collisions on rapid uploads
            hash_suffix = file_hash[:6]
            library_filename = f"{timestamp}_{base_name}_{hash_suffix}{ext}"
            library_path = os.path.join(images_dir, library_filename)
            
            # Determine format from extension
            save_format = "JPEG"
            if ext.lower() in ['.png']:
                save_format = "PNG"
            elif ext.lower() in ['.gif']:
                save_format = "GIF"
            
            # Save image to library
            img.save(library_path, format=save_format, quality=85 if save_format == "JPEG" else None)
            
            # Save metadata
            metadata = {
                "original_name": fid,
                "saved_name": library_filename,
                "timestamp": timestamp,
                "size": os.path.getsize(library_path),
                "file_hash": file_hash
            }
            metadata_path = os.path.join(images_dir, f"{library_filename}.json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f)
        
        return f"[LOCAL: {fid}]", None
    except Exception as e:
        if ErrorHandler:
            ErrorHandler.log_error("process_image", e, {"filename": file.name if file else "unknown"})
            success, message = ErrorHandler.handle_image_error("process", e)
            return None, message
        # Fallback error message if ErrorHandler is not available
        return None, f"Failed to process image: {str(e)}"


def get_image_library():
    """Get list of all images in the library"""
    images = []
    images_dir = os.path.join("projects", "images")
    if not os.path.exists(images_dir):
        return images
    
    for filename in os.listdir(images_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            image_path = os.path.join(images_dir, filename)
            metadata_path = os.path.join(images_dir, f"{filename}.json")
            
            # Get metadata if available
            metadata = {}
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                except:
                    pass
            
            # Get file info
            file_stat = os.stat(image_path)
            images.append({
                "filename": filename,
                "path": image_path,
                "original_name": metadata.get("original_name", filename),
                "timestamp": metadata.get("timestamp", file_stat.st_mtime),
                "size": file_stat.st_size
            })
    
    # Sort by timestamp (newest first)
    images.sort(key=lambda x: x["timestamp"], reverse=True)
    return images


def load_image_from_library(filename):
    """Load image from library and return base64 data URI"""
    try:
        image_path = os.path.join("projects", "images", filename)
        if not os.path.exists(image_path):
            return None
        
        with open(image_path, "rb") as f:
            img_data = f.read()
            b64 = base64.b64encode(img_data).decode()
            
            # Determine MIME type
            if filename.lower().endswith('.png'):
                mime = 'image/png'
            elif filename.lower().endswith('.gif'):
                mime = 'image/gif'
            else:
                mime = 'image/jpeg'
            
            return f"data:{mime};base64,{b64}"
    except Exception as e:
        return None


def delete_image_from_library(filename):
    """Delete image and its metadata from library"""
    try:
        image_path = os.path.join("projects", "images", filename)
        metadata_path = os.path.join("projects", "images", f"{filename}.json")
        
        if os.path.exists(image_path):
            os.remove(image_path)
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        
        return True
    except Exception:
        return False


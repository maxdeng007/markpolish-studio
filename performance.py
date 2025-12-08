"""
Performance optimization utilities for MarkPolish Studio
Handles debouncing, caching, and memory management
"""

import time
import hashlib
import difflib
from typing import Optional, Tuple, Dict, Any

class PerformanceOptimizer:
    """Performance optimization utilities"""
    
    def __init__(self):
        self.preview_cache = {}
        self.last_preview_hash = None
        self.last_preview_time = 0
        self.preview_debounce_ms = 500  # 500ms debounce for preview
        
    def should_update_preview(self, content: str) -> bool:
        """
        Determine if preview should be updated based on debouncing
        
        Args:
            content: Current content
            
        Returns:
            True if preview should update, False otherwise
        """
        content_hash = hash(content)
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # If content changed
        if content_hash != self.last_preview_hash:
            # Check if enough time has passed since last update
            time_since_last = current_time - self.last_preview_time
            if time_since_last >= self.preview_debounce_ms:
                self.last_preview_hash = content_hash
                self.last_preview_time = current_time
                return True
            # Content changed but not enough time passed - will update on next check
            self.last_preview_hash = content_hash
            return False
        
        return False
    
    def get_cached_preview(self, content: str) -> Optional[Any]:
        """
        Get cached preview if available and still valid
        
        Args:
            content: Current content
            
        Returns:
            Cached preview HTML or None
        """
        content_hash = hash(content)
        if content_hash in self.preview_cache:
            return self.preview_cache[content_hash]
        return None
    
    def cache_preview(self, content: str, preview_html: str):
        """
        Cache preview HTML for content
        
        Args:
            content: Content that was rendered
            preview_html: Rendered HTML
        """
        content_hash = hash(content)
        self.preview_cache[content_hash] = preview_html
        
        # Limit cache size to prevent memory issues
        if len(self.preview_cache) > 10:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.preview_cache))
            del self.preview_cache[oldest_key]
    
    @staticmethod
    def calculate_diff(old_content: str, new_content: str) -> Optional[str]:
        """
        Calculate diff between two content versions
        
        Args:
            old_content: Previous version
            new_content: New version
            
        Returns:
            Unified diff string or None if content is identical
        """
        if old_content == new_content:
            return None
        
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
            n=3
        )
        
        return ''.join(diff)
    
    @staticmethod
    def apply_diff(base_content: str, diff_str: str) -> Optional[str]:
        """
        Apply diff to base content to reconstruct new content
        
        Args:
            base_content: Base content
            diff_str: Unified diff string
            
        Returns:
            Reconstructed content or None if diff is invalid
        """
        try:
            base_lines = base_content.splitlines(keepends=True)
            diff_lines = diff_str.splitlines(keepends=True)
            
            # Simple diff application (for basic cases)
            # For production, use a proper diff library
            result_lines = []
            i = 0
            for line in diff_lines:
                if line.startswith('---') or line.startswith('+++') or line.startswith('@@'):
                    continue
                elif line.startswith('-'):
                    # Remove line from base
                    if i < len(base_lines):
                        i += 1
                elif line.startswith('+'):
                    # Add new line
                    result_lines.append(line[1:])
                else:
                    # Context line - keep from base
                    if i < len(base_lines):
                        result_lines.append(base_lines[i])
                        i += 1
            
            # Add remaining base lines
            while i < len(base_lines):
                result_lines.append(base_lines[i])
                i += 1
            
            return ''.join(result_lines)
        except Exception:
            return None
    
    @staticmethod
    def optimize_undo_stack(undo_stack: list, max_size: int = 50, max_memory_mb: float = 10.0) -> list:
        """
        Optimize undo stack by limiting size and memory usage
        
        Args:
            undo_stack: Current undo stack
            max_size: Maximum number of entries
            max_memory_mb: Maximum memory in MB
            
        Returns:
            Optimized undo stack
        """
        if not undo_stack:
            return undo_stack
        
        # Limit by count
        if len(undo_stack) > max_size:
            undo_stack = undo_stack[-max_size:]
        
        # Estimate memory usage (rough calculation)
        total_size = sum(len(str(item)) for item in undo_stack)
        memory_mb = total_size / (1024 * 1024)
        
        # If memory usage is too high, reduce stack size
        if memory_mb > max_memory_mb:
            # Keep only most recent entries that fit in memory
            target_size = int(max_size * (max_memory_mb / memory_mb))
            if target_size < 10:
                target_size = 10  # Keep at least 10 entries
            undo_stack = undo_stack[-target_size:]
        
        return undo_stack
    
    @staticmethod
    def estimate_content_size(content: str) -> Dict[str, Any]:
        """
        Estimate content size and complexity
        
        Args:
            content: Content to analyze
            
        Returns:
            Dictionary with size metrics
        """
        size_bytes = len(content.encode('utf-8'))
        lines = len(content.splitlines())
        words = len(content.split())
        images = content.count('[IMG:') + content.count('[LOCAL:')
        components = content.count(':::')
        
        return {
            'size_bytes': size_bytes,
            'size_kb': size_bytes / 1024,
            'size_mb': size_bytes / (1024 * 1024),
            'lines': lines,
            'words': words,
            'images': images,
            'components': components,
            'is_large': size_bytes > 100000,  # > 100KB
            'is_very_large': size_bytes > 1000000  # > 1MB
        }


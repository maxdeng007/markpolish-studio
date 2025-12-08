"""
Error handling utilities for MarkPolish Studio
Provides user-friendly error messages and recovery mechanisms
"""

import streamlit as st
import os
import traceback
from typing import Optional, Callable, Any, Tuple

class ErrorHandler:
    """Centralized error handling with user-friendly messages"""
    
    @staticmethod
    def handle_file_error(operation: str, error: Exception, filepath: str = None) -> Tuple[bool, str]:
        """
        Handle file operation errors with user-friendly messages
        
        Args:
            operation: Type of operation (save, load, delete, etc.)
            error: The exception that occurred
            filepath: Optional file path for context
            
        Returns:
            Tuple of (success, user_message)
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Permission errors
        if "Permission" in error_type or "permission" in error_msg.lower():
            suggestion = "Check file permissions or try saving to a different location."
            if filepath:
                return False, f"❌ **Permission Denied**\n\nCannot {operation} `{os.path.basename(filepath)}`.\n\n💡 {suggestion}"
            return False, f"❌ **Permission Denied**\n\nCannot {operation} file.\n\n💡 {suggestion}"
        
        # Disk space errors
        if "No space" in error_msg or "disk" in error_msg.lower() and "full" in error_msg.lower():
            return False, f"❌ **Disk Full**\n\nCannot {operation} file - not enough disk space.\n\n💡 Free up disk space and try again."
        
        # File not found
        if "No such file" in error_msg or "FileNotFoundError" in error_type:
            if operation == "load":
                return False, f"❌ **File Not Found**\n\nThe file `{os.path.basename(filepath) if filepath else 'requested file'}` doesn't exist.\n\n💡 It may have been moved or deleted."
            return False, f"❌ **File Not Found**\n\nCannot {operation} - file not found."
        
        # Encoding errors
        if "encoding" in error_msg.lower() or "Unicode" in error_type:
            return False, f"❌ **Encoding Error**\n\nCannot {operation} file - contains invalid characters.\n\n💡 Try saving with UTF-8 encoding or remove special characters."
        
        # Generic file errors
        if filepath:
            return False, f"❌ **Failed to {operation.capitalize()}**\n\nError: {error_msg}\n\nFile: `{os.path.basename(filepath)}`\n\n💡 Check file permissions and disk space."
        return False, f"❌ **Failed to {operation.capitalize()}**\n\nError: {error_msg}"
    
    @staticmethod
    def handle_export_error(export_type: str, error: Exception) -> Tuple[bool, str]:
        """
        Handle export operation errors (PDF, HTML, etc.)
        
        Args:
            export_type: Type of export (PDF, HTML, etc.)
            error: The exception that occurred
            
        Returns:
            Tuple of (success, user_message)
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        if export_type.lower() == "pdf":
            # Missing library errors
            if "ImportError" in error_type or "No module" in error_msg:
                return False, (
                    "❌ **PDF Export Unavailable**\n\n"
                    "PDF generation library not installed.\n\n"
                    "💡 **Solution:** Install a PDF library:\n"
                    "```bash\n"
                    "pip install reportlab\n"
                    "```\n\n"
                    "Or try: `pip install weasyprint` or `pip install xhtml2pdf`"
                )
            
            # PDF generation errors
            if "wkhtmltopdf" in error_msg.lower():
                return False, (
                    "❌ **PDF Export Failed**\n\n"
                    "wkhtmltopdf is not installed or not in PATH.\n\n"
                    "💡 **Solution:** Install wkhtmltopdf:\n"
                    "- macOS: `brew install wkhtmltopdf`\n"
                    "- Linux: `sudo apt-get install wkhtmltopdf`\n"
                    "- Or use ReportLab instead (recommended)"
                )
            
            return False, (
                f"❌ **PDF Export Failed**\n\n"
                f"Error: {error_msg}\n\n"
                "💡 **Try:**\n"
                "1. Check if the document is too large\n"
                "2. Try exporting as HTML instead\n"
                "3. Install ReportLab: `pip install reportlab`"
            )
        
        return False, f"❌ **{export_type} Export Failed**\n\nError: {error_msg}"
    
    @staticmethod
    def handle_ai_error(engine: str, error: Exception) -> Tuple[bool, str]:
        """
        Handle AI operation errors
        
        Args:
            engine: AI engine name (OpenRouter, Ollama, etc.)
            error: The exception that occurred
            
        Returns:
            Tuple of (success, user_message)
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        # API key errors
        if "api" in error_msg.lower() and "key" in error_msg.lower():
            return False, (
                "❌ **API Key Error**\n\n"
                "Invalid or missing API key.\n\n"
                "💡 **Solution:**\n"
                "1. Check your API key in Settings\n"
                "2. Make sure the key is correct and has credits\n"
                "3. For OpenRouter, get a key from: https://openrouter.ai"
            )
        
        # Network errors
        if "Connection" in error_type or "timeout" in error_msg.lower():
            return False, (
                f"❌ **Connection Error**\n\n"
                f"Cannot connect to {engine}.\n\n"
                "💡 **Solution:**\n"
                "1. Check your internet connection\n"
                "2. Verify the API endpoint URL\n"
                "3. Try again in a few moments"
            )
        
        # Rate limit errors
        if "rate limit" in error_msg.lower() or "429" in error_msg:
            return False, (
                "❌ **Rate Limit Exceeded**\n\n"
                "Too many requests to the AI service.\n\n"
                "💡 **Solution:**\n"
                "1. Wait a few minutes and try again\n"
                "2. Upgrade your API plan if needed\n"
                "3. Reduce the frequency of requests"
            )
        
        # Model errors
        if "model" in error_msg.lower() and ("not found" in error_msg.lower() or "invalid" in error_msg.lower()):
            return False, (
                "❌ **Model Error**\n\n"
                f"Model not available or invalid.\n\n"
                "💡 **Solution:**\n"
                "1. Check the model name in Settings\n"
                "2. Verify the model is available for your API key\n"
                "3. Try a different model"
            )
        
        # Generic AI errors
        return False, (
            f"❌ **AI Error**\n\n"
            f"Error: {error_msg}\n\n"
            "💡 **Try:**\n"
            "1. Check your API configuration\n"
            "2. Verify your API key is valid\n"
            "3. Try again in a moment"
        )
    
    @staticmethod
    def handle_image_error(operation: str, error: Exception) -> Tuple[bool, str]:
        """
        Handle image processing errors
        
        Args:
            operation: Type of operation (upload, process, save, etc.)
            error: The exception that occurred
            
        Returns:
            Tuple of (success, user_message)
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Unsupported format
        if "cannot identify" in error_msg.lower() or "PIL" in error_type:
            return False, (
                "❌ **Unsupported Image Format**\n\n"
                "The image format is not supported.\n\n"
                "💡 **Supported formats:** JPEG, PNG, GIF, WebP\n"
                "💡 **Solution:** Convert the image to a supported format"
            )
        
        # File too large
        if "too large" in error_msg.lower() or "Memory" in error_type:
            return False, (
                "❌ **Image Too Large**\n\n"
                "The image is too large to process.\n\n"
                "💡 **Solution:**\n"
                "1. Resize the image to under 10MB\n"
                "2. Compress the image before uploading\n"
                "3. Use a smaller resolution"
            )
        
        return False, f"❌ **Image {operation.capitalize()} Failed**\n\nError: {error_msg}"
    
    @staticmethod
    def safe_execute(operation: Callable, error_handler: Callable, *args, **kwargs) -> Tuple[Any, Optional[str]]:
        """
        Safely execute an operation with error handling
        
        Args:
            operation: Function to execute
            error_handler: Error handler function
            *args, **kwargs: Arguments for the operation
            
        Returns:
            Tuple of (result, error_message)
        """
        try:
            result = operation(*args, **kwargs)
            return result, None
        except Exception as e:
            success, message = error_handler(e)
            return None, message
    
    @staticmethod
    def log_error(operation: str, error: Exception, context: dict = None):
        """
        Log error details for debugging (without exposing to user)
        
        Args:
            operation: Operation that failed
            error: The exception
            context: Additional context
        """
        error_details = {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc()
        }
        if context:
            error_details["context"] = context
        
        # Store in session state for debugging (can be accessed via st.session_state.error_log)
        if "error_log" not in st.session_state:
            st.session_state.error_log = []
        st.session_state.error_log.append(error_details)
        
        # Keep only last 10 errors
        if len(st.session_state.error_log) > 10:
            st.session_state.error_log = st.session_state.error_log[-10:]
    
    @staticmethod
    def show_error_with_details(message: str, error: Exception = None, show_details: bool = False):
        """
        Display error message with optional technical details
        
        Args:
            message: User-friendly error message
            error: Optional exception for details
            show_details: Whether to show technical details by default
        """
        if error:
            ErrorHandler.log_error("user_operation", error)
        
        if show_details and error:
            with st.expander("🔍 Technical Details", expanded=False):
                st.code(f"Error Type: {type(error).__name__}\n{str(error)}\n\n{traceback.format_exc()}")
        
        st.error(message)
    
    @staticmethod
    def validate_markdown_syntax(content: str) -> Tuple[bool, list]:
        """
        Validate markdown syntax and return list of issues
        
        Args:
            content: Markdown content to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check for unclosed component tags
        import re
        component_patterns = [
            (r':::\s*hero', r':::', 'Hero component'),
            (r':::\s*col-2', r':::', '2-Column component'),
            (r':::\s*col-3', r':::', '3-Column component'),
            (r':::\s*steps', r':::', 'Steps component'),
            (r':::\s*timeline', r':::', 'Timeline component'),
            (r':::\s*reveal', r'--cover--', 'Reveal component (missing --cover--)'),
        ]
        
        for start_pattern, end_pattern, component_name in component_patterns:
            starts = len(re.findall(start_pattern, content, re.IGNORECASE))
            ends = len(re.findall(end_pattern, content, re.IGNORECASE))
            if starts > ends:
                issues.append(f"Unclosed {component_name} tag (found {starts} opening, {ends} closing)")
        
        # Check for malformed links
        malformed_links = re.findall(r'\[([^\]]*)\]\([^)]*$', content, re.MULTILINE)
        if malformed_links:
            issues.append(f"Malformed link syntax: {len(malformed_links)} found")
        
        return len(issues) == 0, issues


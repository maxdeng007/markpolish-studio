import streamlit.components.v1 as components
import streamlit as st
import time
import json

def create_cursor_tracker():
    """Create a cursor position tracker component that records caret position in the editor textarea"""
    
    # Inject script into main document (not iframe) using parent window access
    # This component will update cursor position in session_state via URL parameters
    cursor_tracker_html = """
    <script>
    (function() {
        // Get the parent window (main Streamlit document)
        const mainWindow = window.parent !== window ? window.parent : window;
        const mainDoc = mainWindow.document;
        
        // Prevent multiple listeners
        if (mainWindow.mpCursorTrackerInitialized) {
            return;
        }
        mainWindow.mpCursorTrackerInitialized = true;
        
        console.log('📍 Cursor tracker initializing...');
        
        // Function to find the editor textarea by its Streamlit key
        function findEditorTextarea() {
            // Try multiple strategies to find the editor textarea
            const textareas = mainDoc.querySelectorAll('textarea');
            
            // Strategy 1: Look for textarea with specific height (editor is 600px)
            for (let textarea of textareas) {
                const style = window.getComputedStyle(textarea);
                const height = parseInt(style.height);
                // Editor is typically 600px, but check for anything > 400px
                if (height > 400) {
                    // Found it - no need to log every time
                    return textarea;
                }
            }
            
            // Strategy 2: Look for textarea in Streamlit textarea container
            for (let textarea of textareas) {
                let parent = textarea.parentElement;
                let depth = 0;
                while (parent && depth < 5) {
                    const testId = parent.getAttribute('data-testid') || '';
                    if (testId.includes('stTextArea') || testId.includes('textInput')) {
                        // Found it
                        return textarea;
                    }
                    parent = parent.parentElement;
                    depth++;
                }
            }
            
            // Strategy 3: Find the largest textarea (editor is usually the biggest)
            let largestTextarea = null;
            let largestHeight = 0;
            for (let textarea of textareas) {
                const style = window.getComputedStyle(textarea);
                const height = parseInt(style.height);
                if (height > largestHeight) {
                    largestHeight = height;
                    largestTextarea = textarea;
                }
            }
            if (largestTextarea && largestHeight > 200) {
                // Found it
                return largestTextarea;
            }
            
            console.warn('⚠️ Could not find editor textarea');
            return null;
        }
        
        // Store cursor data in window object
        if (!mainWindow.mpCursorData) {
            mainWindow.mpCursorData = {
                cursor_start: null,
                cursor_end: null,
                cursor_timestamp: 0,
                last_valid_start: null,  // Store last valid (non-0,0) position
                last_valid_end: null,
                last_valid_timestamp: 0
            };
        }
        
        // Function to update cursor position and sync to Python
        function updateCursorPosition() {
            const textarea = findEditorTextarea();
            if (!textarea) {
                return;
            }
            
            const isFocused = mainDoc.activeElement === textarea;
            let start, end;
            
            // Try to get selection from the textarea
            try {
                start = textarea.selectionStart;
                end = textarea.selectionEnd;
            } catch (e) {
                console.warn('Could not read cursor position:', e);
                return;
            }
            
            const timestamp = Date.now();
            
            // CRITICAL: If textarea is focused, always update (even if 0,0 - it's valid at start)
            // If textarea is NOT focused and position is 0,0, DON'T overwrite last valid position
            if (isFocused) {
                // Textarea is focused - this is a valid reading
                mainWindow.mpCursorData.cursor_start = start;
                mainWindow.mpCursorData.cursor_end = end;
                mainWindow.mpCursorData.cursor_timestamp = timestamp;
                
                // Also store as "last valid" if it's not 0,0 or if text is empty
                if ((start > 0 || end > 0) || textarea.value.length === 0) {
                    mainWindow.mpCursorData.last_valid_start = start;
                    mainWindow.mpCursorData.last_valid_end = end;
                    mainWindow.mpCursorData.last_valid_timestamp = timestamp;
                }
            } else {
                // Textarea is NOT focused
                if (start === 0 && end === 0 && textarea.value.length > 0) {
                    // Don't overwrite with 0,0 when unfocused - use last valid position instead
                    if (mainWindow.mpCursorData.last_valid_start !== null) {
                        start = mainWindow.mpCursorData.last_valid_start;
                        end = mainWindow.mpCursorData.last_valid_end;
                        timestamp = mainWindow.mpCursorData.last_valid_timestamp;
                        console.log('📍 Using last valid cursor position:', start, end, 'instead of 0,0');
                    } else {
                        // No last valid position - skip update
                        return;
                    }
                }
                // Update with the position we decided to use
                mainWindow.mpCursorData.cursor_start = start;
                mainWindow.mpCursorData.cursor_end = end;
                mainWindow.mpCursorData.cursor_timestamp = timestamp;
            }
            
            // Also store in a data attribute on the textarea for immediate access
            textarea.setAttribute('data-cursor-start', start);
            textarea.setAttribute('data-cursor-end', end);
            textarea.setAttribute('data-cursor-ts', timestamp);
            
            // Update URL query params (throttled to avoid quota errors)
            if (!mainWindow.mpCursorUpdatePending) {
                mainWindow.mpCursorUpdatePending = true;
                setTimeout(function() {
                    try {
                        const url = new URL(mainWindow.location.href);
                        url.searchParams.set('_cursor_start', mainWindow.mpCursorData.cursor_start);
                        url.searchParams.set('_cursor_end', mainWindow.mpCursorData.cursor_end);
                        url.searchParams.set('_cursor_ts', mainWindow.mpCursorData.cursor_timestamp);
                        // Update URL without reload
                        mainWindow.history.replaceState({}, '', url.toString());
                        // Only log if position changed significantly (reduce spam)
                        const lastLogged = mainWindow.mpLastLoggedCursor || {start: -1, end: -1};
                        if (Math.abs(start - lastLogged.start) > 5 || Math.abs(end - lastLogged.end) > 5) {
                            console.log('📍 Cursor updated:', start, end, 'focused:', isFocused);
                            mainWindow.mpLastLoggedCursor = {start: start, end: end};
                        }
                    } catch (e) {
                        console.warn('Could not update URL params:', e);
                    }
                    mainWindow.mpCursorUpdatePending = false;
                }, 100); // Throttle to avoid quota errors
            }
        }
        
        // Function to get current cursor position (for button clicks)
        mainWindow.getCurrentCursorPosition = function() {
            const textarea = findEditorTextarea();
            if (!textarea) {
                return null;
            }
            return {
                start: textarea.selectionStart,
                end: textarea.selectionEnd,
                timestamp: Date.now()
            };
        };
        
        // Add event listeners to the textarea
        function attachListeners() {
            const textarea = findEditorTextarea();
            if (!textarea) {
                // Retry after a short delay if textarea not found yet
                setTimeout(attachListeners, 100);
                return;
            }
            
            console.log('✅ Editor textarea found, attaching cursor listeners');
            
            // Update the function to also update the hidden input
            const originalUpdateCursorPosition = updateCursorPosition;
            updateCursorPosition = function() {
                originalUpdateCursorPosition();
                // updateCursorInput is now called within updateCursorPosition
            };
            
            // Listen to various events that indicate cursor movement
            textarea.addEventListener('click', updateCursorPosition, true);
            textarea.addEventListener('keyup', updateCursorPosition, true);
            textarea.addEventListener('keydown', updateCursorPosition, true);
            textarea.addEventListener('mouseup', updateCursorPosition, true);
            textarea.addEventListener('focus', updateCursorPosition, true);
            textarea.addEventListener('input', updateCursorPosition, true);
            textarea.addEventListener('selectionchange', updateCursorPosition, true);
            
            // Also listen to selection changes
            textarea.addEventListener('select', updateCursorPosition, true);
            
            // Listen to selectionchange on document (more reliable)
            mainDoc.addEventListener('selectionchange', function() {
                if (mainDoc.activeElement === textarea) {
                    updateCursorPosition();
                }
            }, true);
            
            // REMOVED: Polling causes too much console spam
            // The event listeners are sufficient
            
            // CRITICAL: Capture cursor position when focus is lost (before clicking buttons)
            // This is the key moment - capture the position RIGHT BEFORE it loses focus
            textarea.addEventListener('blur', function(e) {
                // Capture immediately, before focus moves away
                const start = textarea.selectionStart;
                const end = textarea.selectionEnd;
                const timestamp = Date.now();
                
                // ALWAYS store as last valid position on blur (this is the position user had before clicking button)
                // Even if 0,0 - it's valid if cursor is at start
                mainWindow.mpCursorData.last_valid_start = start;
                mainWindow.mpCursorData.last_valid_end = end;
                mainWindow.mpCursorData.last_valid_timestamp = timestamp;
                
                // Also update current
                mainWindow.mpCursorData.cursor_start = start;
                mainWindow.mpCursorData.cursor_end = end;
                mainWindow.mpCursorData.cursor_timestamp = timestamp;
                
                // Update URL params immediately
                // Also store text length for validation
                try {
                    const url = new URL(mainWindow.location.href);
                    url.searchParams.set('_cursor_start', start);
                    url.searchParams.set('_cursor_end', end);
                    url.searchParams.set('_cursor_ts', timestamp);
                    url.searchParams.set('_text_len', textarea.value.length);
                    // Also store a snippet of text around cursor for validation
                    const textSnippet = textarea.value.substring(Math.max(0, start - 10), Math.min(textarea.value.length, start + 10));
                    url.searchParams.set('_text_snippet', encodeURIComponent(textSnippet));
                    mainWindow.history.replaceState({}, '', url.toString());
                    console.log('📍 Cursor captured on blur (before button click):', start, end, 'text_len:', textarea.value.length, 'text_around_cursor:', textSnippet);
                } catch (e) {
                    console.warn('Could not update URL params on blur:', e);
                }
            }, true);
            
            // Initial update
            updateCursorPosition();
        }
        
        // Start attaching listeners
        // Wait a bit for Streamlit to render the textarea
        setTimeout(attachListeners, 200);
        
        // Also try on DOMContentLoaded if not already loaded
        if (mainDoc.readyState === 'loading') {
            mainDoc.addEventListener('DOMContentLoaded', attachListeners);
        }
        
        // Re-attach if textarea gets recreated (Streamlit reruns)
        const observer = new MutationObserver(function(mutations) {
            const textarea = findEditorTextarea();
            if (textarea && !textarea.hasAttribute('data-cursor-tracked')) {
                textarea.setAttribute('data-cursor-tracked', 'true');
                attachListeners();
            }
        });
        
        observer.observe(mainDoc.body, {
            childList: true,
            subtree: true
        });
        
        // Store cursor position in a hidden input that Python can read
        // This is more reliable than query params for immediate access
        let cursorInput = mainDoc.getElementById('mp-cursor-input');
        if (!cursorInput) {
            cursorInput = mainDoc.createElement('input');
            cursorInput.type = 'hidden';
            cursorInput.id = 'mp-cursor-input';
            cursorInput.name = 'mp-cursor-input';
            mainDoc.body.appendChild(cursorInput);
        }
        
        // Update the hidden input whenever cursor changes
        function updateCursorInput() {
            const textarea = findEditorTextarea();
            if (textarea && cursorInput) {
                const start = textarea.selectionStart;
                const end = textarea.selectionEnd;
                const timestamp = Date.now();
                
                // Store in hidden input as JSON
                cursorInput.value = JSON.stringify({
                    start: start,
                    end: end,
                    timestamp: timestamp
                });
            }
        }
        
        // Intercept ALL button clicks in capture phase to update cursor BEFORE Streamlit processes them
        mainDoc.addEventListener('click', function(e) {
            const target = e.target;
            // Check if clicking any button (we'll be more aggressive)
            if (target.tagName === 'BUTTON' || target.closest('button')) {
                // CRITICAL: Use last valid cursor position if textarea is not focused
                const textarea = findEditorTextarea();
                if (textarea) {
                    const isFocused = textarea === mainDoc.activeElement;
                    let start, end, timestamp;
                    
                    if (isFocused) {
                        // Textarea is focused - read actual position
                        start = textarea.selectionStart;
                        end = textarea.selectionEnd;
                        timestamp = Date.now();
                        
                        // ALWAYS store as last valid when focused (even 0,0 if text is empty or cursor is at start)
                        mainWindow.mpCursorData.last_valid_start = start;
                        mainWindow.mpCursorData.last_valid_end = end;
                        mainWindow.mpCursorData.last_valid_timestamp = timestamp;
                    } else {
                        // Textarea is NOT focused - ALWAYS use last valid position, never read 0,0
                        if (mainWindow.mpCursorData.last_valid_start !== null) {
                            start = mainWindow.mpCursorData.last_valid_start;
                            end = mainWindow.mpCursorData.last_valid_end;
                            timestamp = mainWindow.mpCursorData.last_valid_timestamp;
                            console.log('📍 Using last valid cursor position (textarea not focused):', start, end);
                        } else {
                            // No last valid position - DON'T use 0,0, skip update
                            console.warn('⚠️ No last valid position and textarea not focused - cannot determine cursor position');
                            return; // Don't update with 0,0
                        }
                    }
                    
                    // Update immediately
                    mainWindow.mpCursorData.cursor_start = start;
                    mainWindow.mpCursorData.cursor_end = end;
                    mainWindow.mpCursorData.cursor_timestamp = timestamp;
                    
                    // Update hidden input
                    if (cursorInput) {
                        cursorInput.value = JSON.stringify({
                            start: start,
                            end: end,
                            timestamp: timestamp
                        });
                    }
                    
                    // Update URL params synchronously (critical for button clicks)
                    // Also store text length so Python can validate cursor position
                    try {
                        const url = new URL(mainWindow.location.href);
                        url.searchParams.set('_cursor_start', start);
                        url.searchParams.set('_cursor_end', end);
                        url.searchParams.set('_cursor_ts', timestamp);
                        // Store text length when cursor was captured for validation
                        url.searchParams.set('_text_len', textarea.value.length);
                        // Also store a snippet of text around cursor for validation
                        const textSnippet = textarea.value.substring(Math.max(0, start - 10), Math.min(textarea.value.length, start + 10));
                        url.searchParams.set('_text_snippet', encodeURIComponent(textSnippet));
                        mainWindow.history.replaceState({}, '', url.toString());
                        console.log('📍 Cursor captured before button click:', start, end, 'text_len:', textarea.value.length, 'focused:', isFocused, 'using_last_valid:', !isFocused && mainWindow.mpCursorData.last_valid_start !== null, 'text_around_cursor:', textSnippet);
                    } catch (e) {
                        console.warn('Could not update URL params:', e);
                    }
                }
            }
        }, true); // Capture phase - runs BEFORE target phase
        
        console.log('✅ Cursor tracker initialized');
    })();
    </script>
    <div id="mp-cursor-tracker" style="display: none;"></div>
    """
    
    # Use components.html to inject the script
    components.html(cursor_tracker_html, height=0)
    
    # ALWAYS try to read cursor data from query params (set by JS)
    # This ensures we have the latest cursor position on every render
    query_params = st.query_params
    if "_cursor_start" in query_params and "_cursor_end" in query_params:
        try:
            cursor_start = int(query_params["_cursor_start"])
            cursor_end = int(query_params["_cursor_end"])
            cursor_timestamp = int(query_params.get("_cursor_ts", 0))
            
            # Always update session state if we have valid query params
            # This ensures cursor position is available when button callbacks run
            st.session_state.cursor_start = cursor_start
            st.session_state.cursor_end = cursor_end
            st.session_state.cursor_timestamp = cursor_timestamp
        except (ValueError, TypeError) as e:
            # Silently ignore invalid values
            pass
    
    return None

def get_cursor_position():
    """Get the current cursor position from session state"""
    cursor_start = st.session_state.get("cursor_start")
    cursor_end = st.session_state.get("cursor_end")
    cursor_timestamp = st.session_state.get("cursor_timestamp", 0)
    
    # Check if cursor data is recent (within 5 seconds)
    current_time = time.time() * 1000  # Convert to milliseconds
    is_recent = (current_time - cursor_timestamp) < 5000 if cursor_timestamp else False
    
    if cursor_start is not None and cursor_end is not None and is_recent:
        return cursor_start, cursor_end, cursor_timestamp
    return None, None, None

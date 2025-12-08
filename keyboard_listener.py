import streamlit.components.v1 as components
import streamlit as st

def create_keyboard_listener():
    """Create a keyboard listener component that captures keyboard shortcuts"""
    
    # Inject script into main document (not iframe) using parent window access
    keyboard_html = """
    <script>
    (function() {
        // Get the parent window (main Streamlit document)
        const mainWindow = window.parent !== window ? window.parent : window;
        const mainDoc = mainWindow.document;
        
        // Prevent multiple listeners
        if (mainWindow.mpKeyboardListenerInitialized) {
            console.log('Keyboard listener already initialized');
            return;
        }
        mainWindow.mpKeyboardListenerInitialized = true;
        
        // Detect OS for Cmd vs Ctrl
        const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0 || 
                     navigator.userAgent.toUpperCase().indexOf('MAC') >= 0;
        const modKey = isMac ? 'metaKey' : 'ctrlKey';
        const modKeyName = isMac ? 'Cmd' : 'Ctrl';
        
        console.log('🎹 Keyboard shortcuts initializing in main window... (Mod key: ' + modKeyName + ')');
        
        // Keyboard shortcut handler
        function handleKeyboardShortcut(e) {
            // Check for modifier key first
            if (!e[modKey]) {
                return;
            }
            
            const key = e.key.toLowerCase();
            
            // Handle Ctrl/Cmd + S - Save
            if (key === 's') {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                console.log('💾 Save shortcut triggered');
                triggerAction('save');
                return false;
            }
            
            // Handle Ctrl/Cmd + Z - Undo
            if (key === 'z' && !e.shiftKey) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                console.log('↶ Undo shortcut triggered');
                triggerAction('undo');
                return false;
            }
            
            // Handle Ctrl/Cmd + Shift + Z or Ctrl/Cmd + Y - Redo
            if ((e.shiftKey && key === 'z') || key === 'y') {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                console.log('↷ Redo shortcut triggered');
                triggerAction('redo');
                return false;
            }
            
            // Handle text formatting shortcuts (only in textarea)
            const target = e.target;
            const isEditor = target && target.tagName === 'TEXTAREA';
            
            console.log('Formatting check - key:', key, 'isEditor:', isEditor, 'target:', target?.tagName);
            
            if (isEditor) {
                // Ctrl/Cmd + B - Bold
                if (key === 'b') {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    console.log('** Bold shortcut triggered');
                    formatText(target, '**', '**');
                    return false;
                }
                
                // Ctrl/Cmd + I - Italic
                if (key === 'i') {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    console.log('* Italic shortcut triggered');
                    formatText(target, '*', '*');
                    return false;
                }
                
                // Ctrl/Cmd + K - Insert Link
                if (key === 'k') {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    console.log('🔗 Link shortcut triggered');
                    insertLink(target);
                    return false;
                }
            }
        }
        
        // Trigger action by clicking the corresponding button
        function triggerAction(action) {
            console.log('Triggering action:', action);
            showShortcutFeedback(action);
            
            // Find and click the button in main document
            setTimeout(() => {
                let button = null;
                
                // Get all buttons
                const buttons = mainDoc.querySelectorAll('button');
                console.log('Found', buttons.length, 'buttons');
                
                // Search for the right button
                for (let btn of buttons) {
                    const text = (btn.textContent || '').trim();
                    const testId = btn.getAttribute('data-testid') || '';
                    const key = btn.getAttribute('data-baseweb') || '';
                    
                    console.log('Checking button:', text.substring(0, 20), 'testId:', testId.substring(0, 30));
                    
                    if (action === 'save') {
                        if (testId.includes('kb_save') || 
                            text.includes('Quick Save') || 
                            text.includes('Save') || 
                            text.includes('💾')) {
                            button = btn;
                            console.log('✅ Save button found!');
                            break;
                        }
                    } else if (action === 'undo') {
                        if (testId.includes('kb_undo') || 
                            text.includes('Undo') || 
                            text.includes('↶')) {
                            button = btn;
                            console.log('✅ Undo button found!');
                            break;
                        }
                    } else if (action === 'redo') {
                        if (testId.includes('kb_redo') || 
                            text.includes('Redo') || 
                            text.includes('↷')) {
                            button = btn;
                            console.log('✅ Redo button found!');
                            break;
                        }
                    }
                }
                
                if (button) {
                    console.log('Clicking button:', button.textContent);
                    // Try multiple click methods
                    button.focus();
                    button.click();
                    // Also try dispatching events
                    const clickEvent = new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        view: mainWindow
                    });
                    button.dispatchEvent(clickEvent);
                } else {
                    console.warn('❌ Button not found for action:', action);
                    console.log('Available buttons:', Array.from(buttons).map(b => ({
                        text: b.textContent.trim().substring(0, 30),
                        testId: b.getAttribute('data-testid') || 'none'
                    })));
                }
            }, 100);
        }
        
        // Format text in textarea
        function formatText(textarea, prefix, suffix) {
            if (!textarea) {
                console.warn('Textarea not found for formatting');
                return;
            }
            
            console.log('Formatting text in textarea');
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const text = textarea.value;
            const selectedText = text.substring(start, end);
            
            const replacement = selectedText 
                ? prefix + selectedText + suffix
                : prefix + suffix;
            
            const newText = text.substring(0, start) + replacement + text.substring(end);
            textarea.value = newText;
            
            // Trigger events for Streamlit - try multiple methods
            const inputEvent = new Event('input', { bubbles: true, cancelable: true });
            textarea.dispatchEvent(inputEvent);
            
            const changeEvent = new Event('change', { bubbles: true, cancelable: true });
            textarea.dispatchEvent(changeEvent);
            
            // Also try InputEvent
            try {
                const inputEvent2 = new InputEvent('input', {
                    bubbles: true,
                    cancelable: true,
                    inputType: 'insertText',
                    data: replacement
                });
                textarea.dispatchEvent(inputEvent2);
            } catch (e) {
                console.log('InputEvent not supported');
            }
            
            // Restore cursor
            if (selectedText) {
                textarea.setSelectionRange(start + prefix.length, start + prefix.length + selectedText.length);
            } else {
                textarea.setSelectionRange(start + prefix.length, start + prefix.length);
            }
            textarea.focus();
            
            console.log('Text formatted successfully');
        }
        
        // Insert link markdown
        function insertLink(textarea) {
            if (!textarea) return;
            
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const text = textarea.value;
            const selectedText = text.substring(start, end);
            
            const linkText = selectedText || 'link text';
            const replacement = `[${linkText}](https://)`;
            
            const newText = text.substring(0, start) + replacement + text.substring(end);
            textarea.value = newText;
            
            // Trigger events
            const inputEvent = new Event('input', { bubbles: true, cancelable: true });
            textarea.dispatchEvent(inputEvent);
            const changeEvent = new Event('change', { bubbles: true, cancelable: true });
            textarea.dispatchEvent(changeEvent);
            
            // Position cursor in URL
            const urlStart = start + linkText.length + 3;
            const urlEnd = urlStart + 8;
            textarea.setSelectionRange(urlStart, urlEnd);
            textarea.focus();
        }
        
        // Show visual feedback
        function showShortcutFeedback(action) {
            const actionNames = {
                'save': '💾 Saving...',
                'undo': '↶ Undo',
                'redo': '↷ Redo'
            };
            
            let feedback = mainDoc.getElementById('mp-shortcut-feedback');
            if (!feedback) {
                feedback = mainDoc.createElement('div');
                feedback.id = 'mp-shortcut-feedback';
                feedback.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: rgba(0, 0, 0, 0.85);
                    color: white;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                    z-index: 999999;
                    pointer-events: none;
                    opacity: 0;
                    transition: opacity 0.2s ease;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                `;
                mainDoc.body.appendChild(feedback);
            }
            
            feedback.textContent = actionNames[action] || action;
            feedback.style.opacity = '1';
            
            setTimeout(() => {
                feedback.style.opacity = '0';
            }, 1500);
        }
        
        // Add event listeners to main document
        const options = { capture: true, passive: false };
        
        // Try to add listeners - if we can't access parent, use current window
        try {
            mainDoc.addEventListener('keydown', handleKeyboardShortcut, options);
            mainWindow.addEventListener('keydown', handleKeyboardShortcut, options);
            console.log('✅ Keyboard shortcuts initialized in main window (' + modKeyName + ' key)');
        } catch (e) {
            // Fallback to current window if parent access fails
            console.warn('Could not access parent window, using current window:', e);
            document.addEventListener('keydown', handleKeyboardShortcut, options);
            window.addEventListener('keydown', handleKeyboardShortcut, options);
            console.log('✅ Keyboard shortcuts initialized in current window (' + modKeyName + ' key)');
        }
        
        console.log('📝 Try pressing ' + modKeyName + '+S, ' + modKeyName + '+Z, ' + modKeyName + '+B to test...');
    })();
    </script>
    """
    
    components.html(keyboard_html, height=0)

    return None

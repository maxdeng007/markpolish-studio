"""
Migration Tool for MarkPolish Studio
Converts old syntax to new syntax (e.g., ## Title to ::: card)
"""

import re
import streamlit as st
import time
from typing import Tuple

def migrate_card_syntax(content: str) -> Tuple[str, int]:
    """
    Migrate old card syntax (## Title) to new syntax (::: card)
    
    Args:
        content: Markdown content to migrate
        
    Returns:
        Tuple of (migrated_content, number_of_changes)
    """
    changes = 0
    lines = content.split('\n')
    result_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a ## heading that should be converted to card
        if re.match(r'^##\s+(.+)$', line):
            # Check if next non-empty line exists (card needs content)
            next_content_line = None
            for j in range(i + 1, len(lines)):
                if lines[j].strip():
                    next_content_line = j
                    break
            
            if next_content_line:
                # This looks like a card - find where it ends
                # Card ends at next ## heading, next ::: component, or double newline
                card_start = i
                card_end = next_content_line
                
                # Find the end of the card content
                for j in range(next_content_line + 1, len(lines)):
                    # Stop at next heading, component, or double newline
                    if (re.match(r'^##', lines[j]) or 
                        re.match(r'^:::', lines[j]) or
                        (j > next_content_line + 1 and not lines[j-1].strip() and not lines[j].strip())):
                        card_end = j - 1
                        break
                    card_end = j
                
                # Extract card content
                card_title = re.match(r'^##\s+(.+)$', line).group(1)
                card_content_lines = lines[card_start + 1:card_end + 1]
                
                # Remove empty lines at start/end
                while card_content_lines and not card_content_lines[0].strip():
                    card_content_lines.pop(0)
                while card_content_lines and not card_content_lines[-1].strip():
                    card_content_lines.pop()
                
                if card_content_lines:
                    # Convert to new syntax
                    result_lines.append("::: card")
                    result_lines.append(f"## {card_title}")
                    result_lines.extend(card_content_lines)
                    result_lines.append(":::")
                    result_lines.append("")  # Add spacing
                    
                    i = card_end + 1
                    changes += 1
                    continue
        
        result_lines.append(line)
        i += 1
    
    return '\n'.join(result_lines), changes

def migrate_content(content: str, show_preview: bool = True) -> Tuple[str, int]:
    """
    Migrate content from old syntax to new syntax
    
    Args:
        content: Content to migrate
        show_preview: Whether to show preview of changes
        
    Returns:
        Tuple of (migrated_content, total_changes)
    """
    total_changes = 0
    
    # Migrate card syntax
    migrated, card_changes = migrate_card_syntax(content)
    total_changes += card_changes
    
    if show_preview and total_changes > 0:
        st.info(f"🔧 Found {total_changes} card(s) to migrate")
    
    return migrated, total_changes

def show_migration_ui():
    """Show migration tool UI in Streamlit"""
    st.subheader("🔧 Syntax Migration Tool")
    st.caption("Convert old syntax to new syntax (## Title → ::: card)")
    
    current_content = st.session_state.get("content", "")
    
    if not current_content:
        st.warning("No content to migrate. Load a file first.")
        return
    
    # Show preview
    migrated_content, changes = migrate_content(current_content, show_preview=True)
    
    if changes > 0:
        st.success(f"✅ Ready to migrate {changes} card(s)")
        
        # Show diff preview
        with st.expander("👁️ Preview Changes", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Before (Old Syntax)**")
                st.code(current_content[:1000] + ("..." if len(current_content) > 1000 else ""), language="markdown")
            with col2:
                st.markdown("**After (New Syntax)**")
                st.code(migrated_content[:1000] + ("..." if len(migrated_content) > 1000 else ""), language="markdown")
        
        # Apply migration
        if st.button("✅ Apply Migration", use_container_width=True, type="primary"):
            st.session_state.content = migrated_content
            st.session_state.reset_editor = True
            st.success(f"✅ Migrated {changes} card(s)!")
            time.sleep(1)
            st.rerun()
    else:
        st.info("✨ No migration needed - your content is already using the latest syntax!")


import os
import re
import aqt
from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.qt import QDockWidget, QVBoxLayout, Qt, QUrl, QWidget, QHBoxLayout, QPushButton, QLabel, QCursor, QPainter
from aqt.utils import showInfo, tooltip

# Global reference to prevent garbage collection
dock_widget = None
current_card_text = ""  # Store the current card text for Tab key access
current_card_question = ""  # Store just the question
current_card_answer = ""  # Store just the answer
is_showing_answer = False  # Track if we're showing the answer side

class CustomTitleBar(QWidget):
    """Custom title bar with pointer cursor on buttons"""
    def __init__(self, dock_widget, parent=None):
        super().__init__(parent)
        self.dock_widget = dock_widget
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 4, 4)
        layout.setSpacing(2)
        
        # Title label
        self.title_label = QLabel("OpenEvidence")
        self.title_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); font-size: 13px; font-weight: 500;")
        layout.addWidget(self.title_label)
        
        # Add stretch to push buttons to the right
        layout.addStretch()
        
        # Float/Undock button with high-quality SVG icon
        self.float_button = QPushButton()
        self.float_button.setFixedSize(24, 24)
        self.float_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Create high-resolution SVG icon for float button
        float_icon_svg = """<?xml version="1.0" encoding="UTF-8"?>
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="6" y="6" width="36" height="36" stroke="white" stroke-width="3" fill="none" rx="3"/>
            <path d="M18 6 L18 18 L6 18" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M30 42 L30 30 L42 30" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        """
        
        # Convert SVG to QIcon
        try:
            from PyQt6.QtGui import QIcon, QPixmap
            from PyQt6.QtCore import QByteArray, QSize
            from PyQt6.QtSvg import QSvgRenderer
        except ImportError:
            from PyQt5.QtGui import QIcon, QPixmap
            from PyQt5.QtCore import QByteArray, QSize
            from PyQt5.QtSvg import QSvgRenderer
        
        # Render SVG at higher resolution for crisp display
        svg_bytes = QByteArray(float_icon_svg.encode())
        renderer = QSvgRenderer(svg_bytes)
        pixmap = QPixmap(48, 48)
        try:
            pixmap.fill(Qt.GlobalColor.transparent)
        except:
            pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        self.float_button.setIcon(QIcon(pixmap))
        self.float_button.setIconSize(QSize(14, 14))
        
        self.float_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.12);
            }
        """)
        self.float_button.clicked.connect(self.toggle_floating)
        layout.addWidget(self.float_button)
        
        # Close button with high-quality SVG icon
        self.close_button = QPushButton()
        self.close_button.setFixedSize(24, 24)
        self.close_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Create high-resolution SVG icon for close button
        close_icon_svg = """<?xml version="1.0" encoding="UTF-8"?>
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 8 L40 40 M40 8 L8 40" stroke="white" stroke-width="4" stroke-linecap="round"/>
        </svg>
        """
        
        # Render SVG at higher resolution for crisp display
        svg_bytes_close = QByteArray(close_icon_svg.encode())
        renderer_close = QSvgRenderer(svg_bytes_close)
        pixmap_close = QPixmap(48, 48)
        try:
            pixmap_close.fill(Qt.GlobalColor.transparent)
        except:
            pixmap_close.fill(Qt.transparent)
        painter_close = QPainter(pixmap_close)
        renderer_close.render(painter_close)
        painter_close.end()
        
        self.close_button.setIcon(QIcon(pixmap_close))
        self.close_button.setIconSize(QSize(14, 14))
        
        self.close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.2);
            }
        """)
        self.close_button.clicked.connect(self.dock_widget.hide)
        layout.addWidget(self.close_button)
        
        # Set background color for title bar - modern dark gray
        self.setStyleSheet("background: #2a2a2a; border-bottom: 1px solid rgba(255, 255, 255, 0.06);")
    
    def toggle_floating(self):
        self.dock_widget.setFloating(not self.dock_widget.isFloating())

class OpenEvidencePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        try:
            from PyQt6.QtWebEngineWidgets import QWebEngineView
            from PyQt6.QtCore import QEvent
            from PyQt6.QtWebEngineCore import QWebEngineSettings
        except ImportError:
            try:
                from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
                from PyQt5.QtCore import QEvent
            except ImportError:
                # Fallback for some Anki versions where it's exposed differently or not available
                from aqt.qt import QWebEngineView, QEvent
                try:
                    from aqt.qt import QWebEngineSettings
                except:
                    QWebEngineSettings = None

        self.web = QWebEngineView(self)
        
        # Prevent the webview from stealing focus on navigation
        if QWebEngineSettings:
            try:
                self.web.settings().setAttribute(QWebEngineSettings.WebAttribute.FocusOnNavigationEnabled, False)
            except:
                pass
        
        layout.addWidget(self.web)
        
        # Inject Ctrl+Shift (Cmd+Shift on Mac) listener after page loads
        self.web.loadFinished.connect(self.inject_shift_key_listener)
        
        self.web.load(QUrl("https://www.openevidence.com/"))
    
    def inject_shift_key_listener(self):
        """Inject JavaScript to listen for Ctrl+Shift (Cmd+Shift on Mac) when search input is actively focused"""
        shift_listener_js = """
        (function() {
            console.log('Anki: Ctrl+Shift (Cmd+Shift on Mac) listener injected for OpenEvidence');
            
            // Listen for keyboard shortcut on the entire document
            document.addEventListener('keydown', function(event) {
                // Only handle Ctrl+Shift (or Cmd+Shift on Mac)
                // Check if Shift is pressed along with Ctrl or Cmd (but no other keys)
                var isCorrectShortcut = event.shiftKey && 
                                       (event.ctrlKey || event.metaKey) &&
                                       !event.altKey &&
                                       (event.key === 'Shift' || event.key === 'Control' || event.key === 'Meta');
                
                if (isCorrectShortcut) {
                    // Check if the ACTIVE ELEMENT is specifically the OpenEvidence search input
                    var activeElement = document.activeElement;
                    
                    // Make sure we're in an input/textarea element
                    var isInputElement = activeElement && (
                        activeElement.tagName === 'INPUT' || 
                        activeElement.tagName === 'TEXTAREA'
                    );
                    
                    // ADDITIONAL CHECK: Make sure it's specifically the OpenEvidence search box
                    var isOpenEvidenceSearchBox = false;
                    if (isInputElement) {
                        // Check if this is the main search input by looking at placeholder or attributes
                        var placeholder = activeElement.placeholder || '';
                        var type = activeElement.type || '';
                        
                        // OpenEvidence search box has "Ask a medical question" placeholder
                        isOpenEvidenceSearchBox = (
                            placeholder.toLowerCase().includes('medical') ||
                            placeholder.toLowerCase().includes('question') ||
                            type === 'text' ||
                            activeElement.tagName === 'TEXTAREA'
                        );
                    }
                    
                    // Only proceed if BOTH conditions are true:
                    // 1. It's an input/textarea element
                    // 2. It's the OpenEvidence search box
                    if (isInputElement && isOpenEvidenceSearchBox) {
                        console.log('Anki: Ctrl+Shift (or Cmd+Shift) pressed in OpenEvidence search box');
                        event.preventDefault();
                        
                        // Request the card text from Python via a custom property
                        if (window.ankiCardText) {
                            var text = window.ankiCardText;
                            
                            // Clear existing value first
                            activeElement.value = '';
                            
                            // Use proper setter that React/Vue can detect
                            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                                window.HTMLInputElement.prototype, 
                                'value'
                            ).set;
                            var nativeTextAreaValueSetter = Object.getOwnPropertyDescriptor(
                                window.HTMLTextAreaElement.prototype, 
                                'value'
                            ).set;
                            
                            if (activeElement.tagName === 'INPUT') {
                                nativeInputValueSetter.call(activeElement, text);
                            } else if (activeElement.tagName === 'TEXTAREA') {
                                nativeTextAreaValueSetter.call(activeElement, text);
                            }
                            
                            // Dispatch proper input event that React recognizes
                            var inputEvent = new InputEvent('input', {
                                bubbles: true,
                                cancelable: true,
                                inputType: 'insertText',
                                data: text
                            });
                            activeElement.dispatchEvent(inputEvent);
                            
                            // Also dispatch change event
                            var changeEvent = new Event('change', { bubbles: true });
                            activeElement.dispatchEvent(changeEvent);
                            
                            // Dispatch keyup event to trigger any validation
                            var keyupEvent = new KeyboardEvent('keyup', { 
                                bubbles: true,
                                cancelable: true,
                                key: ' ',
                                code: 'Space'
                            });
                            activeElement.dispatchEvent(keyupEvent);
                            
                            console.log('Anki: Filled search box with card text using React-compatible events');
                        } else {
                            console.log('Anki: No card text available');
                        }
                    } else {
                        console.log('Anki: Ctrl+Shift (or Cmd+Shift) pressed but not in OpenEvidence search box, allowing default behavior');
                    }
                }
            }, true);
        })();
        """
        self.web.page().runJavaScript(shift_listener_js)
        
        # Also inject the current card text
        self.update_card_text_in_js()
    
    def update_card_text_in_js(self):
        """Update the card text in the JavaScript context"""
        global current_card_text
        if current_card_text:
            escaped_text = current_card_text.replace('\\', '\\\\').replace('`', '\\`').replace("'", "\\'").replace('\n', '\\n').replace('\r', '')
            js_code = f"window.ankiCardText = '{escaped_text}';"
            self.web.page().runJavaScript(js_code)

def create_dock_widget():
    """Create the dock widget for OpenEvidence panel"""
    global dock_widget
    
    if dock_widget is None:
        # Create the dock widget
        dock_widget = QDockWidget("OpenEvidence", mw)
        dock_widget.setObjectName("OpenEvidenceDock")
        
        # Create the panel widget
        panel = OpenEvidencePanel()
        dock_widget.setWidget(panel)
        
        # Create and set custom title bar with pointer cursors
        custom_title = CustomTitleBar(dock_widget)
        dock_widget.setTitleBarWidget(custom_title)
        
        # Get config for width
        config = mw.addonManager.getConfig(__name__) or {}
        panel_width = config.get("width", 500)
        
        # Set initial size
        dock_widget.setMinimumWidth(300)
        dock_widget.resize(panel_width, mw.height())
        
        # Add the dock widget to the right side of the main window
        mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock_widget)
        
        # Hide by default
        dock_widget.hide()
        
        # Store reference to prevent garbage collection
        mw.openevidence_dock = dock_widget
    
    return dock_widget

def toggle_panel():
    """Toggle the OpenEvidence dock widget visibility"""
    global dock_widget
    
    if dock_widget is None:
        create_dock_widget()
    
    if dock_widget.isVisible():
        dock_widget.hide()
    else:
        # If the dock is floating, dock it back to the right side
        if dock_widget.isFloating():
            dock_widget.setFloating(False)
            mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock_widget)
        
        dock_widget.show()
        dock_widget.raise_()

def on_webview_did_receive_js_message(handled, message, context):
    if message == "openevidence":
        toggle_panel()
        return (True, None)
    return handled

def clean_html_text(html_text):
    """Clean HTML text by removing tags and normalizing"""
    # Remove style tags and their contents first
    text = re.sub(r'<style[^>]*>.*?</style>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove script tags and their contents
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Strip remaining HTML tags
    text = re.sub('<[^<]+?>', '', text)
    
    # Decode HTML entities
    try:
        import html
        text = html.unescape(text)
    except:
        pass
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def store_current_card_text(card):
    """Store the current card text globally for Ctrl+Shift (Cmd+Shift on Mac) access from OpenEvidence panel"""
    global current_card_text, current_card_question, current_card_answer, is_showing_answer, dock_widget
    
    try:
        # Always get both question and answer
        question_html = card.question()
        answer_html = card.answer()
        
        # Clean both
        current_card_question = clean_html_text(question_html)
        current_card_answer = clean_html_text(answer_html)
        
        # Check which side is showing
        if mw.reviewer and mw.reviewer.state == "answer":
            is_showing_answer = True
            # Format with both question and answer
            current_card_text = f"""Can you explain this to me:
Question:
{current_card_question}

Answer:
{current_card_answer}"""
        else:
            is_showing_answer = False
            # Format with just question
            current_card_text = f"""Can you explain this to me:
Question:
{current_card_question}"""
        
        # Update the JavaScript context with new card text
        if dock_widget and dock_widget.widget():
            panel = dock_widget.widget()
            if hasattr(panel, 'update_card_text_in_js'):
                panel.update_card_text_in_js()
        
    except:
        current_card_text = ""
        current_card_question = ""
        current_card_answer = ""
        is_showing_answer = False

def add_toolbar_button(links, toolbar):
    """Add OpenEvidence button to the top toolbar"""
    # Create open book SVG icon (matching Anki's icon size and style)
    open_book_icon = """
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -0.2em;">
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
</svg>
"""

    # Add the button to the toolbar using Anki's standard hitem class
    links.append(
        f'<a class="hitem" href="#" onclick="pycmd(\'openevidence\'); return false;" title="OpenEvidence">{open_book_icon}</a>'
    )

# Hook registration
gui_hooks.webview_did_receive_js_message.append(on_webview_did_receive_js_message)

# Add toolbar button
gui_hooks.top_toolbar_did_init_links.append(add_toolbar_button)

# Initialize dock widget when main window is ready
gui_hooks.main_window_did_init.append(create_dock_widget)

# Update stored card text when question/answer is shown (for Ctrl+Shift in OpenEvidence search box)
gui_hooks.reviewer_did_show_question.append(store_current_card_text)
gui_hooks.reviewer_did_show_answer.append(store_current_card_text)

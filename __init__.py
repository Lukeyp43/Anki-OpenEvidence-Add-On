import os
import aqt
from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.qt import QDockWidget, QVBoxLayout, Qt, QUrl, QWidget, QHBoxLayout, QPushButton, QLabel, QCursor
from aqt.utils import showInfo, tooltip

# Global reference to prevent garbage collection
dock_widget = None

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
        
        # Float/Undock button with SVG icon
        self.float_button = QPushButton()
        self.float_button.setFixedSize(24, 24)
        self.float_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Create smaller SVG icon for float button
        float_icon_svg = """
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="1.5" y="1.5" width="9" height="9" stroke="white" stroke-width="1" fill="none" rx="1"/>
            <path d="M4.5 1.5 L4.5 4.5 L1.5 4.5" stroke="white" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7.5 10.5 L7.5 7.5 L10.5 7.5" stroke="white" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        """
        
        # Convert SVG to QIcon
        try:
            from PyQt6.QtGui import QIcon, QPixmap
            from PyQt6.QtCore import QByteArray, QSize
        except ImportError:
            from PyQt5.QtGui import QIcon, QPixmap
            from PyQt5.QtCore import QByteArray, QSize
        
        svg_bytes = QByteArray(float_icon_svg.encode())
        pixmap = QPixmap()
        pixmap.loadFromData(svg_bytes)
        self.float_button.setIcon(QIcon(pixmap))
        self.float_button.setIconSize(QSize(12, 12))
        
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
        
        # Close button with SVG icon
        self.close_button = QPushButton()
        self.close_button.setFixedSize(24, 24)
        self.close_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Create smaller SVG icon for close button
        close_icon_svg = """
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2 2 L10 10 M10 2 L2 10" stroke="white" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
        """
        
        svg_bytes_close = QByteArray(close_icon_svg.encode())
        pixmap_close = QPixmap()
        pixmap_close.loadFromData(svg_bytes_close)
        self.close_button.setIcon(QIcon(pixmap_close))
        self.close_button.setIconSize(QSize(12, 12))
        
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
        except ImportError:
            try:
                from PyQt5.QtWebEngineWidgets import QWebEngineView
            except ImportError:
                # Fallback for some Anki versions where it's exposed differently or not available
                # But modern Anki should have it.
                from aqt.qt import QWebEngineView

        self.web = QWebEngineView(self)
        layout.addWidget(self.web)
        
        self.web.load(QUrl("https://www.openevidence.com/"))

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

# Removed the bottom bar button - icon now appears in top toolbar only

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

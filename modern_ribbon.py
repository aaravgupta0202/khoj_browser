# modern_ribbon.py
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class ModernRibbon(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browser = parent
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # 🔙 Navigation Buttons Group
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(4)
        
        self.back_btn = self.make_nav_btn("←", "Back", self.browser.go_back)
        self.forward_btn = self.make_nav_btn("→", "Forward", self.browser.go_forward)
        self.reload_btn = self.make_nav_btn("↻", "Reload", self.browser.reload_page)
        self.home_btn = self.make_nav_btn("🏠", "Home", self.browser.go_home)
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.reload_btn)
        nav_layout.addWidget(self.home_btn)
        
        layout.addWidget(nav_widget)

        # 🌐 Address Bar with search icon
        address_container = QWidget()
        address_layout = QHBoxLayout(address_container)
        address_layout.setContentsMargins(0, 0, 0, 0)
        address_layout.setSpacing(0)
        
        search_icon = QLabel("🔍")
        search_icon.setFixedSize(30, 30)
        search_icon.setAlignment(Qt.AlignCenter)
        search_icon.setObjectName("searchIcon")
        
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Search Google or enter address...")
        self.address_bar.returnPressed.connect(self.browser.load_url)
        self.address_bar.setMinimumHeight(32)
        
        address_layout.addWidget(search_icon)
        address_layout.addWidget(self.address_bar)
        layout.addWidget(address_container, 1)

        # 🛠️ Action Buttons Group
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(6)
        
        self.zoom_out_btn = self.make_action_btn("−", "Zoom Out", self.browser.zoom_out)
        self.zoom_in_btn = self.make_action_btn("+", "Zoom In", self.browser.zoom_in)
        self.menu_btn = self.make_action_btn("☰", "Menu", self.show_menu)
        
        action_layout.addWidget(self.zoom_out_btn)
        action_layout.addWidget(self.zoom_in_btn)
        action_layout.addWidget(self.menu_btn)
        
        layout.addWidget(action_widget)

        self.setLayout(layout)

    def make_nav_btn(self, text, tooltip, func):
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setFixedSize(36, 32)
        btn.clicked.connect(func)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setObjectName("navButton")
        return btn

    def make_action_btn(self, text, tooltip, func):
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setFixedSize(36, 32)
        btn.clicked.connect(func)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setObjectName("actionButton")
        return btn

    def show_menu(self):
        menu = QMenu(self.browser)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 16px;
                border-radius: 4px;
                margin: 2px;
            }
            QMenu::item:selected {
                background-color: #ff6f3c;
            }
        """)
        
        # File menu
        file_menu = menu.addMenu("📁 File")
        file_menu.addAction("🪟 New Window", self.browser.new_window)
        file_menu.addAction("🔒 New Incognito Window", self.browser.new_incognito_window)
        file_menu.addSeparator()
        file_menu.addAction("❌ Exit", self.browser.close)
        
        # History menu
        history_menu = menu.addMenu("📚 History")
        history_menu.addAction("📖 Show History", self.browser.show_history)
        
        # Bookmarks menu
        bookmarks_menu = menu.addMenu("⭐ Bookmarks")
        bookmarks_menu.addAction("📒 Bookmarks Manager", self.browser.show_bookmarks)
        
        # Profiles menu
        profiles_menu = menu.addMenu("👤 Profiles")
        profiles_menu.addAction("👥 Manage Profiles", self.browser.show_profiles)
        
        # Settings
        menu.addSeparator()
        menu.addAction("⚙️ Settings", self.browser.show_settings)
        
        menu.exec_(self.menu_btn.mapToGlobal(QPoint(0, self.menu_btn.height())))

    def apply_styles(self):
        # Force set the background color directly
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#ff0000"))
        self.setPalette(palette)
        
        self.setStyleSheet("""
            /* Modern Ribbon - RED BACKGROUND */
            ModernRibbon {
                background: #ff0000;
                border-bottom: 2px solid #0000ff;
            }
            
            /* Search Icon - BLUE */
            #searchIcon {
                background: #0000ff;
                border: 2px solid #0000ff;
                border-right: none;
                border-radius: 8px 0 0 8px;
                color: black;
                font-size: 12px;
                font-weight: bold;
            }
            
            /* Navigation Buttons - BLUE */
            #navButton {
                background: #0000ff;
                border: 2px solid #0000ff;
                border-radius: 8px;
                color: black;
                font-weight: bold;
                font-size: 13px;
            }
            
            #navButton:hover {
                background: #3333ff;
                border-color: #3333ff;
            }
            
            #navButton:pressed {
                background: #0000cc;
                border-color: #0000cc;
            }
            
            #navButton:disabled {
                background: #6666ff;
                color: #444444;
                border-color: #6666ff;
            }
            
            /* Action Buttons - BLUE */
            #actionButton {
                background: #0000ff;
                border: 2px solid #0000ff;
                border-radius: 8px;
                color: black;
                font-weight: bold;
                font-size: 13px;
            }
            
            #actionButton:hover {
                background: #3333ff;
                border-color: #3333ff;
            }
            
            /* Address Bar - BLUE */
            QLineEdit {
                background: #0000ff;
                border: 2px solid #0000ff;
                border-left: none;
                border-radius: 0 8px 8px 0;
                padding: 8px 12px;
                color: black;
                font-size: 14px;
                font-weight: bold;
                selection-background-color: #ff0000;
                selection-color: black;
            }
            
            QLineEdit:focus {
                border-color: #0000ff;
                border-left: none;
                background: #3333ff;
            }
            
            QLineEdit::placeholder {
                color: #333333;
                font-weight: normal;
            }
        """)
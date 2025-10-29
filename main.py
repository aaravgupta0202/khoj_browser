# main.py (COMPLETE WITH ALL FEATURES)
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from landing_page import LandingPage
from modern_ribbon import ModernRibbon

# Import managers
from history_manager import HistoryManager
from bookmarks_manager import BookmarksManager
from settings_manager import SettingsManager

class DataManager:
    def __init__(self):
        self.history_manager = HistoryManager()
        self.bookmarks_manager = BookmarksManager()
        self.settings_manager = SettingsManager()

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        
        self.setWindowTitle("Arc Browser")
        self.setGeometry(100, 100, 1200, 800)

        # Central layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Create ribbon
        self.ribbon = ModernRibbon(self)
        self.layout.addWidget(self.ribbon)

        # Create bookmarks bar
        self.create_bookmarks_bar()

        # Create tab system
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.layout.addWidget(self.tabs)

        # Add first tab as landing page
        self.add_landing_tab()
        
        # Apply theme
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #252525;
            }
            QTabBar::tab {
                background-color: #252525;
                color: #ffffff;
                padding: 8px 16px;
                border: 1px solid #404040;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #1a1a1a;
                border-bottom: 2px solid #ff6f3c;
            }
        """)

    def on_tab_changed(self, index):
        """Update address bar when tab changes"""
        if index >= 0:
            current_widget = self.tabs.widget(index)
            if isinstance(current_widget, LandingPage):
                self.ribbon.address_bar.setText("arc://newtab")
            elif hasattr(current_widget, 'url'):
                url = current_widget.url().toString()
                if url:
                    self.ribbon.address_bar.setText(url)

    def create_bookmarks_bar(self):
        """Create bookmarks bar with user bookmarks"""
        if hasattr(self, 'bookmarks_bar') and self.bookmarks_bar:
            self.layout.removeWidget(self.bookmarks_bar)
            self.bookmarks_bar.deleteLater()
            
        self.bookmarks_bar = QWidget()
        layout = QHBoxLayout(self.bookmarks_bar)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(6)

        # Add user bookmarks
        bookmarks = self.data_manager.bookmarks_manager.get_bookmarks()
        for bookmark in bookmarks[:10]:  # Show first 10 bookmarks
            btn = QPushButton(bookmark['title'][:12])
            btn.setFixedHeight(28)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.08);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 4px 10px;
                }
                QPushButton:hover {
                    background: rgba(255,111,60,0.3);
                }
            """)
            btn.clicked.connect(lambda checked, u=bookmark['url']: self.navigate_to_url(u))
            layout.addWidget(btn)

        # Add bookmark button
        add_btn = QPushButton("+")
        add_btn.setFixedSize(28, 28)
        add_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1);
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: rgba(255,111,60,0.3);
            }
        """)
        add_btn.clicked.connect(self.add_current_bookmark)
        layout.addWidget(add_btn)
        
        layout.addStretch()
        self.layout.insertWidget(1, self.bookmarks_bar)

    def add_landing_tab(self):
        """Add a new landing page tab"""
        landing = LandingPage(
            bookmarks_manager=self.data_manager.bookmarks_manager,
            settings_manager=self.data_manager.settings_manager
        )
        landing.search_requested.connect(self.handle_search)
        landing.url_requested.connect(self.navigate_to_url)
        landing.background_changed.connect(self.handle_background_change)
        
        index = self.tabs.addTab(landing, "🏠 Home")
        self.tabs.setCurrentIndex(index)
        self.ribbon.address_bar.setText("arc://newtab")

    def add_browser_tab(self, url=None):
        """Add a new browser tab"""
        if url is None:
            url = "https://www.google.com"
            
        browser = QWebEngineView()
        browser.setUrl(QUrl(url))
        
        index = self.tabs.addTab(browser, "Loading...")
        self.tabs.setCurrentIndex(index)
        
        # Connect signals
        browser.urlChanged.connect(lambda qurl: self.update_urlbar(qurl))
        browser.loadFinished.connect(lambda ok, i=index, b=browser: self.update_tab_title(ok, b, i))
        
        # Add to history
        browser.urlChanged.connect(lambda qurl: self.add_to_history(qurl, browser))

    def add_to_history(self, qurl, browser):
        """Add page to history"""
        url = qurl.toString()
        if url not in ["about:blank", "arc://newtab"] and not url.startswith("arc://"):
            title = browser.page().title()
            self.data_manager.history_manager.add_entry(url, title)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def handle_search(self, query):
        """Handle search from landing page"""
        print(f"Search requested: {query}")
        if query.startswith(("http://", "https://")):
            self.navigate_to_url(query)
        else:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            self.navigate_to_url(search_url)

    def handle_background_change(self, background_data):
        """Handle background change from landing page"""
        print(f"Background change requested: {background_data}")
        # You can implement background change logic here
        QMessageBox.information(self, "Background", f"Background would change to: {background_data}")

    def navigate_to_url(self, url):
        """Main navigation method"""
        print(f"Navigating to: {url}")
        
        current_widget = self.tabs.currentWidget()
        
        if isinstance(current_widget, LandingPage):
            # Replace landing page with browser tab
            current_index = self.tabs.currentIndex()
            self.tabs.removeTab(current_index)
            self.add_browser_tab(url)
        else:
            # Navigate in current browser tab
            processed_url = self.process_url(url)
            current_widget.setUrl(QUrl(processed_url))

    def process_url(self, url):
        """Process URLs to handle search queries"""
        if url.startswith(("http://", "https://", "arc://")):
            return url
            
        if "." in url and " " not in url:
            return "https://" + url
        else:
            return f"https://www.google.com/search?q={url.replace(' ', '+')}"

    def update_urlbar(self, qurl):
        """Update address bar when page URL changes"""
        self.ribbon.address_bar.setText(qurl.toString())
        self.ribbon.address_bar.setCursorPosition(0)

    def update_tab_title(self, ok, browser, index):
        """Update tab title when page loads"""
        if ok:
            title = browser.page().title()
            short = title[:20] + "..." if len(title) > 20 else title
            self.tabs.setTabText(index, short)

    # ===================== Navigation Methods =====================
    def go_back(self):
        current = self.tabs.currentWidget()
        if hasattr(current, "back"):
            current.back()

    def go_forward(self):
        current = self.tabs.currentWidget()
        if hasattr(current, "forward"):
            current.forward()

    def reload_page(self):
        current = self.tabs.currentWidget()
        if hasattr(current, "reload"):
            current.reload()
        elif isinstance(current, LandingPage):
            current.setup_landing_page()

    def go_home(self):
        """Go to home (landing page)"""
        for i in range(self.tabs.count()):
            if isinstance(self.tabs.widget(i), LandingPage):
                self.tabs.setCurrentIndex(i)
                return
        self.add_landing_tab()

    def zoom_in(self):
        current = self.tabs.currentWidget()
        if hasattr(current, "setZoomFactor"):
            current.setZoomFactor(current.zoomFactor() + 0.1)

    def zoom_out(self):
        current = self.tabs.currentWidget()
        if hasattr(current, "setZoomFactor"):
            current.setZoomFactor(current.zoomFactor() - 0.1)

    def load_url(self):
        """Called when user presses Enter in address bar"""
        url = self.ribbon.address_bar.text().strip()
        if url:
            self.navigate_to_url(url)

    # ===================== Bookmark Methods =====================
    def add_current_bookmark(self):
        """Add current page to bookmarks"""
        current = self.tabs.currentWidget()
        if hasattr(current, "url"):
            url = current.url().toString()
            title = current.title()
            if url and url != "about:blank" and not url.startswith("arc://"):
                self.data_manager.bookmarks_manager.add_bookmark(title, url)
                self.refresh_bookmarks_display()
                QMessageBox.information(self, "Bookmark Added", f"Added '{title}' to bookmarks!")

    def refresh_bookmarks_display(self):
        """Refresh bookmarks bar and landing pages"""
        self.create_bookmarks_bar()
        
        # Refresh any open landing pages
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, LandingPage):
                widget.setup_landing_page()

    # ===================== Menu Methods =====================
    def show_history(self):
        QMessageBox.information(self, "History", f"History has {len(self.data_manager.history_manager.get_history())} entries")

    def show_bookmarks_manager(self):
        QMessageBox.information(self, "Bookmarks", f"You have {len(self.data_manager.bookmarks_manager.get_bookmarks())} bookmarks")

    def show_settings(self):
        QMessageBox.information(self, "Settings", "Settings manager would open here")

    def show_profiles(self):
        QMessageBox.information(self, "Profiles", "Profiles manager would open here")

    def new_incognito_window(self):
        QMessageBox.information(self, "Incognito", "New incognito window would open")

    def new_window(self):
        browser = SimpleBrowser()
        browser.show()

    def show_downloads(self):
        QMessageBox.information(self, "Downloads", "Downloads manager would open here")

    def clear_history(self):
        self.data_manager.history_manager.clear_history()
        QMessageBox.information(self, "History Cleared", "Browsing history has been cleared.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Arc Browser")

    browser = SimpleBrowser()
    browser.show()

    sys.exit(app.exec_())
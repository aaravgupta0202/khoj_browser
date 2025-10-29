# internal_pages.py (COMPLETELY FIXED)
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
import os

class InternalPage(QWebEngineView):
    page_requested = pyqtSignal(str)
    setting_changed = pyqtSignal(dict)
    history_cleared = pyqtSignal()
    bookmark_added = pyqtSignal(str, str)
    bookmark_deleted = pyqtSignal(str)
    
    def __init__(self, page_type, data_manager=None):
        super().__init__()
        self.page_type = page_type
        self.data_manager = data_manager
        self.processing_navigation = False
        self.setup_page()
        
    def setup_page(self):
        # Load the appropriate HTML file
        html_file = f"{self.page_type}.html"
        if os.path.exists(html_file):
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Inject data into the HTML
            if self.page_type == 'history' and self.data_manager:
                history_data = self.data_manager.history_manager.get_history()
                injected_data = f"window.historyData = {json.dumps(history_data)};"
            elif self.page_type == 'bookmarks' and self.data_manager:
                bookmarks_data = self.data_manager.bookmarks_manager.get_bookmarks()
                injected_data = f"window.bookmarksData = {json.dumps(bookmarks_data)};"
            elif self.page_type == 'settings' and self.data_manager:
                settings_data = self.data_manager.settings_manager.settings
                injected_data = f"window.settingsData = {json.dumps(settings_data)};"
            else:
                injected_data = "window.historyData = []; window.bookmarksData = []; window.settingsData = {};"
            
            # Inject the data and load the page
            full_html = html_content.replace('</head>', f'<script>{injected_data}</script></head>')
            
            # Temporarily disconnect to prevent loops
            try:
                self.urlChanged.disconnect()
            except:
                pass
                
            self.setHtml(full_html, QUrl(f"arc://{self.page_type}/"))
            
            # Reconnect after a delay
            QTimer.singleShot(100, self.reconnect_signals)
            
        else:
            # Fallback content
            fallback_html = f"""
                <html>
                    <body style="background: #1a1a1a; color: white; font-family: Arial; padding: 40px; text-align: center;">
                        <h1>{self.page_type.title()} Page</h1>
                        <p>This is the {self.page_type} page for Arc Browser</p>
                        <button onclick="window.location.href='arc://newtab'" 
                                style="padding: 10px 20px; background: #ff6f3c; color: white; border: none; border-radius: 5px; cursor: pointer;">
                            Back to Browser
                        </button>
                    </body>
                </html>
            """
            
            try:
                self.urlChanged.disconnect()
            except:
                pass
                
            self.setHtml(fallback_html, QUrl(f"arc://{self.page_type}/"))
            QTimer.singleShot(100, self.reconnect_signals)
    
    def reconnect_signals(self):
        """Reconnect signals after page load"""
        try:
            self.urlChanged.disconnect()
        except:
            pass
        self.urlChanged.connect(self.handle_internal_navigation)
        
    def handle_internal_navigation(self, url):
        url_str = url.toString()
        
        # Skip if we're already processing or if it's the current page URL
        if (self.processing_navigation or 
            url_str == f"arc://{self.page_type}/" or
            not url_str.startswith("arc://")):
            return
            
        self.processing_navigation = True
        print(f"Internal page handling: {url_str}")
        
        try:
            if url_str.startswith("arc://navigate/"):
                target_url = url_str[15:]  # Remove "arc://navigate/"
                self.page_requested.emit(target_url)
                
            elif url_str.startswith("arc://search/"):
                query = url_str[13:]  # Remove "arc://search/"
                self.page_requested.emit(query)
                
            elif url_str == "arc://clear-history":
                self.history_cleared.emit()
                QTimer.singleShot(500, self.setup_page)  # Refresh after clearing
                
            elif url_str.startswith("arc://add-bookmark/"):
                parts = url_str[19:].split('/')
                if len(parts) >= 2:
                    title = QUrl.fromPercentEncoding(parts[0].encode())
                    bookmark_url = QUrl.fromPercentEncoding(parts[1].encode())
                    self.bookmark_added.emit(title, bookmark_url)
                    QTimer.singleShot(500, self.setup_page)  # Refresh after adding
                    
            elif url_str.startswith("arc://delete-bookmark/"):
                bookmark_url = QUrl.fromPercentEncoding(url_str[22:].encode())
                self.bookmark_deleted.emit(bookmark_url)
                QTimer.singleShot(500, self.setup_page)  # Refresh after deleting
                
            elif url_str.startswith("arc://save-settings/"):
                settings_json = QUrl.fromPercentEncoding(url_str[20:].encode())
                try:
                    settings = json.loads(settings_json)
                    self.setting_changed.emit(settings)
                    self.show_success_message("Settings saved successfully!")
                except Exception as e:
                    print(f"Error saving settings: {e}")
                    
            elif url_str == "arc://reset-settings":
                self.setting_changed.emit({})
                QTimer.singleShot(500, self.setup_page)  # Refresh after reset
                
            elif url_str.startswith("arc://"):
                # Handle other arc:// URLs
                self.page_requested.emit(url_str)
                
        finally:
            # Reset processing flag after a delay to prevent immediate re-triggering
            QTimer.singleShot(100, lambda: setattr(self, 'processing_navigation', False))
    
    def show_success_message(self, message):
        """Show a success message without triggering navigation"""
        success_html = f"""
            <html>
                <body style="background: #1a1a1a; color: white; font-family: Arial; padding: 40px; text-align: center;">
                    <h1 style="color: #4CAF50;">✓ Success</h1>
                    <p>{message}</p>
                    <button onclick="window.location.href='arc://{self.page_type}'" 
                            style="padding: 10px 20px; background: #ff6f3c; color: white; border: none; border-radius: 5px; cursor: pointer;">
                        Back to {self.page_type.title()}
                    </button>
                </body>
            </html>
        """
        
        # Disconnect temporarily to prevent loops
        try:
            self.urlChanged.disconnect()
        except:
            pass
            
        self.setHtml(success_html, QUrl(f"arc://{self.page_type}-success/"))
        
        # Reconnect after a delay
        QTimer.singleShot(100, self.reconnect_signals)
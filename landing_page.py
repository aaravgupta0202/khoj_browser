# landing_page.py (FIXED ASSETS AND BOOKMARKS)
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
import os
import urllib.parse

class LandingPage(QWebEngineView):
    search_requested = pyqtSignal(str)
    url_requested = pyqtSignal(str)
    background_changed = pyqtSignal(str)
    
    def __init__(self, bookmarks_manager=None, settings_manager=None):
        super().__init__()
        self.bookmarks_manager = bookmarks_manager
        self.settings_manager = settings_manager
        self.setup_landing_page()
        
    def setup_landing_page(self):
        # Get current background setting
        background_style = self.get_background_style()
        
        # Get bookmarks data
        bookmarks_data = []
        if self.bookmarks_manager:
            bookmarks_data = self.bookmarks_manager.get_bookmarks()
        
        # Load and modify the HTML
        html_file = "landing_page.html"
        if os.path.exists(html_file):
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Inject data and fix asset paths
            html_content = self.inject_data_and_fix_paths(html_content, background_style, bookmarks_data)
            
            self.setHtml(html_content, QUrl("arc://newtab/"))
        else:
            # Fallback HTML
            self.setHtml(self.create_fallback_html(background_style, bookmarks_data), QUrl("arc://newtab/"))
        
        self.urlChanged.connect(self.handle_navigation)
        
    def get_background_style(self):
        """Get background style from settings or use default"""
        if self.settings_manager:
            bg_type = self.settings_manager.get('appearance', 'background_type', 'preset')
            if bg_type == 'preset':
                preset_num = self.settings_manager.get('appearance', 'preset_bg', 9)
                return f"url('assets/backgrounds/bg{preset_num}.jpg')"
            elif bg_type == 'color':
                color = self.settings_manager.get('appearance', 'background_color', '#1a1a2e')
                return color
            elif bg_type == 'gradient':
                gradient = self.settings_manager.get('appearance', 'background_gradient', 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)')
                return gradient
        return "url('assets/backgrounds/bg9.jpg')"
    
    def inject_data_and_fix_paths(self, html_content, background_style, bookmarks_data):
        """Inject data and fix asset paths in HTML"""
        # Fix asset paths - convert to file URLs
        html_content = html_content.replace('src="assets/', f'src="file:///{os.path.abspath("assets")}/')
        html_content = html_content.replace('url("assets/', f'url("file:///{os.path.abspath("assets")}/')
        
        # Replace background
        html_content = html_content.replace(
            'background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);',
            f'background: {background_style};'
        )
        
        # Inject data
        injected_data = f"""
        <script>
            window.landingBookmarks = {json.dumps(bookmarks_data)};
            window.currentBackground = "{background_style}";
        </script>
        """
        
        return html_content.replace('</head>', f'{injected_data}</head>')
    
    def create_fallback_html(self, background_style, bookmarks_data):
        """Create fallback HTML if landing_page.html doesn't exist"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ARC | New Tab</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: "Inter", sans-serif;
                }}

                body {{
                    background: {background_style};
                    min-height: 100vh;
                    color: #fff;
                    overflow-y: auto;
                }}

                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 40px 20px;
                }}

                .top-info {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 40px;
                    background: rgba(25, 25, 25, 0.6);
                    border-radius: 15px;
                    padding: 20px 30px;
                    backdrop-filter: blur(12px);
                }}

                .time {{
                    font-size: 1.8rem;
                    font-weight: 600;
                }}

                .weather {{
                    font-size: 1.1rem;
                    opacity: 0.9;
                }}

                .title {{
                    font-size: 4rem;
                    font-weight: 700;
                    text-align: center;
                    margin-bottom: 10px;
                    background: linear-gradient(135deg, #ff6f3c 0%, #ff9c7a 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}

                .subtitle {{
                    font-size: 1.2rem;
                    text-align: center;
                    opacity: 0.8;
                    margin-bottom: 40px;
                }}

                .search-bar {{
                    display: flex;
                    align-items: center;
                    background: rgba(255,255,255,0.1);
                    border-radius: 50px;
                    padding: 15px 25px;
                    margin-bottom: 50px;
                    max-width: 600px;
                    margin-left: auto;
                    margin-right: auto;
                    backdrop-filter: blur(10px);
                }}

                .search-bar input {{
                    flex: 1;
                    background: transparent;
                    border: none;
                    outline: none;
                    color: white;
                    font-size: 1.1rem;
                    padding: 10px 15px;
                }}

                .search-bar button {{
                    background: #ff6f3c;
                    border: none;
                    border-radius: 50%;
                    width: 44px;
                    height: 44px;
                    cursor: pointer;
                    transition: 0.3s;
                    font-size: 1.2rem;
                }}

                .search-bar button:hover {{
                    background: #ff8358;
                    transform: scale(1.1);
                }}

                .bookmarks-section {{
                    background: rgba(25, 25, 25, 0.6);
                    border-radius: 20px;
                    padding: 30px;
                    margin-bottom: 30px;
                    backdrop-filter: blur(12px);
                }}

                .bookmarks-title {{
                    color: #ff6f3c;
                    font-size: 1.4rem;
                    font-weight: 600;
                    margin-bottom: 25px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}

                .bookmarks-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
                    gap: 15px;
                }}

                .bookmark-item {{
                    background: rgba(255,255,255,0.08);
                    border-radius: 12px;
                    padding: 20px 15px;
                    text-align: center;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    text-decoration: none;
                    color: #ddd;
                    border: 1px solid rgba(255,255,255,0.1);
                }}

                .bookmark-item:hover {{
                    background: rgba(255,111,60,0.2);
                    transform: translateY(-5px);
                    border-color: rgba(255,111,60,0.3);
                }}

                .bookmark-favicon {{
                    width: 32px;
                    height: 32px;
                    margin: 0 auto 10px;
                    border-radius: 8px;
                    background: rgba(255,255,255,0.1);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.2rem;
                }}

                .bookmark-name {{
                    font-weight: 500;
                    font-size: 0.9rem;
                    line-height: 1.3;
                }}

                .no-bookmarks {{
                    text-align: center;
                    padding: 40px;
                    opacity: 0.7;
                    font-style: italic;
                }}

                .quick-links {{
                    display: flex;
                    justify-content: center;
                    gap: 15px;
                    flex-wrap: wrap;
                    margin-bottom: 30px;
                }}

                .quick-links a {{
                    background: rgba(255,255,255,0.1);
                    border-radius: 12px;
                    padding: 12px 20px;
                    text-decoration: none;
                    color: #fff;
                    font-weight: 500;
                    transition: 0.3s;
                }}

                .quick-links a:hover {{
                    background: #ff6f3c;
                    transform: translateY(-2px);
                }}

                .customize-btn {{
                    position: fixed;
                    bottom: 25px;
                    right: 25px;
                    background: #ff6f3c;
                    color: #fff;
                    border: none;
                    border-radius: 50%;
                    width: 60px;
                    height: 60px;
                    font-size: 1.5rem;
                    cursor: pointer;
                    box-shadow: 0 0 20px rgba(0,0,0,0.3);
                    transition: 0.3s;
                    z-index: 10;
                }}

                .customize-btn:hover {{
                    background: #ff845d;
                    transform: scale(1.1);
                }}
            </style>
            <script>
                window.landingBookmarks = {json.dumps(bookmarks_data)};
                window.currentBackground = "{background_style}";
            </script>
        </head>
        <body>
            <div class="container">
                <div class="top-info">
                    <div class="time" id="time">12:00 PM</div>
                    <div class="weather">
                        <span id="weather-icon">☀️</span>
                        <span id="temperature">24°C</span> |
                        <span id="weather-desc">Sunny</span> |
                        <span id="weather-location">Manipal, India</span>
                    </div>
                </div>

                <h1 class="title">ARC</h1>
                <p class="subtitle">Your Modern Web Browser</p>

                <div class="search-bar">
                    <input type="text" id="searchInput" placeholder="Search Google or enter address...">
                    <button onclick="performSearch()">🔍</button>
                </div>

                <div class="bookmarks-section">
                    <div class="bookmarks-title">
                        <span>⭐ Your Bookmarks</span>
                        <button onclick="openBookmarksManager()" style="background: rgba(255,111,60,0.3); color: white; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 0.9rem;">Manage</button>
                    </div>
                    <div class="bookmarks-grid" id="bookmarksContainer"></div>
                </div>

                <div class="quick-links">
                    <a href="arc://navigate/https://www.google.com">Google</a>
                    <a href="arc://navigate/https://www.youtube.com">YouTube</a>
                    <a href="arc://navigate/https://github.com">GitHub</a>
                    <a href="arc://navigate/https://mail.google.com">Gmail</a>
                    <a href="arc://navigate/https://twitter.com">Twitter</a>
                </div>
            </div>

            <button class="customize-btn" onclick="openCustomize()">✏️</button>

            <script>
                function loadBookmarks() {{
                    const bookmarks = window.landingBookmarks || [];
                    const container = document.getElementById('bookmarksContainer');
                    
                    if (bookmarks.length === 0) {{
                        container.innerHTML = '<div class="no-bookmarks">No bookmarks yet. Add some from the browser menu!</div>';
                        return;
                    }}
                    
                    container.innerHTML = '';
                    bookmarks.forEach(bookmark => {{
                        const faviconUrl = `https://www.google.com/s2/favicons?domain=${{new URL(bookmark.url).hostname}}&sz=32`;
                        const bookmarkElement = document.createElement('a');
                        bookmarkElement.className = 'bookmark-item';
                        bookmarkElement.href = `arc://navigate/${{bookmark.url}}`;
                        bookmarkElement.innerHTML = `
                            <div class="bookmark-favicon">
                                <img src="${{faviconUrl}}" width="24" height="24" onerror="this.style.display='none'; this.parentNode.innerHTML='🌐';">
                            </div>
                            <div class="bookmark-name">${{escapeHtml(bookmark.title)}}</div>
                        `;
                        container.appendChild(bookmarkElement);
                    }});
                }}
                
                function escapeHtml(text) {{
                    const div = document.createElement('div');
                    div.textContent = text;
                    return div.innerHTML;
                }}
                
                function performSearch() {{
                    const query = document.getElementById("searchInput").value.trim();
                    if (query) {{
                        window.location.href = `arc://search/${{encodeURIComponent(query)}}`;
                    }}
                }}
                
                function openBookmarksManager() {{
                    window.location.href = 'arc://bookmarks/';
                }}
                
                function openCustomize() {{
                    window.location.href = 'arc://settings/';
                }}
                
                // Allow Enter key in search
                document.getElementById("searchInput").addEventListener("keypress", function(event) {{
                    if (event.key === "Enter") {{
                        performSearch();
                    }}
                }});
                
                // Update time
                function updateTime() {{
                    const now = new Date();
                    document.getElementById('time').textContent = now.toLocaleTimeString([], {{ 
                        hour: '2-digit', minute: '2-digit' 
                    }});
                }}
                
                setInterval(updateTime, 1000);
                updateTime();
                
                // Load bookmarks when page loads
                loadBookmarks();
            </script>
        </body>
        </html>
        """
        
    def handle_navigation(self, url):
        url_str = url.toString()
        
        if url_str.startswith("arc://navigate/"):
            target_url = url_str[15:]
            self.url_requested.emit(target_url)
            
        elif url_str.startswith("arc://search/"):
            query = url_str[13:]
            self.search_requested.emit(query)
            
        elif url_str.startswith("arc://background/"):
            # Handle background change requests
            background_data = url_str[17:]
            self.background_changed.emit(background_data)
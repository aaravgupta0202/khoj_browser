from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import json
import os

class BookmarksManager:
    def __init__(self):
        self.bookmarks = []
        # Start with NO default bookmarks
        
    def add_bookmark(self, title, url):
        bookmark = {'title': title, 'url': url}
        self.bookmarks.append(bookmark)
        
    def get_bookmarks(self):
        return self.bookmarks
        
    def remove_bookmark(self, url):
        self.bookmarks = [b for b in self.bookmarks if b['url'] != url]
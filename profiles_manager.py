import os
import json
import shutil
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Profile:
    def __init__(self, name, email="", pfp_path=""):
        self.name = name
        self.email = email
        self.pfp_path = pfp_path
        self.settings = {
            'theme': 'dark',
            'background': 'default',
            'bookmarks': [],
            'history': []
        }
        
    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'pfp_path': self.pfp_path,
            'settings': self.settings
        }
        
    @classmethod
    def from_dict(cls, data):
        profile = cls(data['name'], data.get('email', ''), data.get('pfp_path', ''))
        profile.settings = data.get('settings', {})
        return profile

class ProfilesManager:
    def __init__(self):
        self.profiles_dir = "profiles"
        self.current_profile = None
        self.profiles = []
        self.load_profiles()
        
    def load_profiles(self):
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir)
            
        self.profiles = []
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.profiles_dir, filename), 'r') as f:
                    data = json.load(f)
                    self.profiles.append(Profile.from_dict(data))
                    
        if not self.profiles:
            self.create_default_profile()
            
    def create_default_profile(self):
        default_profile = Profile("Default")
        self.add_profile(default_profile)
        self.current_profile = default_profile
        
    def add_profile(self, profile):
        self.profiles.append(profile)
        self.save_profile(profile)
        
    def save_profile(self, profile):
        filename = f"{profile.name.lower().replace(' ', '_')}.json"
        with open(os.path.join(self.profiles_dir, filename), 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)
            
    def get_profile(self, name):
        for profile in self.profiles:
            if profile.name == name:
                return profile
        return None
        
    def delete_profile(self, profile):
        if profile in self.profiles:
            self.profiles.remove(profile)
            filename = f"{profile.name.lower().replace(' ', '_')}.json"
            filepath = os.path.join(self.profiles_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)

class ProfileDialog(QDialog):
    def __init__(self, profiles_manager, parent=None):
        super().__init__(parent)
        self.profiles_manager = profiles_manager
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Profiles")
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout()
        
        # Current profile
        current_group = QGroupBox("Current Profile")
        current_layout = QHBoxLayout()
        
        self.current_profile_label = QLabel("No profile selected")
        self.current_profile_pic = QLabel()
        self.current_profile_pic.setFixedSize(50, 50)
        self.current_profile_pic.setStyleSheet("border-radius: 25px; border: 2px solid #ff6f3c;")
        
        current_layout.addWidget(self.current_profile_pic)
        current_layout.addWidget(self.current_profile_label)
        current_layout.addStretch()
        
        current_group.setLayout(current_layout)
        layout.addWidget(current_group)
        
        # Profiles list
        layout.addWidget(QLabel("Available Profiles:"))
        self.profiles_list = QListWidget()
        self.load_profiles()
        self.profiles_list.itemSelectionChanged.connect(self.on_profile_selected)
        layout.addWidget(self.profiles_list)
        
        # Profile actions
        action_layout = QHBoxLayout()
        self.switch_btn = QPushButton("Switch to Profile")
        self.switch_btn.clicked.connect(self.switch_profile)
        self.delete_btn = QPushButton("Delete Profile")
        self.delete_btn.clicked.connect(self.delete_profile)
        
        action_layout.addWidget(self.switch_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        # Add new profile
        add_group = QGroupBox("Add New Profile")
        add_layout = QHBoxLayout()
        
        self.new_name_input = QLineEdit()
        self.new_name_input.setPlaceholderText("Profile Name")
        self.new_email_input = QLineEdit()
        self.new_email_input.setPlaceholderText("Email (optional)")
        
        self.pfp_btn = QPushButton("Choose Picture")
        self.pfp_btn.clicked.connect(self.choose_pfp)
        self.pfp_path = ""
        
        add_btn = QPushButton("Add Profile")
        add_btn.clicked.connect(self.add_profile)
        
        add_layout.addWidget(QLabel("Name:"))
        add_layout.addWidget(self.new_name_input)
        add_layout.addWidget(QLabel("Email:"))
        add_layout.addWidget(self.new_email_input)
        add_layout.addWidget(self.pfp_btn)
        add_layout.addWidget(add_btn)
        
        add_group.setLayout(add_layout)
        layout.addWidget(add_group)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        self.update_current_display()
        
    def load_profiles(self):
        self.profiles_list.clear()
        for profile in self.profiles_manager.profiles:
            item = QListWidgetItem(profile.name)
            item.setData(Qt.UserRole, profile)
            self.profiles_list.addItem(item)
            
    def update_current_display(self):
        if self.profiles_manager.current_profile:
            profile = self.profiles_manager.current_profile
            self.current_profile_label.setText(f"{profile.name}\n{profile.email}")
            
            if profile.pfp_path and os.path.exists(profile.pfp_path):
                pixmap = QPixmap(profile.pfp_path)
                self.current_profile_pic.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.current_profile_pic.clear()
                
    def on_profile_selected(self):
        selected = self.profiles_list.currentItem()
        self.switch_btn.setEnabled(selected is not None)
        self.delete_btn.setEnabled(selected is not None and selected.data(Qt.UserRole).name != "Default")
        
    def switch_profile(self):
        selected = self.profiles_list.currentItem()
        if selected:
            profile = selected.data(Qt.UserRole)
            self.profiles_manager.current_profile = profile
            self.update_current_display()
            QMessageBox.information(self, "Profile Switched", f"Switched to {profile.name}")
            
    def delete_profile(self):
        selected = self.profiles_list.currentItem()
        if selected:
            profile = selected.data(Qt.UserRole)
            if profile.name == "Default":
                QMessageBox.warning(self, "Cannot Delete", "Cannot delete the default profile")
                return
                
            reply = QMessageBox.question(self, "Delete Profile", 
                                       f"Are you sure you want to delete profile '{profile.name}'?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.profiles_manager.delete_profile(profile)
                self.load_profiles()
                self.update_current_display()
                
    def choose_pfp(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Profile Picture", "", 
                                                "Images (*.png *.jpg *.jpeg *.bmp)")
        if filename:
            self.pfp_path = filename
            
    def add_profile(self):
        name = self.new_name_input.text().strip()
        email = self.new_email_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a profile name")
            return
            
        if self.profiles_manager.get_profile(name):
            QMessageBox.warning(self, "Error", "Profile name already exists")
            return
            
        profile = Profile(name, email, self.pfp_path)
        self.profiles_manager.add_profile(profile)
        
        self.new_name_input.clear()
        self.new_email_input.clear()
        self.pfp_path = ""
        
        self.load_profiles()
        QMessageBox.information(self, "Success", f"Profile '{name}' created")
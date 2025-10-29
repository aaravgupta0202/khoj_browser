import PyInstaller.__main__
import os
import shutil

def build_executable():
    # Clean up previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
        
    PyInstaller.__main__.run([
        'main.py',
        '--name=SimpleBrowser',
        '--windowed',
        '--onefile',
        '--noconsole'
    ])

if __name__ == '__main__':
    build_executable()
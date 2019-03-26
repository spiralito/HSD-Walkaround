#!/usr/bin/env python
import sys
from cx_Freeze import setup, Executable

# Dependency list.
build_exe_options = {
    'packages': ['asyncio', 'numpy', 'pygame'], 
    'excludes': ['tkinter', 'matplotlib', 'scipy'],
    'include_files': ['assets']
}
# Base for GUI apps on Windows.
base = 'Win32GUI' if sys.platform == 'win32' else None

setup(
    name = 'HSD Walkaround',
    version = '1.1',
    description = 'Homestuck & Hiveswap Discord Walkaround Game',
    url = '',
    author = 'virtuNat',
    author_email = '',
    license = 'MIT',
    options = {'build_exe': build_exe_options},
    executables = [Executable(
        script='game.py',
        base=base,
        icon='icon.ico',
        targetName='Walkaround.exe'
        )],
    )

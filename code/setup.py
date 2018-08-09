#setup.py
import sys, os
from cx_Freeze import setup, Executable

__version__ = "1.0"

include_files = ['exit.png', 'folder.png', 'selectall.png', 'chromeOFF.png', 'chromeON.png', 'ICO.png', 'run.png', 'save.png', 'deselect.png']
excludes = ["tkinter"]
packages = ["os", "wx", "psutil","shutil"]

setup(
    name = "RTR",
    description='Robot Test Runner',
    version=__version__,
    options = {"build_exe": {
    'packages': packages,
    'include_files': include_files,
    'excludes': excludes,
    'include_msvcr': True,
}},
executables = [Executable("app.py", base = "Win32GUI")]
)

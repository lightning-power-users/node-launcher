import os
import subprocess

from pathlib import Path
from PySide2.QtWidgets import QErrorMessage

from node_launcher.constants import IS_MACOS, IS_LINUX, IS_WINDOWS, OPERATING_SYSTEM


def reveal(path: str):
    try:
        if IS_MACOS:
            contents = os.listdir(path)
            contents.sort()
            if contents:
                path = os.path.join(path, contents[0])
            subprocess.call(['open', '-R', path])
        elif IS_WINDOWS:
            subprocess.call(f'explorer "{Path(path)}"', shell=True)
        elif IS_LINUX:
            subprocess.call(["xdg-open", path])
        else:
            raise NotImplementedError(f'reveal method has not been implemented for {OPERATING_SYSTEM}')
    except (FileNotFoundError, NotADirectoryError):
        QErrorMessage().showMessage(f'{path} not found')
        return

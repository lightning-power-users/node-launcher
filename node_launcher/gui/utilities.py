import os
import subprocess

from pathlib import Path
from PySide2.QtGui import QClipboard
from PySide2.QtWidgets import QErrorMessage

from node_launcher.constants import IS_MACOS, IS_WINDOWS, OPERATING_SYSTEM


def copy_to_clipboard(text: str):
    QClipboard().setText(text)


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
        else:
            raise NotImplementedError(f'reveal method has not been implemented for {OPERATING_SYSTEM}')
    except (FileNotFoundError, NotADirectoryError):
        QErrorMessage().showMessage(f'{path} not found')
        return

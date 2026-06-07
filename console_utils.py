import ctypes
import logging
import sys
from ctypes import wintypes


STD_INPUT_HANDLE = -10
ENABLE_QUICK_EDIT_MODE = 0x0040
ENABLE_EXTENDED_FLAGS = 0x0080
BELOW_NORMAL_PRIORITY_CLASS = 0x00004000


def without_quick_edit(mode):
    return (mode | ENABLE_EXTENDED_FLAGS) & ~ENABLE_QUICK_EDIT_MODE


def disable_quick_edit(logger=None):
    if sys.platform != "win32":
        return False

    logger = logger or logging.getLogger(__name__)
    kernel32 = ctypes.windll.kernel32
    kernel32.GetStdHandle.argtypes = [wintypes.DWORD]
    kernel32.GetStdHandle.restype = wintypes.HANDLE
    kernel32.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel32.GetConsoleMode.restype = wintypes.BOOL
    kernel32.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.SetConsoleMode.restype = wintypes.BOOL

    handle = kernel32.GetStdHandle(STD_INPUT_HANDLE)
    mode = wintypes.DWORD()
    if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        logger.debug("Unable to read console mode")
        return False

    new_mode = without_quick_edit(mode.value)
    if new_mode == mode.value:
        return True

    if not kernel32.SetConsoleMode(handle, new_mode):
        logger.debug("Unable to disable console QuickEdit mode")
        return False
    return True


def set_below_normal_priority(logger=None):
    if sys.platform != "win32":
        return False

    logger = logger or logging.getLogger(__name__)
    kernel32 = ctypes.windll.kernel32
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    kernel32.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.SetPriorityClass.restype = wintypes.BOOL

    handle = kernel32.GetCurrentProcess()
    if not kernel32.SetPriorityClass(handle, BELOW_NORMAL_PRIORITY_CLASS):
        logger.debug("Unable to lower process priority")
        return False
    return True

import ctypes
import sys
import subprocess
from ctypes import wintypes
from pathlib import Path

class STARTUPINFOW(ctypes.Structure):
    _fields_ = [
        ('cb', wintypes.DWORD),
        ('lpReserved', wintypes.LPWSTR),
        ('lpDesktop', wintypes.LPWSTR),
        ('lpTitle', wintypes.LPWSTR),
        ('dwX', wintypes.DWORD),
        ('dwY', wintypes.DWORD),
        ('dwXSize', wintypes.DWORD),
        ('dwYSize', wintypes.DWORD),
        ('dwXCountChars', wintypes.DWORD),
        ('dwYCountChars', wintypes.DWORD),
        ('dwFillAttribute', wintypes.DWORD),
        ('dwFlags', wintypes.DWORD),
        ('wShowWindow', wintypes.WORD),
        ('cbReserved2', wintypes.WORD),
        ('lpReserved2', ctypes.c_char_p),
        ('hStdInput', wintypes.HANDLE),
        ('hStdOutput', wintypes.HANDLE),
        ('hStdError', wintypes.HANDLE)
    ]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('hProcess', wintypes.HANDLE),
        ('hThread', wintypes.HANDLE),
        ('dwProcessId', wintypes.DWORD),
        ('dwThreadId', wintypes.DWORD)
    ]

def launch_on_desktop(command_line, cwd=None):
    si = STARTUPINFOW()
    si.cb = ctypes.sizeof(STARTUPINFOW)
    si.lpDesktop = r"WinSta0\Default"
    # STARTF_USESHOWWINDOW = 1, SW_SHOWNORMAL = 1
    si.dwFlags = 1
    si.wShowWindow = 1

    pi = PROCESS_INFORMATION()
    # CREATE_NEW_CONSOLE = 0x00000010
    flags = 0x00000010
    
    success = ctypes.windll.kernel32.CreateProcessW(
        None,
        command_line,
        None,
        None,
        False,
        flags,
        None,
        str(cwd) if cwd else None,
        ctypes.byref(si),
        ctypes.byref(pi)
    )
    if not success:
        err = ctypes.GetLastError()
        raise RuntimeError(f"CreateProcessW failed with error code {err}")
    return pi

if __name__ == "__main__":
    print("[*] Testing launch on desktop...")
    # Test launching chrome or cmd
    cmd = r'"C:\Program Files\Google\Chrome\Application\chrome.exe" --new-window "https://businessclass.punjab.gov.in/login"'
    pi = launch_on_desktop(cmd)
    print(f"[OK] Launched Chrome with PID {pi.dwProcessId}")

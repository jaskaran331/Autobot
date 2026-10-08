import ctypes
import sys
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

def launch_on_user_desktop(cmd_line, cwd=None):
    si = STARTUPINFOW()
    si.cb = ctypes.sizeof(STARTUPINFOW)
    si.lpDesktop = r"WinSta0\Default"
    si.dwFlags = 1  # STARTF_USESHOWWINDOW
    si.wShowWindow = 1  # SW_SHOWNORMAL

    pi = PROCESS_INFORMATION()
    # 0x00000010 = CREATE_NEW_CONSOLE
    flags = 0x00000010
    
    success = ctypes.windll.kernel32.CreateProcessW(
        None,
        cmd_line,
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

def main():
    agent_dir = Path(__file__).parent.resolve()
    bat_file = agent_dir / "run_login.bat"
    cmd = f'cmd.exe /c "{bat_file}"'
    
    print("[*] Spawning interactive console & browser on user desktop (WinSta0\\Default)...")
    pi = launch_on_user_desktop(cmd, cwd=agent_dir)
    print(f"[OK] Process spawned with PID: {pi.dwProcessId}")
    return pi.dwProcessId

if __name__ == "__main__":
    main()

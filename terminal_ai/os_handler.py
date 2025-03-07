import platform

def get_os_type():
    """Detect the current operating system."""
    os_type = platform.system().lower()
    
    if os_type == 'linux':
        return 'linux'
    elif os_type == 'darwin':
        return 'macos'
    elif os_type == 'windows':
        return 'windows'
    else:
        raise EnvironmentError("Unsupported OS detected.")

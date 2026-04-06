import platform
import socket
import Utils.Logger as logger 

log = logger.LoggerClass(0, "osHelper.py")


def get_operating_system():
    """
    Return a normalized OS name, e.g. 'Windows', 'Linux', 'Darwin' (macOS).
    """
    try:
        os_name = platform.system()  # 'Windows', 'Linux', 'Darwin', etc.
        log.debug(f"Detected operating system: {os_name}")
        return os_name
    except Exception as e:
        log.error(f"Error detecting operating system: {e}")
        return None


def get_architecture():
    """
    Return the machine architecture, e.g. 'x86_64', 'AMD64', 'arm64'.
    """
    try:
        arch = platform.machine()
        log.debug(f"Detected architecture: {arch}")
        return arch
    except Exception as e:
        log.error(f"Error detecting architecture: {e}")
        return None


def get_active_hostname():
    """
    Return the current hostname of the machine.
    """
    try:
        hostname = socket.gethostname()
        log.debug(f"Detected hostname: {hostname}")
        return hostname
    except Exception as e:
        log.error(f"Error detecting hostname: {e}")
        return None

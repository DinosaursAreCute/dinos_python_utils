import logging
from pathlib import *

import Utils.Logger

# ======================== Initialization ========================
log = Utils.Logger.LoggerClass(logger_name="FileOperationsLogger",logger_level = 0,log_color = True)


# ======================== Common Utils ========================

def convert_string_to_path(target_path):
    log.debug(f"Converting {target_path} to Path object")
    return Path(target_path)


# ======================== Directory Utils ========================#

def check_is_directory(target_directory):
    is_dir= target_directory.is_dir()
    log.debug(f"{target_directory} is directory = {is_dir}")
    if not is_dir:
        log.info(f"{target_directory} is not a directory or does not exist")
        return False
    return True


def check_directory_exists(target_directory):
    if not target_directory.exists():
        log.debug(f"target directory does not exist. Target directory: ({target_directory})")
        return False
    return True


def list_subdirectories(root_path,recursive: bool = False):
    root = root_path if isinstance(root_path, Path) else Path(root_path)
    if not root.exists():
        log.debug(f"search path does not exist: {root}")
        return []
    if not root.is_dir():
        log.debug(f"search path is not a directory: {root}")
        return []
    if recursive:
        dirs = [p for p in root.rglob('*') if p.is_dir()]
        log.debug(f"found {len(dirs)} directories under {root} (recursive)")
        return dirs
    dirs = [p for p in root.iterdir() if p.is_dir()]
    log.debug(f"found {len(dirs)} immediate directories under {root}")
    return dirs


# ======================== File Utils ========================
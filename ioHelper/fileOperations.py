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

def list_files(root_path):
    root = root_path if isinstance(root_path,Path) else Path(root_path)
    if not root.exists():
        log.debug(f"search path does not exist: {root}")
    if not root.is_dir():
        log.debug(f"search path is not a directory: {root}")
        return []
    files= [f for f in root.iterdir() if not f.is_dir()]
    log.debug(f"found {len(files)} files under {root}")
    return files

def check_file_exists(file_path: Path) -> bool:
    if not file_path.exists():
        log.debug(f"File does not exist at path: {file_path}")
        return False
    if file_path.is_dir():
        log.debug(f"Requested file is a directory: {file_path}")
        return False
    return True

def delete_file(file_path) -> bool:
    file_path = file_path if isinstance(file_path, Path) else Path(file_path)
    log.debug(f"Trying to remove file: {file_path}")
    try:
        file_path.unlink()
    except FileNotFoundError:
        log.error(f"Tried to remove file: {file_path} but file does not exist")
        return False
    if not file_path.exists():
        log.success(f"Successfully removed {file_path}")
        return True
    else:
        log.error(f"Failed to remove file: {file_path}")
        return False

def create_file(file_path,replace_existing: bool = False)-> bool :
    file_path = file_path if isinstance(file_path, Path) else Path(file_path)
    log.debug(f"Trying to create file: {file_path}")
    if file_path.exists() and not replace_existing:
        log.error(f"File: {file_path} already exists and replace files is: False.")
        return False
    if file_path.exists():
        log.info(f"File: {file_path} already exists and will be replaced")

    try:
        file_path.touch()
    except Exception as e:
        log.error(f"Failed to create file due to: {e}")
        return False
    log.success(f"File: {file_path} was successfully replaced")
    return True

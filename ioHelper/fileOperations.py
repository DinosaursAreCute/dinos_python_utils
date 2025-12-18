import logging
from pathlib import *
import shutil
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

def check_file_exists(file_path) -> bool:
    file_path = file_path if isinstance(file_path, Path) else Path(file_path)
    if not file_path.exists():
        log.debug(f"File does not exist at path: {file_path}")
        return False
    if file_path.is_dir():
        log.debug(f"Requested file is a directory: {file_path}")
        return False
    return True

def delete_file(file_path) -> bool:
    file_path = file_path if isinstance(file_path, Path) else Path(file_path)
    log.info(f"Trying to remove file: {file_path}")
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
    log.info(f"Trying to create file: {file_path}")
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

def _transfer_file(source_file_path, target_file_path, operation: str,
                   replace_existing_target_file: bool = False,
                   create_file_if_not_exist: bool = False) -> bool:

    source = source_file_path if isinstance(source_file_path, Path) else Path(source_file_path)
    target = target_file_path if isinstance(target_file_path, Path) else Path(target_file_path)
    log.info(f"Attempting to {operation} file: {source} -> {target}")
    source_exists = check_file_exists(source)
    target_exists = check_file_exists(target)
    if source.is_dir():
        log.error(f"Source is a directory: {source}")
        return False
    if target.is_dir():
        log.error(f"Target is a directory: {target}")
        return False
    if not source_exists:
        if create_file_if_not_exist:
            if not create_file(target, replace_existing_target_file):
                log.error(f"Failed to create target file: {target}")
                return False
            log.success(f"Created target file {target} because source did not exist")
            return True
        log.error(f"Source file does not exist: {source}")
        return False
    if target_exists:
        if not replace_existing_target_file:
            log.error(f"Target already exists and replace not allowed: {target}")
            return False
        try:
            target.unlink()
        except Exception as e:
            log.error(f"Failed to remove existing target {target}: {e}")
            return False
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        log.error(f"Failed to ensure parent directory for target {target}: {e}")
        return False
    try:
        if operation == "move":
            shutil.move(str(source), str(target))
        elif operation == "copy":
            shutil.copy2(str(source), str(target))
        else:
            log.error(f"Unsupported operation: {operation}")
            return False
    except Exception as e:
        log.error(f"Failed to {operation} file: {source} -> {target}: {e}")
        return False
    if operation == "move":
        if source.exists() or not target.exists():
            log.error(f"Move failed: source exists={source.exists()}, target exists={target.exists()}")
            return False
    else:
        if not target.exists():
            log.error(f"Copy failed: target does not exist after copy: {target}")
            return False
    log.success(f"Successfully {operation}d file: {source} -> {target}")
    return True


def move_file(source_file_path, target_file_path, replace_existing_target_file: bool = False,
              create_file_if_not_exist: bool = False) -> bool:
    return _transfer_file(source_file_path, target_file_path, "move",
                          replace_existing_target_file, create_file_if_not_exist)


def copy_file(source_file_path, target_file_path, replace_existing_target_file: bool = False,
              create_file_if_not_exist: bool = False) -> bool:
    return _transfer_file(source_file_path, target_file_path, "copy",
                          replace_existing_target_file, create_file_if_not_exist)

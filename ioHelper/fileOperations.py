from pathlib import *
import shutil
import Utils.Logger
import fileinput
import yaml
# ======================== Initialization ========================
log = Utils.Logger.LoggerClass(logger_name="FileOperationsLogger",logger_level = 1,log_color = True)


# ======================== Common Utils ========================

def convert_string_to_path(path: str):
    """Convert a filesystem path string to a pathlib.Path object.

    Args:
        path (str): Path string to convert.

    Returns:
        pathlib.Path: Path object representing the given path.
    """
    log.debug(f"Converting {path} to Path object")
    return Path(path)


# ======================== Directory Utils ========================#

def check_is_directory(target_directory: Path)-> bool:
    """Return True if the provided path exists and is a directory.

    Args:
        target_directory (pathlib.Path): The path to validate.

    Returns:
        bool: True if the path exists and is a directory, False otherwise.
    """
    is_dir= target_directory.is_dir()
    log.debug(f"{target_directory} is directory = {is_dir}")
    if not is_dir:
        log.info(f"{target_directory} is not a directory or does not exist")
        return False
    return True


def check_directory_exists(target_directory: Path):
    """Return True if the provided directory path exists.

    Args:
        target_directory (pathlib.Path): Directory path to check.

    Returns:
        bool: True if the path exists, False otherwise.
    """
    if not target_directory.exists():
        log.debug(f"target directory does not exist. Target directory: ({target_directory})")
        return False
    return True


def list_subdirectories(root_path,recursive: bool = False):
    """List subdirectories under a root path.

    This function accepts either a Path or a string for `root_path`. If the
    path does not exist or is not a directory an empty list is returned.

    Args:
        root_path (str | pathlib.Path): Root path to search for subdirectories.
        recursive (bool): If True, include nested subdirectories (default False).

    Returns:
        list[pathlib.Path]: List of Path objects pointing to directories found
            under `root_path`. Returns an empty list when `root_path` is
            invalid.
    """
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
    """List non-directory entries directly under `root_path`.

    Args:
        root_path (str | pathlib.Path): Directory to list files from.

    Returns:
        list[pathlib.Path]: List of file Path objects. Returns an empty list if
            `root_path` does not exist or is not a directory.
    """
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
    """Return True when `file_path` exists and is a file (not a directory).

    Args:
        file_path (str | pathlib.Path): Path to the file to validate.

    Returns:
        bool: True if the path exists and refers to a regular file; False
            otherwise.
    """
    file_path = file_path if isinstance(file_path, Path) else Path(file_path)
    if not file_path.exists():
        log.debug(f"File does not exist at path: {file_path}")
        return False
    if file_path.is_dir():
        log.debug(f"Requested file is a directory: {file_path}")
        return False
    return True

def remove_file(file_path) -> bool:
    """Delete the file at `file_path`.

    Args:
        file_path (str | pathlib.Path): Path to the file to remove.

    Returns:
        bool: True if the file was removed successfully; False otherwise.

    Notes:
        - If the file does not exist, the function logs an error and returns
          False. FileNotFoundError is handled internally.
    """
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
    """Create an empty file at `file_path` (like `touch`).

    Args:
        file_path (str | pathlib.Path): Path where the file should be created.
        replace_existing (bool): If True, overwrite an existing file by
            touching it again; otherwise return False when the file exists.

    Returns:
        bool: True if the file was created (or replaced) successfully; False
            on error.
    """
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
    """Internal helper to move or copy files with shared validation.

    This centralizes common checks (existence, directory checks, parent
    directory creation) and dispatches to shutil.move or shutil.copy2.

    Args:
        source_file_path (str | pathlib.Path): Source file path.
        target_file_path (str | pathlib.Path): Destination file path.
        operation (str): Either "move" or "copy".
        replace_existing_target_file (bool): If True and the target exists,
            it will be removed before the operation.
        create_file_if_not_exist (bool): If True and the source does not
            exist, an empty target file will be created (uses
            `create_file`) and the function returns True.

    Returns:
        bool: True on success, False on failure.
    """
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
    log.success(f"Successful {operation} of file: {source} -> {target}")
    return True


def move_file(source_file_path, target_file_path, replace_existing_target_file: bool = False,
              create_file_if_not_exist: bool = False) -> bool:
    """Move a file from source to target using shared validation logic.

    Thin wrapper around :func:`_transfer_file`.

    Args:
        source_file_path (str | pathlib.Path): File to move.
        target_file_path (str | pathlib.Path): Destination path.
        replace_existing_target_file (bool): If True allow overwriting target.
        create_file_if_not_exist (bool): If True create the target if source
            is missing (see _transfer_file behavior).

    Returns:
        bool: True on success, False on failure.
    """
    return _transfer_file(source_file_path, target_file_path, "move",
                          replace_existing_target_file, create_file_if_not_exist)


def copy_file(source_file_path, target_file_path, replace_existing_target_file: bool = False,
              create_file_if_not_exist: bool = False) -> bool:
    """Copy a file from source to target using shared validation logic.

    Thin wrapper around :func:`_transfer_file`.

    Args:
        source_file_path (str | pathlib.Path): File to copy.
        target_file_path (str | pathlib.Path): Destination path.
        replace_existing_target_file (bool): If True allow overwriting target.
        create_file_if_not_exist (bool): If True create the target if source
            is missing (see _transfer_file behavior).

    Returns:
        bool: True on success, False on failure.
    """
    return _transfer_file(source_file_path, target_file_path, "copy",
                          replace_existing_target_file, create_file_if_not_exist)

def rename_file(file_path,name: str,replace_existing_file: bool = False) -> bool:
    """Rename a file to a new name within the same directory.

    Args:
        file_path (str | pathlib.Path): Path to the existing file to rename.
        name (str): New filename (not a full path). The file will be moved to
            the same parent directory under this name.
        replace_existing_file (bool): If True and a file with the target name
            already exists it will be removed before renaming.

    Returns:
        bool: True on success, False on failure.
    """
    file_path = file_path if isinstance(file_path, Path) else Path(file_path)
    new_path = file_path.parent / name
    log.info(f"Attempting to rename: {file_path} -> {new_path}")
    if not file_path.exists():
        log.error(f"File: {file_path} does not exist.")
        return False
    if file_path.is_dir():
        log.error(f"Path: {file_path} is a directory and cannot be renamed as a file.")
        return False
    if new_path.exists():
        if not replace_existing_file:
            log.error(f"Target file already exists: {new_path}")
            return False
        log.info(f"File with the same name already exists: {new_path}, file will be replaced")
        if not remove_file(new_path):
            log.error(f"Cannot rename file: {new_path} due to error during deletion of the existing file with the same name.")
            return False
    try:
        file_path.rename(new_path)
    except Exception as e:
        log.error(f"Failed to rename file: {file_path} to {new_path} due to: {e}")
        return False
    log.success(f"Successfully renamed file: {file_path} to {new_path}")
    return True

def read_file(file_path,strip: bool = False,enumerate: bool = False, debug: bool = False):
    file_path = file_path if isinstance(file_path, Path) else Path(file_path)
    if not check_file_exists(file_path):
        log.error(f"File not found or is directory. {file_path}")
        return None
    
    with open(file=file_path,mode="+r") as file:
        if enumerate:
            file_content = {}    
            i = 0
            for line in file:
                if strip:
                    line = line.strip()
                if debug:
                    log.debug(f"index={i},line={line}")
                file_content[i]=line
                i=i+1
        else:
            file_content=[]
            for line in file:
                if strip: line.strip 
                if debug: log.debug(f"Read line:'{line}'")
                file_content.append(line)
    return file_content



def read_file_yaml(file_path):
    file_path = file_path if isinstance(file_path, Path) else Path(file_path)
    if not check_file_exists(file_path):
            log.error("File not found")
            return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
    # YAML syntax / parsing error
        raise ValueError(f"Invalid YAML in '{file_path}': {e}") from e
    except OSError as e:
    # Problems opening/reading the file
        raise OSError(f"Error reading '{file_path}': {e}") from e

def write_to_file(file_path:str|Path,data:list|dict,debug:bool=False):
    file_path = file_path if isinstance(file_path, Path) else Path(file_path)
    if not check_file_exists(file_path=file_path):
        log.error(f"Cannot Write to unaccesable file. {file_path}") 
        raise FileNotFoundError()
    write_data=[]
    if type(data) == dict:
        for key in data:
            write_data.append(data[key]+"\n")
        if debug: log.debug(f"Data to write:{write_data}")
    elif type(data) == list:
        for line in data: 
            write_data.append(line+"\n")
        if debug: log.debug(f"Data to write:{write_data}")
    else:
        log.error(f"Expected 'data' as either 'list' or 'dict' but received {type(data)}")
    try:
        with open(file=file_path,mode="w+") as file:
            file.writelines(write_data)
    except OSError as e:
        log.error(f"Writing to {file_path} failed due to:", e)
        
if __name__ == "__main__":
    print(list_subdirectories(Path("a")).__doc__)
    
    

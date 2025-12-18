import logging
import types
from pathlib import *

import colorama as color

import Utils.Logger as Logger
import ioHelper.fileOperations as fOps

if __name__ == "__main__":

    log1 = Logger.LoggerClass(logger_name="TestLogger",logger_level = 1,log_color = True)
    path = fOps.convert_string_to_path("Test/Test_1/Test_1_file.txt")
    subdirMap=fOps.list_subdirectories(path,True)
    for x in subdirMap:
        files=fOps.list_files(x)


    fOps.create_file(path)
    fOps.check_file_exists(path)

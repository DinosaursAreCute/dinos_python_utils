import logging
import types
from pathlib import *

import colorama as color

import Utils.Logger as Logger
import ioHelper.fileOperations as fOps

if __name__ == "__main__":

    log1 = Logger.LoggerClass(logger_name="TestLogger",logger_level = 1,log_color = True)
    path = fOps.convert_string_to_path(".")
    subdirMap=fOps.list_subdirectories(path,True)
    for x in subdirMap:
        files=fOps.list_files(x)
        for f in files:
            f=f.parts[-1]
            print("                                                     -",f)
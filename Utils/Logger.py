# ======================== Imports ========================
from datetime import datetime
from typing import Optional
failed_imports=[]
try:
    import colorama as color #Try catch due to colors being an optional feature that should not be enforced
except:
    failed_imports.append("colorama")


# ======================== Independent Functions ========================

def logger_logger(msg: str, logger_name: str):
    print(f"[LOGGER_DEBUG][{logger_name}]; {msg}")


# ======================== Logger Class ========================
class LoggerClass:

        def __init__(self, logger_level: int,logger_name: str = 'UNNAMED_LOGGER', log_date: bool = False, log_time: bool = True, log_name: bool = True, log_level: bool = True,log_color: bool = True,logger_debug: bool = False):
            if logger_debug:
                self.logger_debug = True
                logger_logger(f"Debug Mode for Logger: {logger_name} set to: True", logger_name)
                logger_logger(f"args: logger_name={logger_name}, logger_level={logger_level}, log_date={log_date}, log_time={log_time}, log_name={log_name}, log_level={log_level},log_color={log_color} logger_debug={logger_debug}", logger_name)

            if logger_level-5 > 0:
                print(f"[Logger_ERROR]; Invalid logger_level {logger_level} for logger {logger_name} setting using default 2")
                logger_level = 0

            prevent_color = False
            if "colorama" in failed_imports and log_color:
                logger_logger("Color is enabled", logger_name)
                prevent_color=True
                log_color = False

            self.logger_name = logger_name
            self.logger_level = logger_level
            self.log_date = log_date
            self.log_time = log_time
            self.log_name = log_name
            self.log_level = log_level
            self.log_color = log_color
            self.prevent_color = prevent_color
            self.logger_debug = logger_debug

        # ======================== Main Logic ========================

        def logger_log(self,msg):
            if self.logger_debug:
                logger_logger(msg, logger_name = self.logger_name)
        #---------------------------------------------------------------------------------------------------------------

        def construct_prefix(self,message_log_level: int = 1, log_date: Optional[bool] = None, log_time: Optional[bool] = None,
                             log_name: Optional[bool] = None, log_level: Optional[bool] = None,log_color: Optional[bool] = None) -> str:
            if log_date is None:
                log_date = self.log_date
            if log_time is None:
                log_time = self.log_time
            if log_name is None:
                log_name = self.log_name
            if log_level is None:
                log_level = self.log_level
            if log_color is None:
                log_color = self.log_color
            if message_log_level -5 > 0:
                logger_logger(f"Encountered invalid message_log_level: {message_log_level} during prefix construction", self.logger_name)

            levels = [" DEBUG "," VALUE ","  INFO ","SUCCESS","WARNING"," ERROR "]
            if not self.prevent_color and log_color:
                levels = [color.Fore.LIGHTWHITE_EX+' DEBUG '+color.Fore.RESET,
                          color.Fore.MAGENTA+' VALUE '+color.Fore.RESET,
                          color.Fore.CYAN+' INFO '+color.Fore.RESET,
                          color.Fore.LIGHTGREEN_EX+'SUCCESS'+color.Fore.RESET,
                          color.Fore.YELLOW+'WARNING'+color.Fore.RESET,
                          color.Back.RED+color.Style.BRIGHT+color.Fore.BLACK+' ERROR '+color.Style.RESET_ALL]

            time = datetime.now()
            parts = []

            if log_date and log_time:
                parts.append(f"[{time.strftime('%d-%m-%Y')} {time.strftime('%H:%M:%S')}.{time.microsecond // 1000:03d}]")
            elif log_date:
                parts.append(f"[{time.strftime('%d-%m-%Y')}]")
            elif log_time:
                parts.append(f"[{time.strftime('%H:%M:%S')}.{time.microsecond // 1000:03d}]")
            if log_name:
                parts.append(f"[{self.logger_name}]")
            if log_level:
                parts.append(f"[{levels[message_log_level]}]")
            return f"{" ".join(parts)}; "
        #---------------------------------------------------------------------------------------------------------------

        def log_message(self,msg: str,log_level: int):
            # int log_level: 0=Debug 1=Value 2=Info 3=Success 4=Warning 5=Error
            if log_level < self.logger_level:
                logger_logger(f"log level {log_level} is lower than set logger level {self.logger_level}. Message will be discarded", self.logger_name)
                return
            log_message = f"{self.construct_prefix(log_level)}{msg}"
            print(log_message)
        # ---------------------------------------------------------------------------------------------------------------


        def debug(self,msg: str):
            self.log_message(msg, 0)
        # ----

        def value(self,msg: str):
            self.log_message(msg, 1)
        # ---

        def info(self,msg: str):
            self.log_message(msg, 2)
        # ---

        def success(self,msg: str):
            self.log_message(msg,3)
        # ---

        def warning(self,msg):
            self.log_message(msg,4)
       # ---

        def error(self,msg):
            self.log_message(msg,5)




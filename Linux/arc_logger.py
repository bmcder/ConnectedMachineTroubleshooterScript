from enum import Enum
from os.path import exists
from datetime import datetime

class ArcLoggerLevel(Enum):
    Debug = 1
    Info = 2
    Warn = 3
    Error = 4
    Fatal = 5

class ArcLogger:
    log_path: str = None

    colors = {
        ArcLoggerLevel.Debug: "\u001b[35m",
        ArcLoggerLevel.Info: "\u001b[37m",
        ArcLoggerLevel.Warn: "\u001b[33m",
        ArcLoggerLevel.Error: "\u001b[31m",
        ArcLoggerLevel.Fatal: "\u001b[31;1m"

    }

    def __init__(self,path: str):
        if not exists(path):
            try:
                with open(path,'w'): pass
            except Exception as e:
                raise e
        
        self.log_path = path

    def __getTime (self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Maybe put the parse string to enum

    # def __parseSource(self,name: str) -> str:
    #     threshold = 20
    #     if len(name) > threshold:
    #         raise "Error formatting Logger source: name is greater than {}".format(threshold)

    #     delta = 20 - len(name)

    #     for i in range(delta):
    #         name += " "
        
    #     return name

    def writeLine(self,log_level: ArcLoggerLevel, source: str, message: str) -> None:
        try:
            self.writeLineToLog(log_level,source,message)
            self.writeLineToConsole(log_level,message,True)
        except Exception as e:
            raise e


    
    def writeLineToLog(self,log_level: ArcLoggerLevel, source: str, message: str) -> None:
        timestamp = self.__getTime()
        source_string =source # self.__parseSource(source)

        try:
            with open(self.log_path,'a') as f:
                f.write("{} {:<5} {:<20} {}\n".format(timestamp,log_level.name,source_string,message))
        except Exception as e:
            print("Failed to write entry to file: {}".format(e))
            raise e

    def writeTableToLog(self,log_level: ArcLoggerLevel, source: str,table, predictate) -> None:
        try:
            for row in table:
                parsed_row = predictate(row)
                self.writeLineToLog(log_level,source,parsed_row)

        except Exception as e:
            raise "Failed to parse table and write to log: {}".format(e)

    def writeLineToConsole(self,log_level: ArcLoggerLevel,message: str, use_new_line: bool) -> None:
        fg_color = self.colors[log_level]

        try:
            if use_new_line:
                print("{}{}\u001b[0m".format(fg_color,message))
            else:
                print("{}{}\u001b[0m".format(fg_color,message),end="")
        except Exception as e:
            raise "Failed to write line to console: {}".format(e)

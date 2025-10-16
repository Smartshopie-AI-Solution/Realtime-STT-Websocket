import sys
import traceback

class ProjectException(Exception):
    def __init__(self, error_message, error_details: sys):
        self.error_message = error_message
        self.error_details = error_details
        _, _, exec_tb = error_details.exc_info()
        
        if exec_tb:
            self.lineno = exec_tb.tb_lineno
            self.filename = exec_tb.tb_frame.f_code.co_filename
        else:
            self.lineno = "Unknown"
            self.filename = "Unknown"

    def __str__(self):
        error_msg = f'\nError occurred in file: {self.filename}, \nline: {self.lineno}, \nError Msg: {self.error_message}'
        return error_msg

    def log_error(self):
        """Log the error without exiting the program"""
        print(f"ProjectException: {self}")
        traceback.print_exc()
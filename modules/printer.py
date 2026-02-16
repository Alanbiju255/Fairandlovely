import os
import win32api
import win32print

def print_pdf(file_path):
    printer_name = win32print.GetDefaultPrinter()
    win32api.ShellExecute(
        0,
        "print",
        file_path,
        None,
        ".",
        0
    )

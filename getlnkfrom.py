import pylnk3
import os

def get_lnk_file(path):
    lnk = pylnk3.parse(path)
    return lnk.path or '' ,lnk.arguments

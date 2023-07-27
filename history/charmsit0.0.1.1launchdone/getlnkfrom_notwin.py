import os
def get_lnk_file(path):
    target = os.readlink(path)
    return target

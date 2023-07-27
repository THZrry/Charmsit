"""
Empty.
use in systems not windows.
"""
class BITMAPINFOHEADER():
    " empty. "

class BITMAPINFO(Structure):
    " empty. "

def rgb(raw,width=32,height=32):
    # From mss.screenshot
    rgb = bytearray(height * width * 3)
    rgb[0::3] = raw[2::4]
    rgb[1::3] = raw[1::4]
    rgb[2::3] = raw[0::4]
    return bytes(rgb)

def get_raw_data(path,index=0,size=32):
    " empty. "
    return bytearray(b'')

def get_rgb_data(path):
    return rgb(get_raw_data(path))

if __name__ == "__main__":
    0


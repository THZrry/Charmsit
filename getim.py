import zipfile
import json
from PIL import Image, ImageTk

#zarchive = zipfile.ZipFile("resource.zip")
cache = {}

def get(path):
    tkim = cache.get(path)
    if tkim:
        return tkim
    try:
        with zarchive.open(path) as file:
            img = Image.open(file)
            tkim = ImageTk.PhotoImage(img)
            cache[path] = tkim
    except:
        tkim = None
    return tkim

def changeres(path):
    global zarchive, colordic
    zarchive = zipfile.ZipFile(path)
    cache.clear()
    with zarchive.open("colors.json",'r') as f:
        try:
            colordic = json.loads(f.read().decode())
        except:
            colordic = json.loads(f.read())

changeres("resource.zip")

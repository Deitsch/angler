import urllib, urllib.request, re, os
from anglerEnums import AnglerConfig

def __extractPath(path: str):
    return path.split(":")[1].strip("\"")

def getSwaggerDefinitionsFrom(url: str):
    html = urllib.request.urlopen(url).read()
    paths = re.findall(r'"url":"[a-zA-Z\/0-9]*"', html.decode("utf-8"))
    sanitizedPaths = map(__extractPath, paths)
    return list(sanitizedPaths) 

def readFromJson(json, key: AnglerConfig, defaultValue: str = None):
    try:
        return json[key.value]
    except:
        print(f"{key.value} was not defined in config")
        if defaultValue is None:
            exit()
        else:
            print(f"{key.value} using defaultValue: {defaultValue}")
            return defaultValue


def createFolder(createPath: str, folder: str):
    newFolder=f"{createPath}/{folder}"
    if not os.path.exists(newFolder):
        if (folder == ""):
            print(f"root directory created")
        else:
            print(f"{folder} directory created")
        os.mkdir(newFolder)
    else: 
        if (folder == ""):
            print(f"    root directory found")
        else:
            print(f"    {folder} directory found")
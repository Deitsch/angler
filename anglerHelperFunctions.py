import urllib, urllib.request, re, os
from anglerEnums import AnglerConfig

def __extractPath(path: str):
    return path.split(":")[1].strip("\"")

def getSwaggerDefinitionsFrom(url: str):
    try:
        html = urllib.request.urlopen(url).read()
    except:
        print(f"SwaggerUI not found. Is this the correct url? {url}")
        return []
    paths = re.findall(r'"url":"[a-zA-Z\/0-9]*"', html.decode("utf-8"))
    sanitizedPaths = map(__extractPath, paths)
    return list(sanitizedPaths) 

def readConfig(json, key: AnglerConfig, defaultValue: str = None):
    try:
        return json[key.value]
    except:
        print(f"{key.value} was not defined in config")
        if defaultValue is None:
            exit()
        else:
            print(f"{key.value} using defaultValue: {defaultValue}")
            return defaultValue
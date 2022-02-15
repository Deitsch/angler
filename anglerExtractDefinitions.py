#!/usr/bin/env python3
import urllib, urllib.request, re

def extractPath(path: str):
    return path.split(":")[1].strip("\"")

def getSwaggerDefinitions(url: str):
    html = urllib.request.urlopen(url).read()
    paths = re.findall(r'"url":"[a-zA-Z\/0-9]*"', html.decode("utf-8"))
    sanitizedPaths = map(extractPath, paths)
    return list(sanitizedPaths) 

import json, urllib.request, re, os

from packaging import version

class Angler:
    def __init__(self, gatewayHost: str):
        self.gatewayHost = gatewayHost
    
    def mergeDefinitions(self, swaggerDefinitions: list[str]) -> str:
        openapi = ""
        info = ""
        summary = []
        paths = {}
        schemas = {}
        for definition in swaggerDefinitions:
            definitionURL = self.gatewayHost + definition
            summary.append(definition)
            f = urllib.request.urlopen(definitionURL)
            data = json.load(f)

            openapi = data["openapi"]
            info = data["info"]
            paths.update(data["paths"])
            schemas.update(data["components"]["schemas"])
        info["title"] = "service"
        info["description"] = "Created with Angler"

        if version.parse(openapi) > version.parse("3.0.1"):
            info["summary"] = f"This is a merged definition file of following definition files {summary}"
        
        newDef = {
            "openapi": openapi,
            "info": info,
            "paths": paths,
            "components": {
                "schemas": schemas
            }
        }
        return json.dumps(newDef)

    def __extractPath(self, path: str):
        return path.split(":")[1].strip("\"")
    
    def getSwaggerDefinitionsFrom(self, url: str) -> list[str]:
        try:
            html = urllib.request.urlopen(url).read()
        except:
            print(f"SwaggerUI not found. Is this the correct url? {url}")
            return []
        paths = re.findall(r'"url":"[a-zA-Z\/0-9]*"', html.decode("utf-8"))
        sanitizedPaths = map(self.__extractPath, paths)
        return list(sanitizedPaths) 
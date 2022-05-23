import os, shutil, json, urllib
from anglerOpenAPIfix import removeDeleteBody

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
        info["summary"] = f"This is a merged definition file of following definition files {summary}"
        
        newDef = {
            "openapi": openapi,
            "info": info,
            "paths": paths,
            "components": {
                "schemas": schemas
            }
        }
        print("Merging done!")
        return json.dumps(newDef) 
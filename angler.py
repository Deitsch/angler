import json, urllib.request, re, ssl
from packaging import version

class Angler:
    def __init__(self, gatewayHost: str):
        self.gatewayHost = gatewayHost
    
    def mergeDefinitions(self, swaggerDefinitions: list[str], allowUnsafe: bool) -> str:
        openapi = ""
        info = ""
        summary = []
        paths = {}
        schemas = {}
        securitySchemes = {}
        for definition in swaggerDefinitions:
            definitionURL = self.gatewayHost + definition
            summary.append(definition)

            if allowUnsafe:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            else: 
                ctx = None
            f = urllib.request.urlopen(definitionURL, context=ctx)
            data = json.load(f)

            openapi = data["openapi"]
            info = data["info"]
            paths.update(data["paths"])
            components = data["components"]

            if (components == {}):
                print(f"No components found for {definition}, skipping ...")
                continue
            
            try: 
                compSchemas = components["schemas"]
                schemas.update(compSchemas)
            except:
                print(f"No schemas found for {definition}, skipping ...")

            try: 
                compSecuritySchemes = components["securitySchemes"]
                if (compSecuritySchemes != {}):
                    if (securitySchemes == {}):
                        securitySchemes.update(compSecuritySchemes)
                    elif (securitySchemes != compSecuritySchemes):
                        raise ValueError('The OpenAPI Definitions contain missmatching security schemas.')
            except:
                print(f"No securitySchemes found for {definition}, skipping ...")
                

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
    
    def getSwaggerDefinitionsFrom(self, url: str, allowUnsafe: bool) -> list[str]:
        try:
            if allowUnsafe:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            else: 
                ctx = None
            html = urllib.request.urlopen(url, context=ctx).read()
        except BaseException as err:
            print(err)
            print(f"SwaggerUI not found or inaccessible. \nIs this the correct url? {url}")
            exit()
        paths = re.findall(r'"url":"[a-zA-Z\/0-9_]*"', html.decode("utf-8"))
        sanitizedPaths = map(self.__extractPath, paths)
        return list(sanitizedPaths) 
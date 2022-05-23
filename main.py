#!/usr/bin/env python3
import json, os, argparse, os.path
from os import path
from urllib.parse import urlparse
from anglerOpenAPIfix import removeDeleteBody
from angler import Angler
from anglerEnums import AnglerConfig, AnglerMode

def readConfig(json, key: AnglerConfig, defaultValue: str = None) -> str:
    try:
        return json[key.value]
    except:
        print(f"{key.value} was not defined in config")
        if defaultValue is None:
            exit()
        else:
            print(f"{key.value} using defaultValue: {defaultValue}")
            return defaultValue

def main():
    parser = argparse.ArgumentParser(description='A swagger gen for microservices')
    parser.add_argument("-c", "--config", help="Path to the generator config", default="angler.json")
    parser.add_argument("-v", "--version", help="Shows current version", action='store_true')
    parser.add_argument("-vv", "--verbose", help="Shows more details in log", action='store_false')

    args = parser.parse_args()
    isVerbose=args.verbose

    if args.version:
        dirPath = os.path.dirname(os.path.realpath(__file__))
        currentVersion = open(f'{dirPath}/version').read()
        print(f"Angler {currentVersion}")
        exit()

    try:
        config = open(f'{args.config}')
        configJson = json.load(config)
    except:
        print("No config found")
        exit()

    ### read gateway address
    # get swaggerUI path (e.g. http://localhost:8002/swagger)
    swaggerUIPath = readConfig(configJson, AnglerConfig.GATEWAY)
    # get rid of any path (e.g. http://localhost:8002)
    gatewayHost = swaggerUIPath.strip(urlparse(swaggerUIPath).path)

    ### read mode
    mode = readConfig(configJson, AnglerConfig.MODE, AnglerMode.AUTO.value)
    try:
        mode = AnglerMode(configJson[AnglerConfig.MODE.value])
    except:
        allModes = ", ".join([e.value for e in AnglerMode])
        print(f"Invalid mode set for angler.\nAvailable modes: {allModes}")
        exit()

    if mode == AnglerMode.MANUAL and AnglerConfig.DEFINITIONS.value not in configJson:
        print(f"{AnglerMode.MANUAL.value} requires {AnglerConfig.DEFINITIONS.value} to be defined in the config")

    angler = Angler(gatewayHost)

    if mode == AnglerMode.MANUAL:
        swaggerDefinitions = configJson['definitions']
    else:
        swaggerDefinitions = angler.getSwaggerDefinitionsFrom(swaggerUIPath)

    if len(swaggerDefinitions) == 0:
        print("No swagger definitions found")
        exit()
    for swaggerDef in swaggerDefinitions:
        print(f"Found {swaggerDef}")

    ### All Data collected, run actual merge & generation
    mergedDefinition = angler.mergeDefinitions(swaggerDefinitions)
    print("Merging done!")

    ### generationFolder
    generationFolder = readConfig(configJson, AnglerConfig.GENERATIONFOLDER, "./openapi")
    createPath = os.path.abspath(os.getcwd()) + "/" + generationFolder

    if not path.isdir(createPath):
        os.mkdir(createPath)

    filePath = f"{createPath}/definition.json"
    file = open(filePath, "w")
    file.write(mergedDefinition)
    file.close()
    print(f"Created merged definition file {filePath}\n")

    generate = readConfig(configJson, AnglerConfig.GENERATE, "")

    ### read additional swaggergern properties
    additionalProperties = readConfig(configJson, AnglerConfig.OPENAPICLIADD, "")
    swaggerGenCommand = f"openapi-generator-cli generate -g {generate} " + f"{additionalProperties}" + " -o " + createPath + " -i " + filePath

    # >/dev/null 2>&1 to hide output
    if isVerbose:
        print(f"swagger command used: {swaggerGenCommand}")
        swaggerGenCommand+=" >/dev/null 2>&1"
    # add docker mode here
    os.system(swaggerGenCommand)
    print("\nGenerating done!")

    # this is needed cause OpenAPI has a bug
    # removeDeleteBody(f"{createPath}/api", isVerbose)

if __name__ == '__main__':
    main()
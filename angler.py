#!/usr/bin/env python3
import json, os, shutil, argparse

parser = argparse.ArgumentParser(description='A swagger gen for microservices')

parser.add_argument("-c", "--config", help="Path to the generator config", default="angler.json")
parser.add_argument("-v", "--verbose", help="Shows more details in log", action='store_true')

args = parser.parse_args()

isVerbose=args.verbose

# todo: add this file to path, write readme how to and installer to do so -> brew??
dirPath = os.path.dirname(os.path.realpath(__file__))
swaggerGenBase="openapi-generator-cli generate -g typescript-angular "
try:
    config = open(f'./{args.config}')
    configJson = json.load(config)
except:
    print("No config found")
    exit()

try:
    gatewaySwaggerAdress = configJson['swaggerBase']
except:
    print("Swaggerbase was not defined in config")
    exit()

try:
    swaggerPaths = configJson['swaggerPaths']
except:
    print("swaggerPaths were not defined in config")
    exit()

try:
    createPath = dirPath + "/" + configJson['generationFolder']
except:
    print("createPath was not defined in config")
    exit()

try:
    additionalProperties = configJson['additional-properties']
    swaggerGenBase += f"--additional-properties  \"{additionalProperties}\" "
except:
    print("No additional properties flag set")

copyFiles=[".gitignore", "configuration.ts", "api.module.ts", "encoder.ts", "index.ts", "variables.ts"]
mergeFolders=["model", "api"]

def createFolder(folder):
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

print("creating folder structure...")
createFolder("")
createFolder("model")
createFolder("api")
os.chdir(createPath)

def removeIfExist(path):
    if os.path.exists(path):
        os.remove(path)

print("\nremoving old files...")
removeIfExist("./api/api.ts")
removeIfExist("./model/models.ts")


# export const APIS = [NewsService, WeatherForecastService];
def mergeApiTs(sourceFile, destinationFile):
    # append contents if it exists
    if os.path.exists(destinationFile):
        sfile = open(sourceFile, "r")
        dFile = open(destinationFile, "r")
        sContent = sfile.readlines()
        dContent = dFile.readlines()

        # sourcfile: disect last line (export const APIS = ...) line
        sourceAPISLine = sContent[-1].split("=")
        # sourcfile: creating array of api services from said line
        sourceAPISClasses = sourceAPISLine[-1].strip().strip("[]; ")

        # destfile: disect last line (export const APIS = ...) line
        destAPISLine = dContent[-1].split("=")
        # destfile: creating array of api services from said line
        destAPISClasses = destAPISLine[-1].strip().strip("[]; ")

        #creating merged const APIS from source and dest
        newAPIConst = sourceAPISLine[0] + "= [" + sourceAPISClasses + ", " + destAPISClasses +  "]\n"
        # print(newAPIConst)

        # merge content of source and dest w/o const APIS
        newContent = "".join(dContent[:-1]).join(sContent[:-1])
        # add merged const APIS
        newContent+=newAPIConst

        # overwrite file with new content
        finalFile = open(destinationFile, "w")
        finalFile.write(newContent)
    # copy file in none exists
    else:
        shutil.copy(sourceFile, destinationFile)

def mergeModelTs(sourceFile, destinationFile):
    # append contents if it exists
    if os.path.exists(sourceFile):
        sfile = open(sourceFile, "r")
        dFile = open(destinationFile, "a")
        dFile.write(sfile.read())
    # copy file in none exists
    else:
        shutil.copy(sourceFile, destinationFile)

def copyFolder(src, dest):
    # print(f'copying from {src} to {dest}')
    sourcePath = os.path.abspath(os.getcwd()) + src
    destinationPath = os.path.abspath(os.getcwd()) + dest
    for fileName in os.listdir(sourcePath):
        sourceFile = sourcePath + fileName
        destinationFile = destinationPath + fileName
        
        if fileName == "api.ts":
            mergeApiTs(sourceFile, destinationFile)
        elif fileName == "models.ts":
            mergeModelTs(sourceFile, destinationFile)
        elif os.path.isfile(sourceFile):
            shutil.copy(sourceFile, destinationFile)
            # print('copied', fileName)

print("generating from openapi...")
# create services and models
for path in swaggerPaths:
    print(f"    generating {path}")
    swaggerGen=f"{swaggerGenBase} -o ./temp/{path} -i {gatewaySwaggerAdress}/{path}"
    if not isVerbose:
        swaggerGen+=" >/dev/null 2>&1"
    os.system(swaggerGen) # >/dev/null 2>&1 to hide output
    for folder in mergeFolders:
        copyFolder(f"/temp/{path}/{folder}/", f"/{folder}/")

# copying files that are the same for all generations from first generation
firstSwaggerGenPath=swaggerPaths[0]
for file in copyFiles:
    shutil.copyfile(f"./temp/{firstSwaggerGenPath}/{file}", f"./{file}")

print("cleaning up tmp data...")
shutil.rmtree("./temp")

print("Done!")
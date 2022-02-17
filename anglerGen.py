import os, shutil

class AnglerGen:
    def __init__(self, gatewayHost: str, createPath: str, swaggerGenBase: str, swaggerDefinitions: list[str], isVerbose: bool):
    
        self.gatewayHost = gatewayHost       
        self.createPath = createPath
        self.swaggerGenBase = swaggerGenBase
        self.swaggerDefinitions = swaggerDefinitions
        self.isVerbose = isVerbose
        self.copyFiles=[".gitignore", "configuration.ts", "api.module.ts", "encoder.ts", "index.ts", "variables.ts"]
        self.mergeFolders=["model", "api"]
    
    def generateCode(self):
        # export const APIS = [NewsService, WeatherForecastService];
        print("generating from openapi...")
        # create services and models
        for path in self.swaggerDefinitions:
            print(f"    generating {path}")
            swaggerGen=f"{self.swaggerGenBase} -o ./temp{path} -i {self.gatewayHost}{path}"
            if not self.isVerbose:
                swaggerGen+=" >/dev/null 2>&1"
            else:
                print(f"{swaggerGen}")

            os.system(swaggerGen) # >/dev/null 2>&1 to hide output
            for folder in self.mergeFolders:
                self.__copyFolder(f"/temp{path}/{folder}/", f"/{folder}/")

        # copying files that are the same for all generations from first generation
        firstSwaggerGenPath=self.swaggerDefinitions[0]
        for file in self.copyFiles:
            shutil.copyfile(f"./temp{firstSwaggerGenPath}/{file}", f"./{file}")

        print("cleaning up tmp data...")
        shutil.rmtree("./temp")
        print("Done!")

    def __mergeApiTs(self, sourceFile: str, destinationFile: str):
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

    def __mergeModelTs(self, sourceFile: str, destinationFile: str):
        # append contents if it exists
        if os.path.exists(sourceFile):
            sfile = open(sourceFile, "r")
            dFile = open(destinationFile, "a")
            dFile.write(sfile.read())
        # copy file in none exists
        else:
            shutil.copy(sourceFile, destinationFile)

    def __copyFolder(self, src: str, dest: str):
        # print(f'copying from {src} to {dest}')
        sourcePath = os.path.abspath(os.getcwd()) + src
        destinationPath = os.path.abspath(os.getcwd()) + dest
        for fileName in os.listdir(sourcePath):
            sourceFile = sourcePath + fileName
            destinationFile = destinationPath + fileName
            
            if fileName == "api.ts":
                self.__mergeApiTs(sourceFile, destinationFile)
            elif fileName == "models.ts":
                self.__mergeModelTs(sourceFile, destinationFile)
            elif os.path.isfile(sourceFile):
                shutil.copy(sourceFile, destinationFile)
                # print('copied', fileName)

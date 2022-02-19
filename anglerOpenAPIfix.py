import os

def removeDeleteBody(dir: str, isVerbose: bool = False):
    for fileName in os.listdir(dir):
        # skip export file
        if fileName == "api.ts":
            continue
        sourceFile = f"{dir}/{fileName}"
        lines = open(sourceFile, "r").readlines()
        count = 0
        deleteBodyLines=[]
        # Strips the newline character
        for line in lines:
            count += 1
            # find delete call, next line is delete body
            if line.find('this.httpClient.delete<any>') > 0:
                deleteBodyLines.append(count+1)


        count = 0
        with open(sourceFile, "w") as f:
            for line in lines:
                count += 1
                if count in deleteBodyLines and line.strip() == "null,":
                    if isVerbose:
                        print(f"removing delete body: line {count} in {fileName}")
                else: 
                    f.write(line)
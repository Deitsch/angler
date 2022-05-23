from enum import Enum

class AnglerConfig(Enum):
    GENERATIONFOLDER = "generationFolder"
    GATEWAY = "swaggerUI"
    MODE = "mode" # detect (default) / manual ()
    DEFINITIONS = "definitions" #only read if mode = manual
    OPENAPICLIADD = "openapi-cli-add" # additional props for openapi gen
    GENERATE = "generate"

class AnglerMode(Enum):
    AUTO = "auto"
    MANUAL = "manual"
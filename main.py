from analyze import *
from simulate import *
from generate import *

import configparser
import sys
import time

def main():
    config = loadConfig()
    setup(config)
    profiles = generateProfiles(config)
    topDps = runSims(profiles["valid"], config["Sim"]["maxthreads"])

    generateHtmlProfiles([x[1] for x in topDps])

    topDpsProfiles = [x[1] for x in topDps]
    print("Top %s DPS results available at:" % len(topDps))
    for i in range(len(topDps)):
        print("%s: output\\html\\%s.html (%s)" % (i+1, topDps[i][1], topDps[i][0]))
    # analyzeSims(profiles)

def setup(config):
    if not os.path.exists(config["player"]["profilename"]):
        os.makedirs(config["player"]["profilename"])
    os.chdir(config["player"]["profilename"])
    for dir in ["output", "output\\json", "output\\html", "profiles"]:
        if not os.path.exists(dir):
            os.makedirs(dir)

def loadConfig():
    config = configparser.ConfigParser()

    if (len(sys.argv) > 1 and os.path.exists(sys.argv[1])):
        configFile = sys.argv[1]
    else:
        print("Enter name of exported settings file:")
        configFile = input()

    if os.path.exists(configFile):
        config.read(configFile)
    else:
        print("ERROR: Config file (%s) does not exist." % configFile)
        sys.exit(99)

    if config.has_option("Sim", "maxthreads"):
        try:
            int(config["Sim"]["maxthreads"])
        except Exception:
            config["Sim"]["maxthreads"] = str(max(multiprocessing.cpu_count()-2, 1))
            print("WARN: maxthreads option not a valid number. Defaulting maxthreads to %s" % config["Sim"]["maxthreads"])
    else:
        config["Sim"] = {}
        config["Sim"]["maxthreads"] = str(max(multiprocessing.cpu_count()-2, 1))
        print("INFO: maxthreads option not set. Defaulting maxthreads to %s" % config["Sim"]["maxthreads"])
    profile = config["Profile"]
    player = {}
    player["profilename"]=profile["profilename"]
    player["class"]=profile["class"]
    player["race"]=profile["race"]
    player["level"]=profile["level"]
    player["spec"]=profile["spec"]
    player["role"]=profile["role"]
    player["position"]=profile["position"]
    player["talents"]=profile["talents"]
    player["artifact"]=profile["artifact"]
    player["other"]=profile["other"]

    config["player"] = player

    return config

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- Full execution in %s seconds ---" % (time.time() - start_time))

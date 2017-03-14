from analyze import *
from simulate import *
from generate import *

import configparser
import sys
import time

def main():
    config = loadConfig()
    setup(config)
    generatedProfiles = generateProfiles(config)
    for fightStyle in generatedProfiles:
        print("---Simming profiles for fight style %s---" % fightStyle)
        topDps = runSims(generatedProfiles[fightStyle]["valid"], config["Sim"]["maxthreads"])

        topDpsProfiles = []
        for dpsTuple in topDps:
            topDpsProfiles.append((dpsTuple[0], dpsTuple[1]))

        generateHtmlProfiles(topDpsProfiles)

        topDpsProfiles = [x[1] for x in topDps]
        print("Top %s DPS for %s results available at:" % (len(topDps), fightStyle))
        for i in range(len(topDps)):
            print("%s: output\\html\\%s_%s.html (%s)" % (i+1, topDps[i][0], topDps[i][1], topDps[i][2]))
        print("-------")
        print()

def setup(config):
    if not os.path.exists(config["Profile"]["profilename"]):
        os.makedirs(config["Profile"]["profilename"])
    os.chdir(config["Profile"]["profilename"])
    for dir in ["output", "output\\json", "output\\html", "profiles"]:
        if not os.path.exists(dir):
            os.makedirs(dir)

def loadConfig():
    config = configparser.ConfigParser()

    if (len(sys.argv) > 1 and os.path.isfile(sys.argv[1])):
        configFile = sys.argv[1]
    else:
        print("Enter name of exported settings file:")
        configFile = input()

    if os.path.isfile(configFile):
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

    if not config.has_option("Profile", "fightstyle"):
        config["Profile"]["fightstyle"] = "Patchwerk"
        print("INFO: Defaulting fightstyle to Patchwerk.")

    return config

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- Full execution in %s seconds ---" % (time.time() - start_time))

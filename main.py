from analyze import *
from simulate import *
from generate import *

import configparser
import sys
import time

def main():
    config = loadConfig()
    setup(config)
    generatedGear = generateGear(config)
    for fightStyle in generatedGear:
        print("---Simming profiles for fight style %s---" % fightStyle)

        simInputs = []
        for fightStyleGear in generatedGear[fightStyle]["valid"]:
            simInputs.append((fightStyle, fightStyleGear, config["Profile"]))

        topSims = runSims(simInputs, config["Sim"]["maxthreads"])
        print(topSims)
        htmlOutputs = generateHtmlOutput(topSims)

        # topSimDps = [x[1] for x in topSims]
        print("Top %s DPS for %s results available at:" % (len(htmlOutputs), fightStyle))
        for i in range(len(htmlOutputs)):
            print("%s: %s (%s) Gear: %s" % (i+1, htmlOutputs[i]["output"], htmlOutputs[i]["dps"], htmlOutputs[i]["equippedGear"]))
        print("-------")
        print()

def setup(config):
    if not os.path.exists(config["Profile"]["profilename"]):
        os.makedirs(config["Profile"]["profilename"])
    # os.chdir(config["Profile"]["profilename"])
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

    if not config.has_option("Sim", "fightstyle"):
        config["Sim"]["fightstyle"] = "Patchwerk"
        print("INFO: Defaulting fightstyle to Patchwerk.")

    return dict(config)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- Full execution in %s seconds ---" % (time.time() - start_time))

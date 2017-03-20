from generate import *
from simulate import *
from analyze import *

import configparser
import sys
import time

def main():
    config = loadConfig()
    print("Performing gear comparisons for %s on Fight Styles: %s" % (config["Profile"]["profilename"], config["Sim"]["fightstyle"]))
    print("Using %s threads" % config["Sim"]["maxthreads"])
    print()

    generatedGear = generateGear(config["Gear"])

    metric = config["Sim"]["metric"]
    htmlOutputs = {}

    for fightStyle in config["Sim"]["fightstyle"].split(","):
        print("---Simming profiles for fight style %s---" % fightStyle)
        simInputs = []

        topSims = runSims(fightStyle, generatedGear["valid"], config["Profile"], config["Sim"]["maxthreads"], metric)
        htmlOutputs[fightStyle] = generateHtmlOutput(topSims, metric)

    for fightStyle, fightHtmlOutputs in htmlOutputs.items():
        print("---Best %s %s for %s results available at:---" % (len(fightHtmlOutputs), metric, fightStyle))
        for i in range(len(fightHtmlOutputs)):
            print("%s: %s (%s)" % (i+1, fightHtmlOutputs[i]["output"], fightHtmlOutputs[i][metric]))
        print("-------")
        print()

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

    if "Sim" not in config:
        config["Sim"] = {}

    if config.has_option("Sim", "maxthreads"):
        try:
            int(config["Sim"]["maxthreads"])
        except Exception:
            config["Sim"]["maxthreads"] = str(max(multiprocessing.cpu_count()-2, 1))
            print("WARN: Maxthreads option not a valid number. Defaulting maxthreads to %s" % config["Sim"]["maxthreads"])
    else:
        config["Sim"]["maxthreads"] = str(max(multiprocessing.cpu_count()-2, 1))
        print("INFO: Defaulting maxthreads to %s" % config["Sim"]["maxthreads"])

    if not config.has_option("Sim", "fightstyle"):
        config["Sim"]["fightstyle"] = "Patchwerk"
        print("INFO: Defaulting fightstyle to %s." % config["Sim"]["fightstyle"])

    if not config.has_option("Sim", "metric"):
        config["Sim"]["metric"] = "dps"
        print("INFO: Defaulting to optimizing %s." % config["Sim"]["metric"])

    # extend the acronym because simc is stupid
    if config["Sim"]["metric"] == "tmi":
        config["Sim"]["metric"] = "theck_meloree_index"

    if config["Sim"]["metric"] == "etmi":
        config["Sim"]["metric"] = "effective_theck_meloree_index"

    validMetrics = ["dps", "prioritydps", "dpse", "hps", "dtps", "dmg_taken", "theck_meloree_index", "tmi", "effective_theck_meloree_index", "etmi"]
    if config["Sim"]["metric"] not in validMetrics:
        print("Unknown metric value (%s) in config file. Valid Metrics are one of: %s" % (config["Sim"]["metric"], validMetrics))
        sys.exit(98)

    print()

    return dict(config)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- Full execution in %s seconds ---" % (time.time() - start_time))

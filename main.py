from analyze import *
from simulate import *
from generate import *

import configparser
import sys
import time

def main():
    config = loadConfig()
    print("Performing gear comparisons for %s on Fight Styles: %s" % (config["Profile"]["profilename"], config["Sim"]["fightstyle"]))
    print()

    generatedGear = generateGear(config)
    metric = config["Sim"]["metric"]

    for fightStyle, fightStyleGear in generatedGear.items():
        print("---Simming profiles for fight style %s---" % fightStyle)

        simInputs = []

        for validGear in fightStyleGear["valid"]:
            simInputs.append((fightStyle, validGear, config["Profile"], metric))

        topSims = runSims(simInputs, config["Sim"]["maxthreads"], metric)
        htmlOutputs = generateHtmlOutput(topSims, metric)

        # topSimDps = [x[1] for x in topSims]
        print("---Best %s %s for %s results available at:---" % (len(htmlOutputs), metric, fightStyle))
        for i in range(len(htmlOutputs)):
            print("%s: %s (%s) Gear: %s" % (i+1, htmlOutputs[i]["output"], htmlOutputs[i][metric], htmlOutputs[i]["equippedGear"]))
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
            print("WARN: maxthreads option not a valid number. Defaulting maxthreads to %s" % config["Sim"]["maxthreads"])
    else:
        config["Sim"]["maxthreads"] = str(max(multiprocessing.cpu_count()-2, 1))
        print("INFO: maxthreads option not set. Defaulting maxthreads to %s" % config["Sim"]["maxthreads"])

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

    return dict(config)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- Full execution in %s seconds ---" % (time.time() - start_time))

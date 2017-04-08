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
    topSims = {}

    for fightStyle in config["Sim"]["fightstyle"].split(","):
        simInputs = []
        topSims[fightStyle] = getTopSims(fightStyle, generatedGear["valid"], config["Profile"], config["Sim"]["maxthreads"], metric)

    for fightStyle, fightTopSims in topSims.items():
        print("---Best %s %s for %s results available at:---" % (len(fightTopSims), metric, fightStyle))
        for i in range(len(fightTopSims)):
            print("%s: %s (%s +/- %s) (Talents: %s)" % (i+1, fightTopSims[i]["htmlOutput"], "{:.1f}".format(fightTopSims[i][metric]), "{:.1f}".format(fightTopSims[i]["error"]), fightTopSims[i]["configProfile"]["talentSet"]))
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

    if config.has_option("Profile", "talents"):
        if config["Profile"]["talents"].lower() == "all":
            config["Profile"]["talents"] = allTalents()

    print()

    return dict(config)

def allTalents():
    talents = ""
    for a in range(1,4):
        for b in range(1,4):
            for c in range(1,4):
                for d in range(1,4):
                    for e in range(1,4):
                        for f in range(1,4):
                            for g in range(1,4):
                                talents += "%s%s%s%s%s%s%s," % (a,b,c,d,e,f,g)
    return talents[:-1]

if __name__ == "__main__":
    start_time = time.time()
    main()
    timeSeconds = (time.time() - start_time)
    print("--- Full execution in %s:%s ---" % (math.floor(timeSeconds/60), "{:04.1f}".format(timeSeconds % 60)))

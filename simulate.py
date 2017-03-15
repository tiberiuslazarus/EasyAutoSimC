import multiprocessing
import time
import sys
import subprocess
import os
from analyze import *
from generate import generateGearProfile
import tempfile
import traceback

simResults = []

def generateHtmlOutput(simInputs):
    outputId = 1
    htmlOutputs = []
    for simInput in simInputs:
        outputFileName = "%s/%s/%s.html" % (simInput["configProfile"]["profilename"], simInput["fightStyle"], outputId)
        htmlDict = runSim(simInput["fightStyle"], simInput["equippedGear"], simInput["configProfile"], "html", outputFileName, delete=False)
        htmlDict["output"] = "outputFileName"
        htmlDict["dps"] = simInput["dps"]
        htmlOutputs.append(htmlDict)
        outputId += 1
    return htmlOutputs

def runSims(simInputs, maxthreads):
    completedProfiles = 0
    totalProfiles = len(simInputs)
    topSims = []
    lastTime = time.time()
    # maxthreads = config["Sim"]["maxthreads"]

    while (len(simInputs) > 0):
        batchSize=min(100, len(simInputs))
        batchInputs = simInputs[:batchSize]
        del simInputs[:batchSize]

        if (int(maxthreads) > 1):
            topSims.extend(runSimsMultiThread(batchInputs, maxthreads))
        else:
            topSims.extend(runSimsSingleThread(batchInputs, "json"))


        topDps = [simDict for simDict in heapq.nlargest(5,topSims,key=itemgetter("dps"))]

        completedProfiles += batchSize
        print("%s of %s profiles completed." % (completedProfiles, totalProfiles))
        print("Last %s profiles simmed in %s seconds" % (batchSize, time.time() - lastTime))
        print()
        lastTime = time.time()
    return topDps

def runSimsMultiThread(simInputs, maxthreads):
    simStartTime = time.time()
    lastTime = simStartTime
    pool = multiprocessing.Pool(int(maxthreads));
    completedProfiles = 0

    try:
        simDicts = pool.starmap(runSim, simInputs)
        pool.close()
    except KeyboardInterrupt:
        pool.terminate()
        print("---Simming cancelled by user after %s profiles---" % completedProfiles)
        sys.exit(1)
    except Exception as e:
        pool.terminate()
        print('---Simming cancelled by exception: %r, terminating---' % e)
        traceback.print_exc()
        sys.exit(2)
    finally:
        pool.join()
    return simDicts

def runSim(fightStyle, equippedGear, configProfile, outputType="json", outputFileName=None, delete=True):
    gearProfileFile = tempfile.NamedTemporaryFile(mode="w", suffix=".simc", delete=False)
    gearProfileFile.write(generateGearProfile(gearProfileFile.name, equippedGear, configProfile))
    if outputFileName:
        if not os.path.exists(os.path.dirname(os.path.abspath(outputFileName))):
            os.makedirs(os.path.dirname(os.path.abspath(outputFileName)))
        outputFile = open(outputFileName, "w")
    else:
        outputFile = tempfile.NamedTemporaryFile(mode="w", delete=False)

    output = "%s=%s" % (outputType, outputFile.name)

    inputFile = gearProfileFile.name
    gearProfileFile.close()
    outputFile.close()

    subprocess.check_call(["simc.exe", inputFile, output, "threads=1", "fight_style=%s" % fightStyle], stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
    simDict = {"equippedGear": equippedGear, "fightStyle": fightStyle, "configProfile": configProfile}
    if outputType == "json":
        simDict["dps"] = processFile(outputFile)

    os.remove(gearProfileFile.name)
    if delete:
        os.remove(outputFile.name)

    return simDict

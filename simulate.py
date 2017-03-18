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

def generateHtmlOutput(simInputs, metric):
    outputId = 1
    htmlOutputs = []
    print("Generating html output reports for best %s %s reports" % (len(simInputs), metric))
    print()

    for simInput in simInputs:
        outputFileName = "results/%s/%s/%s.html" % (simInput["configProfile"]["profilename"], simInput["fightStyle"], outputId)
        htmlDict = runSim(simInput["fightStyle"], simInput["equippedGear"], simInput["configProfile"], metric, .1, "html", outputFileName, delete=False)
        htmlDict["output"] = outputFileName
        htmlDict[metric] = simInput[metric]
        htmlOutputs.append(htmlDict)
        outputId += 1
    return htmlOutputs

def runSims(fightStyle, gear, profile, maxthreads, metric):
    totalProfiles = len(gear)
    topSims = []
    lastTime = time.time()
    # maxthreads = config["Sim"]["maxthreads"]
    maxthreads = int(maxthreads)

    targetErrors = [100, 200, 500, 1000, 2000]
    targetErrorSims = []
    for errorIndex, targetError in enumerate(targetErrors):
        targetInputs = []
        # if there are 5 or less gear sets left to sim we can jump ahead to the last sim
        if (targetErrorSims != [] and len(targetErrorSims) <= 5) or len(gear) <= 5:
            if errorIndex != (len(targetErrors) - 1):
                continue
        if targetErrorSims != []:
            for gear in [targetErrorSim["equippedGear"] for targetErrorSim in targetErrorSims]:
                targetInputs.append((fightStyle, gearSet, profile, targetError, metric))
            targetErrorSims = []
        else:
            for gearSet in gear:
                targetInputs.append((fightStyle, gearSet, profile, targetError, metric))
        completedProfiles = 0

        print("Total size of run at %s%% error: %s" % (targetError, len(targetInputs)))

        while (len(targetInputs) > 0):
            topSims = []
            batchSize=min(100, len(targetInputs))
            batchInputs = targetInputs[:batchSize]
            del targetInputs[:batchSize]

            # print("Simming batch of %s gear options at %s%% target_error" % (batchSize, targetError))

            if (int(maxthreads) > 1):
                batchSims = runSimsMultiThread(batchInputs, maxthreads)
            else:
                batchSims = runSimsSingleThread(batchInputs, "json")

            smallestMetrics = ["dtps", "dmg_taken", "theck_meloree_index", "effective_theck_meloree_index"]
            metrics = [batchSim[metric] for batchSim in batchSims]
            if metric in smallestMetrics:
                bestMetric = min(metrics)
            else:
                bestMetric = max(metrics)

            # print("Size of batch sims: %s" % len(batchSims))
            # print("%s" % bestMetric)

            errorDifference = (1000/float(targetError))/100

            if metric in smallestMetrics:
                # print("Target error margin: %s" % (bestMetric*(1+errorDifference)))
                metricCutoff = bestMetric*(1+errorDifference)
                targetErrorSims.extend([sim for sim in batchSims if sim[metric] < metricCutoff])
            else:
                # print("Target error margin: %s" % (bestMetric*(1-errorDifference)))
                metricCutoff = bestMetric*(1-errorDifference)
                targetErrorSims.extend([sim for sim in batchSims if sim[metric] > metricCutoff])

            if len(targetErrorSims) < 5:
               if metric in smallestMetrics:
                   targetErrorSims = [simDict for simDict in heapq.nsmallest(5,batchSims,key=itemgetter(metric))]
               else:
                   targetErrorSims = [simDict for simDict in heapq.nlargest(5,batchSims,key=itemgetter(metric))]

            completedProfiles += batchSize
            # print("%s of %s profiles completed." % (completedProfiles, totalProfiles))
            # print("Last %s profiles simmed in %s seconds" % (batchSize, time.time() - lastTime))
            # print()
            lastTime = time.time()

    if metric in smallestMetrics:
        topSims = [simDict for simDict in heapq.nsmallest(5,targetErrorSims,key=itemgetter(metric))]
    else:
        topSims = [simDict for simDict in heapq.nlargest(5,targetErrorSims,key=itemgetter(metric))]
    return topSims

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

def runSim(fightStyle, equippedGear, configProfile, targetError=1000, metric="dps", outputType="json", outputFileName=None, delete=True):
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

    subprocess.check_call(["simcraft/simc.exe", inputFile, output, "threads=1", "fight_style=%s" % fightStyle, "iterations=%s" % targetError], stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
    simDict = {"equippedGear": equippedGear, "fightStyle": fightStyle, "configProfile": configProfile}
    if outputType == "json":
        simDict[metric] = processFile(outputFile, metric)

    os.remove(gearProfileFile.name)
    if delete:
        os.remove(outputFile.name)

    return simDict

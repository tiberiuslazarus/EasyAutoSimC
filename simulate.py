import multiprocessing
import time
import sys
import subprocess
import os
from analyze import *
from generate import generateGearProfile
import tempfile
import traceback
import math

def generateHtmlOutput(simInputs, metric):
    outputId = 1
    htmlOutputs = []
    print("Generating html output reports for best %s %s reports" % (len(simInputs), metric))
    print()

    for simInput in simInputs:
        outputFileName = "results/%s/%s/%s.html" % (simInput["configProfile"]["profilename"], simInput["fightStyle"], outputId)
        htmlDict = runSim(simInput["fightStyle"], simInput["equippedGear"], simInput["configProfile"], metric, 15000, "html", outputFileName, delete=False)
        htmlDict["output"] = outputFileName
        htmlDict[metric] = simInput[metric]
        htmlOutputs.append(htmlDict)
        outputId += 1
    return htmlOutputs

def runSims(fightStyle, gear, profile, maxthreads, metric):
    totalProfiles = len(gear)
    topSims = []
    maxthreads = int(maxthreads)
    smallestMetrics = ["dtps", "dmg_taken", "theck_meloree_index", "effective_theck_meloree_index"]
    minResultSize = 5
    totalSimTime = 0
    completedSims = 0

    iterationSequence = [100,200,500,5000,15000]

    simInputs = []
    for gearSet in gear:
        simInputs.append([fightStyle, gearSet, profile, metric])

    for iterations in iterationSequence:
        if len(simInputs) <= minResultSize:
            if iterations != max(iterationSequence):
                continue
        for simInput in simInputs:
            simInput.append(iterations)

        print("Total size of run at %s iterations: %s" % (iterations, len(simInputs)))

        simResults = []
        while (len(simInputs) > 0):
            batchStartTime = time.time()
            batchSize=min(100, len(simInputs))
            batchInputs = simInputs[:batchSize]
            del simInputs[:batchSize]
            if maxthreads > 1:
                simResults.extend(runSimsMultiThread(batchInputs, maxthreads))
            else:
                simResults.extend(runSimsSingleThread(batchInputs, "json"))
            completedSims += batchSize
            totalSimTime += (time.time() - batchStartTime)
            print("Completed last batch of %s in %s seconds" % (len(batchInputs), (time.time() - batchStartTime)))
            if len(simInputs) > 0:
                print("Estimated time remaining: %s minutes" % (math.ceil((totalSimTime/completedSims)*len(simInputs)/60)))

        simResultMetrics = [(simResult[metric], simResult["error"]) for simResult in simResults]

        if metric in smallestMetrics:
            bestMetricTuple = min(simResultMetrics, key = lambda t: t[0]+t[1])
            bestMetric=bestMetricTuple[0]+bestMetricTuple[1]
            for simResult in simResults:
                tempBestResults = [x for x in simResults if (x[metric] - x["error"]) < bestMetric]
        else:
            bestMetricTuple = max(simResultMetrics, key = lambda t: t[0]-t[1])
            bestMetric=bestMetricTuple[0]-bestMetricTuple[1]
            for simResult in simResults:
                tempBestResults = [x for x in simResults if (x[metric] + x["error"]) > bestMetric]

        if len(tempBestResults) < minResultSize:
            if metric in smallestMetrics:
                simResults = [simDict for simDict in heapq.nsmallest(minResultSize, simResults, key=itemgetter(metric))]
            else:
                simResults = [simDict for simDict in heapq.nlargest(minResultSize, simResults, key=itemgetter(metric))]
        else:
            simResults = tempBestResults

        simInputs = []
        for simResult in simResults:
            simInputs.append([fightStyle, simResult["equippedGear"], profile, metric])

        print()

    if metric in smallestMetrics:
        simResults = [simDict for simDict in heapq.nsmallest(minResultSize, simResults, key=itemgetter(metric))]
    else:
        simResults = [simDict for simDict in heapq.nlargest(minResultSize, simResults, key=itemgetter(metric))]
    return simResults

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

def runSim(fightStyle, equippedGear, configProfile, metric="dps", iterations=1000, outputType="json", outputFileName=None, delete=True):
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

    subprocess.check_call(["simcraft/simc.exe", inputFile, output, "threads=1", "fight_style=%s" % fightStyle, "iterations=%s" % iterations], stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
    simDict = {"equippedGear": equippedGear, "fightStyle": fightStyle, "configProfile": configProfile}

    if outputType == "json":
        analysisResult = processFile(outputFile, metric)
        simDict[metric] = analysisResult[0]
        simDict["error"] = analysisResult[1]*1.96

    os.remove(gearProfileFile.name)
    if delete:
        os.remove(outputFile.name)

    return simDict

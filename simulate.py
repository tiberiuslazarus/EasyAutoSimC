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
import itertools
import shutil

smallestMetrics = ["dtps", "dmg_taken", "theck_meloree_index", "effective_theck_meloree_index"]
minResultSize = 5

def getTopSims(fightStyle, gear, profile, maxthreads, metric):
    topSims = getBestSimResults(metric, runSims(fightStyle, gear, profile, maxthreads, metric))

    for i, topSim in enumerate(topSims):
        outputDir = "results/%s/%s" % (topSim["configProfile"]["profilename"], topSim["fightStyle"])
        newFileName = "%s/%s.html" % (outputDir, i+1)
        if not os.path.exists(outputDir):
            os.makedirs(os.path.dirname(os.path.abspath(newFileName)))
        if not os.path.isfile(topSim["htmlOutput"]):
            print("--Info: Temp html file for a top simming gear set no longer exists. Regenerating...")
            newTopSim = runSim(topSim["fightStyle"], topSim["equippedGear"], topSim["configProfile"], metric, 15000)
            topSim = newTopSim

        moveHtmlOutputs(topSim["htmlOutput"], newFileName)
        topSim["htmlOutput"] = newFileName

    return topSims

def moveHtmlOutputs(curFileName, newFileName):
    if not os.path.exists(os.path.dirname(os.path.abspath(newFileName))):
        os.makedirs(os.path.dirname(os.path.abspath(newFileName)))
    if os.path.isfile(curFileName):
        shutil.move(curFileName, newFileName)
    else:
        print("ERROR: expected file (%s) does not exist. Cannot move to (%s)" % (curFileName, newFileName))

def generateHtmlOutput(simInputs, metric):
    outputId = 1
    htmlOutputs = []
    print("Generating html output reports for best %s %s reports" % (len(simInputs), metric))
    print()

    for simInput in simInputs:
        # outputFileName = "results/%s/%s/%s.html" % (simInput["configProfile"]["profilename"], simInput["fightStyle"], outputId)
        htmlDict = runSim(simInput["fightStyle"], simInput["equippedGear"], simInput["configProfile"], metric, 15000, delete=False)
        htmlDict["output"] = outputFileName
        htmlDict[metric] = simInput[metric]
        htmlOutputs.append(htmlDict)
        outputId += 1
    return htmlOutputs

def runSims(fightStyle, gear, profile, maxthreads, metric):
    talentSets = profile["talents"].split(",")
    topSims = []
    maxthreads = int(maxthreads)
    totalSimTime = 0
    completedSims = 0

    iterationSequence = [10,100,500,5000,15000]

    simInputs = []
    for talentSet in talentSets:
        profile["talentSet"] = talentSet
        for gearSet in gear:
            simInputs.append([fightStyle, gearSet, profile, metric])

    for iterations in iterationSequence:
        isLastIteration = (iterations == iterationSequence[len(iterationSequence)-1])
        if len(simInputs) <= minResultSize:
            if not isLastIteration:
                continue
        for simInput in simInputs:
            simInput.append(iterations)

        simResults = []
        maxBatchSize=max(100, (math.ceil(len(simInputs) / 100.0)))

        print("Total size of run at %s iterations: %s (%s Talent Sets * %s Gear Sets)" % (iterations, len(simInputs), len(talentSets), len(gear)))
        print("Batch size of %s" % min(maxBatchSize, len(simInputs)))

        while (len(simInputs) > 0):
            batchStartTime = time.time()

            batchSize=min(maxBatchSize, len(simInputs))
            batchInputs = simInputs[:batchSize]
            del simInputs[:batchSize]

            if maxthreads > 1:
                simResults.extend(runSimsMultiThread(batchInputs, maxthreads))
            else:
                simResults.extend(runSimsSingleThread(batchInputs))

            completedSims += batchSize
            totalSimTime += (time.time() - batchStartTime)

            print("Completed last batch of %s in %s seconds" % (len(batchInputs), format((time.time() - batchStartTime), ".1f")))
            if len(simInputs) > 0:
                secondsPerSim = (totalSimTime/completedSims)*len(simInputs)
                estRemaining = math.ceil(secondsPerSim/60)
                if estRemaining == 1:
                    print("Estimated time remaining: less than 1 minute")
                else:
                    print("Estimated time remaining: %s minutes" % (estRemaining))

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
            bestSimResults = getBestSimResults(metric, simResults)
        else:
            bestSimResults = tempBestResults

        for removedSimResult in list(itertools.filterfalse(lambda x: x in bestSimResults, simResults)):
            removeTempFile(removedSimResult["htmlOutput"])

        simInputs = []
        for simResult in bestSimResults:
            simInputs.append([fightStyle, simResult["equippedGear"], profile, metric])
            if not isLastIteration:
                removeTempFile(simResult["htmlOutput"])
        print()

    bestSimResults = getBestSimResults(metric, simResults)

    for removedSimResult in list(itertools.filterfalse(lambda x: x in bestSimResults, simResults)):
        removeTempFile(removedSimResult["htmlOutput"])

    return bestSimResults

def getBestSimResults(metric, simResults):
    if metric in smallestMetrics:
        bestSimResults = [simDict for simDict in heapq.nsmallest(minResultSize, simResults, key=itemgetter(metric))]
    else:
        bestSimResults = [simDict for simDict in heapq.nlargest(minResultSize, simResults, key=itemgetter(metric))]
    return bestSimResults

def removeTempFile(tempFile):
    try:
        os.remove(tempFile)
    except:
        pass

def runSimsSingleThread(simInputs):
    simResults = []
    for simInput in simInputs:
        simResults.append(runSim(*simInput))
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

def runSim(fightStyle, equippedGear, configProfile, metric="dps", iterations=1000):
    gearProfileFile = tempfile.NamedTemporaryFile(mode="w", suffix=".simc", delete=False)
    gearProfileFile.write(generateGearProfile(gearProfileFile.name, equippedGear, configProfile))

    outputFileJson = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    outputFileHtml = tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False)

    inputFile = gearProfileFile.name
    gearProfileFile.close()

    outputFileJson.close()
    outputFileHtml.close()

    subprocess.check_call(["simcraft/simc.exe", inputFile, "json=%s" % outputFileJson.name, "html=%s" % outputFileHtml.name, "threads=1", "fight_style=%s" % fightStyle, "iterations=%s" % iterations], stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
    simDict = {"equippedGear": equippedGear, "fightStyle": fightStyle, "configProfile": configProfile, "htmlOutput": outputFileHtml.name}

    analysisResult = processFile(outputFileJson, metric)
    simDict[metric] = analysisResult[0]
    simDict["error"] = analysisResult[1]*1.96

    os.remove(gearProfileFile.name)
    os.remove(outputFileJson.name)

    return simDict

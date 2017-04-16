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
iterationSequence = [10,100,500,5000,15000]

def getTopSims(fightStyle, gear, profile, maxthreads, metric):
    topSims = getBestSimResults(metric, runSims(fightStyle, gear, profile, maxthreads, metric))

    for i, topSim in enumerate(topSims):
        outputDir = "results/%s/%s" % (topSim["configProfile"]["profilename"], topSim["fightStyle"])
        newFileName = "%s/%s.html" % (outputDir, i+1)
        if not os.path.exists(outputDir):
            os.makedirs(os.path.dirname(os.path.abspath(newFileName)))
        if not os.path.isfile(topSim["htmlOutput"]):
            print("--Info: Temp html file for a top simming gear set no longer exists. Regenerating...")
            newTopSim = runSim(topSim["fightStyle"], topSim["equippedGear"], topSim["configProfile"], metric, iterationSequence[len(iterationSequence)-1])
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

    simInputs = []
    for talentSet in talentSets:
        if talentSet == "":
            continue
        profile["talentSet"] = talentSet
        for gearSet in gear:
            simInputs.append([fightStyle, gearSet, profile, metric])

    print("%s Talent Sets * %s Gear Sets" % (len(talentSets), len(gear)))

    for iterations in iterationSequence:
        totalIterationGear = len(simInputs)
        isLastIteration = (iterations == iterationSequence[len(iterationSequence)-1])
        if len(simInputs) <= minResultSize:
            if not isLastIteration:
                continue
        for simInput in simInputs:
            simInput.append(iterations)

        simResults = []
        iterationTime = 0
        completedSims = 0
        maxBatchSize=max(100, (10**math.floor(math.log(len(simInputs),10))))
        maxBatchSize=10

        print("Total size of run at %s iterations: %s" % (iterations, len(simInputs)))
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

            batchTime = (time.time() - batchStartTime)
            completedSims += batchSize
            iterationTime += batchTime

            printProgressBar(completedSims, totalIterationGear, batchTime, iterationTime)

        totalSimTime += iterationTime
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
    simProfile = generateGearProfile("easc", equippedGear, configProfile)

    simcCall = ["simcraft/simc.exe", "threads=1", "fight_style=%s" % fightStyle, "iterations=%s" % iterations]
    simcCall.extend(simProfile)
    outputFileHtml = None

    if iterations == iterationSequence[len(iterationSequence)-1]:
        outputFileHtml = tempfile.NamedTemporaryFile(mode="w", suffix=".html", prefix="easc_", delete=False)
        simcCall.append("html=%s" % outputFileHtml.name)

    simcOutput = subprocess.check_output(simcCall, stderr=subprocess.DEVNULL).decode("utf-8")

    analysisResult = processOutput(simcOutput, metric)

    simDict = {
        "equippedGear": equippedGear,
        "fightStyle": fightStyle,
        "configProfile": configProfile,
        "htmlOutput": (outputFileHtml.name if outputFileHtml else ""),
        metric: analysisResult[0],
        "error": analysisResult[1]
    }

    return simDict

def printProgressBar(completed, totalSize, stageTime, totalIterationTime, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (completed / float(totalSize)))

    estRemaining = 0
    if completed < totalSize:
        remainingSeconds = (totalIterationTime/completed)*totalSize
        estRemaining = math.ceil(remainingSeconds/60)

    filledLength = int(length * completed // totalSize)
    bar = fill * filledLength + '-' * (length - filledLength)
    if completed < totalSize: 
        if estRemaining == 1:
            print('\r%s |%s| %s%% %s (Estimated remaining time: less than 1 minute)' %
                (prefix, bar, percent, suffix), end = '\r')
        else:
            print('\r%s |%s| %s%% %s (Estimated remaining time: %s %s)' %
                (prefix, bar, percent, suffix, estRemaining, "minutes" if estRemaining != 1 else "minute"), end = '\r')
    else:
        m, s = divmod(totalIterationTime, 60)
        print('\r%s |%s| %s%% %s (Time taken: %s:%s)                               ' 
            % (prefix, bar, percent, suffix, "{0:02d}".format(int(m)), "{0:04.1f}".format(s)))

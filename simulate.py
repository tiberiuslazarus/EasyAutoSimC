import multiprocessing
import time
import sys
import subprocess
import os
from analyze import *
import traceback
import math
import itertools
import shutil
import gear

import cProfile
import logging
logger = logging.getLogger()

smallestMetrics = ["dtps", "theck_meloree_index", "tmi"]
minResultSize = 10
iterationSequence = [10,100,500,5000,15000]

def getTopSims(fightStyle, gearList, profile, maxthreads, metric, statWeights, enemies):
	logger.debug("started getTopSims()")
	return getBestSimResults(metric, runSims(fightStyle, gearList, profile, maxthreads, metric, statWeights, enemies))

def runSims(fightStyle, gearList, profile, maxthreads, metric, statWeights, enemies):
	logger.debug("started runSims()")

	talentSets = profile["talents"].split(",")
	maxthreads = int(maxthreads)

	simInputs = []
	simResults = []

	for iterations in iterationSequence:
		if simResults != [] and len(simResults) <= minResultSize:
			if not isLastIteration(iterations):
				continue

		print("--Beginning sims at %s Iterations" % (iterations))
		if simResults == []:
			simResults = getBestSimResults(metric, runIterations(gearList, fightStyle, dict(profile), metric, statWeights, enemies, maxthreads, iterations, talentSets))
		else:
			simResults = getBestSimResults(metric, runIterations(simResults, fightStyle, dict(profile), metric, statWeights, enemies, maxthreads, iterations))

	# All iterations done
	bestSimResults = getBestSimResults(metric, simResults, minResults=True)

	logger.debug("done runSims()")
	return bestSimResults

def runIterations(simGear, fightStyle, profile, metric, statWeights, enemies, maxthreads, iterations, talentSets=None):
	manager = multiprocessing.Manager()

	gearQueue = manager.Queue(maxthreads*2)
	tempResultsQueue = manager.Queue()
	resultsQueue = manager.Queue()
	progressQueue = manager.Queue()
	
	resultsList = []

	gearObj = gear.Gear(simGear)
	talentCount = len(talentSets) if talentSets else 1
	totalGearSets = gearObj.getPossibleCount() * talentCount

	progressProcess = multiprocessing.Process(target=printProgress, name="progress", args=(totalGearSets, progressQueue, iterations))
	progressProcess.start()
	
	resultProcesserProcess = multiprocessing.Process(target=resultProcesser, name="resultProcesser", args=(tempResultsQueue, resultsQueue, metric))
	resultProcesserProcess.start()

	threads = 1 if isLastIteration(iterations) else maxthreads

	simProcesses = [multiprocessing.Process(target=worker, args=(fightStyle, profile, metric, statWeights, enemies, maxthreads, iterations, gearQueue, tempResultsQueue, progressQueue)) for i in range(threads)]
	gearProcess = multiprocessing.Process(target=gearObj.getGear, name="gearWorker", args=(gearQueue,talentSets))

	for proc in simProcesses:
		proc.start()
	gearProcess.start()

	gearProcess.join()

	for proc in simProcesses:
		gearQueue.put(None)
	for proc in simProcesses:
		proc.join()
	
	tempResultsQueue.put(None)
	resultProcesserProcess.join()

	progressQueue.put(None)
	progressProcess.join()

	print()

	while resultsQueue.qsize() != 0:
		result = resultsQueue.get()
		if result is not False:
			resultsList.append(result)

	return resultsList

def isLastIteration(iterations):
	return (iterations == iterationSequence[len(iterationSequence)-1])

def worker(fightStyle, profile, metric, statWeights, enemies, maxthreads, iterations, gearQueue, tempResultsQueue, progressQueue):
	cProfile.runctx('workerRun(fightStyle, profile, metric, statWeights, enemies, maxthreads, iterations, gearQueue, tempResultsQueue, progressQueue)', globals(), locals(), filename='cprofile.txt')

def workerRun(fightStyle, profile, metric, statWeights, enemies, maxthreads, iterations, gearQueue, tempResultsQueue, progressQueue):
	threads = maxthreads if isLastIteration(iterations) else 1
	while True:
		gear = gearQueue.get()
		newResult = False
		if gear is None:
			break
		if gear is not False:
			profile["talentset"] = gear[1]
			newResult = runSim(fightStyle, gear[0], profile, metric, statWeights, enemies, iterations, threads)
			tempResultsQueue.put(newResult)
		progressQueue.put(not newResult is False)

def resultProcesser(tempResultsQueue, resultsQueue, metric):
	bestResult = (None, None)
	while True:
		tempResult = tempResultsQueue.get()
		if tempResult is None:
			break

		if tempResult is not False:
			if bestResult[0] is None:
				bestResult = (tempResult[metric], tempResult["error"])

			bestMetric = bestResult[0]

			if resultsQueue.qsize() > minResultSize:
				if metric in smallestMetrics:
					if (tempResult[metric] - tempResult["error"]*.75) > bestMetric:
						tempResult = False
					elif tempResult[metric] < bestMetric:
						bestResult = (tempResult[metric], tempResult["error"])
				else:
					if (tempResult[metric] + tempResult["error"]*1.25) < bestMetric:
						tempResult = False
					elif tempResult[metric] > bestMetric:
						bestResult = (tempResult[metric], tempResult["error"])
				
		resultsQueue.put(tempResult)

def getBestSimResults(metric, simResults, minResults=None):
	logger.debug("started getBestSimResults()")
	bestSimResults = None

	simResultMetrics = [(simResult[metric], simResult["error"]) for simResult in simResults]

	if metric in smallestMetrics:
		bestMetricTuple = min(simResultMetrics, key = lambda t: t[0]+t[1])
		bestMetric=bestMetricTuple[0]+bestMetricTuple[1]
		tempBestResults = [x for x in simResults if (x[metric] - x["error"]) < bestMetric]
	else:
		bestMetricTuple = max(simResultMetrics, key = lambda t: t[0]-t[1])
		bestMetric=bestMetricTuple[0]-bestMetricTuple[1]
		tempBestResults = [x for x in simResults if (x[metric] + x["error"]) > bestMetric]

	if len(tempBestResults) < minResultSize or minResults:
		if metric in smallestMetrics:
			bestSimResults = [simDict for simDict in heapq.nsmallest(minResultSize, simResults, key=itemgetter(metric))]
		else:
			bestSimResults = [simDict for simDict in heapq.nlargest(minResultSize, simResults, key=itemgetter(metric))]
	else:
		bestSimResults = tempBestResults

	logger.debug("done getBestSimResults()")
	return bestSimResults

def runSim(fightStyle, equippedGear, configProfile, metric, statWeights, enemies, iterations, threads="1"):
	logger.debug("started runSim()")
	simProfile = generateProfile("easc", equippedGear, configProfile, enemies)

	if os.name == 'nt':
		simcProgram = "simc.exe"
	else:
		simcProgram = "simc"
	simcCall = ["simcraft/%s" % simcProgram, "threads=%s" % threads, "fight_style=%s" % fightStyle, "iterations=%s" % iterations]
	simcCall.extend(simProfile)

	if isLastIteration(iterations):
		if statWeights != "0":
			simcCall.append("calculate_scale_factors=1")

			if metric == "tmi":
				simcCall.append("scale_over=tmi")

	simcOutput = subprocess.check_output(simcCall, stderr=subprocess.DEVNULL).decode("utf-8")

	analysisResult = processOutput(simcOutput, metric)


	simDict = {
		"equippedGear": equippedGear,
		"fightStyle": fightStyle,
		"configProfile": configProfile,
		"metric": metric,
		metric: analysisResult[0],
		"error": analysisResult[1],
		"enemies": enemies
	}

	if isLastIteration(iterations):
		if statWeights == "1":
			simDict["scaleFactors"] = getScaleFactors(simcOutput)
		simDict["stats"] = getCharStats(simcOutput)

	logger.debug("done runSim()")
	return simDict

def printProgress(totalCount, progressQueue, iterations):
	completed = 0
	valid = 0
	startTime = time.time()
	while True:
		loopTime = time.time()
		while not progressQueue.empty() and (time.time() - loopTime) < 1:
			try:
				newProgress = progressQueue.get(timeout=1)
			except:
				newProgress = 0
				pass
			if newProgress is None:
				print("%s simulations completed in %s                                                                 " % (totalCount, "{0:03.1f}".format(time.time() - startTime)))
				return
			if newProgress is not 0:
				completed += 1
				if newProgress:
					valid += 1

		runTime = time.time() - startTime
		if completed > 0:
			timePerSim = runTime / completed
			remainingTime = (timePerSim * (totalCount - completed))
			if valid != completed:
				print("\rCompleted %s valid sims out of %s total (%s invalid) in %s (%s remaining)   " % (completed, totalCount, (completed-valid), "{0:03.1f}".format(runTime), "{0:03.1f}".format(remainingTime)), end = '\r')
			else:
				print("\rCompleted %s valid sims out of %s total in %s (%s remaining)                " % (completed, totalCount, "{0:03.1f}".format(runTime), "{0:03.1f}".format(remainingTime)), end = '\r')
		else:
			print("\rSimulations in progress. Elapsed: %s                                                             " % ("{0:03.1f}".format(runTime)), end="\r")
			# print("Completed %s sims out of %s total in %s (%s remaining)                       " % (completed, totalCount, runTime, remainingTime))
		time.sleep(1)

def generateProfile(outputFileName, equippedGear, configProfile, enemies):
	logger.debug("started generateGearProfile()")
	gearProfile = []
	gearProfile.append("%s=%s_%s" % (configProfile["class"], configProfile["profilename"], outputFileName))
	gearProfile.append("specialization=%s" % (configProfile["spec"]))
	gearProfile.append("race=%s" % (configProfile["race"]))
	gearProfile.append("level=%s" % (configProfile["level"]))
	gearProfile.append("role=%s" % (configProfile["role"]))
	gearProfile.append("position=%s" % (configProfile["position"]))
	gearProfile.append("talents=%s" % (configProfile["talentset"]))
	gearProfile.append("skill=%s" % (float(configProfile["skill"]) / 100))
	if "max_time" in configProfile:
		gearProfile.append("max_time=%s" % (configProfile["max_time"]))
		
	if "vary_combat_length" in configProfile:
		gearProfile.append("vary_combat_length=%s" % (float(configProfile["vary_combat_length"]) / 100))
		
	for slot, gear in equippedGear.items():
		if gear != "":
			gearProfile.append("%s=%s" % (slot, (gear if gear[0]!="L" else gear[1:])))

	try:
		for i in range(int(enemies)):
			gearProfile.append("enemy=enemy_%s" % i)
	except:
		pass

	logger.debug("done generateGearProfile()")
	return gearProfile

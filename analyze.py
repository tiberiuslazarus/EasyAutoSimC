import os
import time
import json
import heapq
import re
from operator import itemgetter
from multiprocessing import Pool

def processOutput(simcOutput, metric):
	for line in simcOutput.split("\n"):
		if "%s:" % metric.upper() in line:
			vals = re.findall("\d+\.?\d*", line)
			return (float(vals[0]), float(vals[1]))

	print("WARN: Metric not found in simc output. This is weird...")
	# print("WARN: Simc Output")
	# print(simcOutput)
	# print("WARN: End Simc Output")
	return (0,0)

def processFileJson(outputFile, metric):
	with open(outputFile.name, "r") as jsonFile:
		try:
			simInfo = json.load(jsonFile)
			return (float(simInfo["sim"]["players"][0]["collected_data"][metric]["mean"]), float(simInfo["sim"]["players"][0]["collected_data"][metric]["mean_std_dev"]))
		except Exception as e:
			print('--- Error reading simulation output file (%s) with error: %s ---' % (outputFile, e))
			print("--- File contents ---")
			for line in jsonFile:
				print(line)
			print("--- End file contents ---")
			return (0,0)

def analyzeSims(profiles, maxthreads):
	analysisStartTime = time.time()
	dpsList = Pool(int(maxthreads)).starmap(processFile, profiles)

	return [dpsTuple for dpsTuple in heapq.nlargest(5,dpsList,key=itemgetter(2))]

def getTopDps(profiles):
	topDps = {}
	for profile in profiles:
		fightStyle, profileId, dps = profile[0], profile[1], profile[2]
		topDps.setDefault(fightStyle, []).append(profile)
	for fightStyle, profiles in topDps:
		topDps[fightStyle] = [dpsTuple for dpsTuple in heapq.nlargest(5,dpsList,key=itemgetter(2))]
	print(topDps)
	return topDps

if __name__ == "__main__":
	outputFiles = os.listdir(".\\output\\json")
	profiles = []
	for filename in outputFiles:
		profiles.append(os.path.splitext(filename)[0])
	analyzeSims(profiles)

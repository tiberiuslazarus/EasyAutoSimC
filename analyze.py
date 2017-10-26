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
	return (0,0)

def getScaleFactors(simcOutput):
	scaleFactorsFound = False
	for line in simcOutput.split("\n"):
		if scaleFactorsFound:
			factors = line.split()
			factorsDict = {}
			for factor in factors:
				if "=" in factor:
					factorSplit = factor.split("=")
					factorsDict[factorSplit[0]] = factorSplit[1].split("(")[0]
				else:
					factors.remove(factor)
			return factorsDict
		elif "Scale Factors:" in line:
			scaleFactorsFound = True
	return {}

#   Core Stats:    strength=8805|8480(8480)  agility=36378|34147(32973)  stamina=61899|61899(42689)  intellect=5323|4998(4998)  spirit=5|5(5)  health=3713940|3713940  mana=0|0
#   Generic Stats: mastery=62.51%|62.51%(5861)  versatility=12.47%|12.47%(5921)  leech=0.00%|0.00%(0)  runspeed=8.05%|8.05%(0)
#   Spell Stats:   power=0|0(0)  hit=15.00%|15.00%(0)  crit=32.55%|32.55%(9019)  haste=10.55%|10.55%(3957)  speed=10.55%|10.55%  manareg=0|0(0)
#   Attack Stats:  power=36378|34147(0)  hit=7.50%|7.50%(0)  crit=32.55%|32.55%(9019)  expertise=7.50%/7.50%|7.50%/7.50%(0)  haste=10.55%|10.55%(3957)  speed=10.55%|10.55%
#   Defense Stats: armor=2476|2476(2476) miss=3.00%|3.00%  dodge=23.58%|22.49%(0)  parry=3.00%|3.00%(0)  block=0.00%|0.00%(0) crit=0.00%|0.00%  versatility=6.23%|6.23%(5921)
def getCharStats(simcOutput):
	charStats = {}
	coreFound = False
	genericFound = False
	spellFound = False
	attackFound = False
	defenseFound = False

	for line in simcOutput.split("\n"):
		if "Core Stats" in line and not coreFound:
			coreFound = True
			charStats["core"] = splitStats(line)
		elif "Generic Stats" in line and not genericFound:
			genericFound = True
			charStats["generic"] = splitStats(line)
		elif "Spells Stats" in line and not spellFound:
			spellFound = True
			charStats["spell"] = splitStats(line)
		elif "Attack Stats" in line and not attackFound:
			attackFound = True
			charStats["attack"] = splitStats(line)
		elif "Defense Stats" in line and not defenseFound:
			defenseFound = True
			charStats["defense"] = splitStats(line)
		if coreFound and genericFound and spellFound and attackFound and defenseFound:
			break

	return charStats

def splitStats(statsLine):
	stats = statsLine.split()
	statsDict = {}
	for stat in stats:
		if "=" in stat:
			statSplit = stat.split("=")
			statValSplit = statSplit[1].split("|")
			statsDict[statSplit[0]] = {
				"buffed": statValSplit[0],
				"unbuffed": statValSplit[1].split("(")[0]
			}
	return statsDict


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

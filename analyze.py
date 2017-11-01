import os
import time
import json
import heapq
import re
from operator import itemgetter
from multiprocessing import Pool
import logging
logger = logging.getLogger()

def processOutput(simcOutput, metric):
	logger.debug("started processOutput()")
	for line in simcOutput.split("\n"):
		if "%s:" % metric.upper() in line:
			vals = re.findall("\d+\.?\d*", line)
			return (float(vals[0]), float(vals[1]))

	print("WARN: Metric not found in simc output. This is weird...")
	return (0,0)

def getScaleFactors(simcOutput):
	logger.debug("started getScaleFactors()")
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
	logger.debug("started getCharStats()")
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
	logger.debug("started splitStats()")
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

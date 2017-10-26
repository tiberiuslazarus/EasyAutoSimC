from generate import *
from simulate import *
from analyze import *

import configparser
import sys
import time
import urllib.request
import webbrowser
import datetime

def main():
	checkVersion()
	config = loadConfig()
	print("Performing gear comparisons for %s on Fight Styles: %s" % (config["Profile"]["profilename"], config["Sim"]["fightstyle"]))
	print("Simming at player skill level: %s%%" % config["Profile"]["skill"])
	print("Using %s threads" % config["Sim"]["maxthreads"])
	print()

	generatedGear = generateGear(config["Gear"])

	metric = config["Sim"]["metric"]
	statWeights = config["Sim"]["statweights"]
	if "enemies" in config["Sim"]:
		enemiesList = config["Sim"]["enemies"].split(",")
	else:
		enemiesList = [None]
	topSims = {}

	for fightStyle in config["Sim"]["fightstyle"].split(","):
		topSims[fightStyle] = {}
		for enemies in enemiesList:
			if enemies != None:
				print("---Simming %s with %s enemies---" % (fightStyle, enemies))
			else:
				print("---Simming %s---" % fightStyle)
			simInputs = []
			topSims[fightStyle][enemies] = getTopSims(fightStyle, generatedGear["valid"], config["Profile"], config["Sim"]["maxthreads"], metric, statWeights, enemies)

	indexName = createIndex(topSims, config["Profile"]["profilename"])

	for fightStyle, enemiesFightTopSims in topSims.items():
		for enemies, fightTopSims in enemiesFightTopSims.items():
			print("---Best %s %s for %s results available at: %s---" % (len(fightTopSims), metric, fightStyle, indexName))
			for i in range(len(fightTopSims)):
				print("%s: %s +/- %s (Talents: %s)" %
				 (i+1,
				  "{:.1f}".format(fightTopSims[i][metric]),
				  "{:.1f}".format(fightTopSims[i]["error"]),
				  fightTopSims[i]["configProfile"]["talentset"]))
		print("-------")
		print()
	webbrowser.open("%s/%s" % (os.getcwd(), indexName))

def createIndex(topSims, profileName):
	outputIndexName = 'results/%s/results_%s.html' % (profileName, datetime.datetime.now().strftime("%y%m%d%H%M"))
	with open('web/index.template.html') as indexTemplate:
		navString = ""
		resultsString = ""
		for fightStyle, enemiesFightTopSims in topSims.items():
			for enemies, fightTopSims in enemiesFightTopSims.items():
				if enemies != None:
					navString += "<ul id='%s_%s' class='nav'><h3>%s <div>(%s Enemies)</div></h3>" % (fightStyle, enemies, fightStyle, enemies)
				else:
					navString += "<ul id='%s' class='nav'><h3>%s</h3>" % (fightStyle, fightStyle)
				for i, topSim in enumerate(fightTopSims):
					navString += "<li class='tooltip'><a onclick=\"showResult('%s_%s_%s')\">%s</a><div class='tooltiptext'>%s: %s</div></li>" % (fightStyle, i+1, enemies, i+1, topSim["metric"], topSim[topSim["metric"]])

					resultsString += """<div id='%s_%s_%s' class='result'>
						<div class='header name'>%s</div>
						<div class='header metric'>%s %s on %s</div>
						<div class='header rank'>Rank %s</div>
						<div class='header talents'>Talents: %s</div>
						<div class='header skill'>Player Skill: %s</div>
						<div class='header enemies'>Enemy count: %s</div>
						""" % (
							fightStyle, i+1, enemies, profileName, topSim["metric"].upper(), topSim[topSim["metric"]], fightStyle, i+1, topSim["configProfile"]["talentset"], topSim["configProfile"]["skill"], topSim["enemies"]
						)

					leftSlots = ["head", "neck", "shoulders", "back", "chest", "wrists"]
					rightSlots = ["hands", "waist", "legs", "feet", "finger1", "finger2", "trinket1", "trinket2"]
					leftDiv = "<div id='gearLeft'>"
					rightDiv = "<div id='gearRight'>"
					weaponDiv = "<div id='gearWeapon'>"

					parsedItems = []
					for slot, item in topSim["equippedGear"].items():
						itemDict = {"slot": slot}
						for itemProperty in item.split(","):
							if "=" in itemProperty:
								prop = itemProperty.split("=")
								itemDict[prop[0]] = prop[1]
						if "id" not in itemDict:
							itemDict["id"] = "0"
						parsedItems.append(itemDict)

					allGearIds = [item["id"] for item in parsedItems]

					for item in parsedItems:
						slot = item["slot"]
						link = "http://www.wowhead.com/"

						wowHeadKey = ["item=%s" % item["id"], "pcs=%s" % (":".join(allGearIds))]
						if "bonus_id" in item:
							wowHeadKey.append("bonus=%s" % item["bonus_id"].replace("/", ":"))
						if "gem_id" in item:
							wowHeadKey.append("gems=%s" % item["gem_id"].replace("/", ":"))
						if "enchant_id" in item:
							wowHeadKey.append("ench=%s" % item["enchant_id"])

						url = "%s%s" % (link, "&".join(wowHeadKey))
						link = "<a href='%s' rel='%s'>%s</a>" % (url, "&".join(wowHeadKey), item["id"])

						divContents = "<div class='gear %s'><div class='slot'>%s</div><div class='item'>%s</div></div>" % (slot, slot.upper(), link)
						if item["id"] == "0":
							divContents = "<div class='gear %s'><div class='slot'>%s</div><div class='item'>&nbsp;</div></div>" % (slot, slot.upper())

						if slot in leftSlots:
							leftDiv += divContents
						elif slot in rightSlots:
							rightDiv += divContents
						else:
							weaponDiv += divContents

					scaleFactors = ""
					if "scaleFactors" in topSim:
						scaleFactors += "<div id='scaleFactors'><div class='header'>Stat Weights</div>"
						for scaleFactor in sorted(topSim["scaleFactors"].items(), key=lambda x:float(x[1]), reverse=True):
							scaleFactors += "<div class='scale'><div class='scaleAttribute'>%s</div><div class='scaleValue'>%s</div></div>" % (scaleFactor[0], scaleFactor[1].replace("(", " ("))
						scaleFactors += "</div>"

					stats = ""
					if "stats" in topSim:
						stats += "<div id='stats'><div class='header'>Stats</div>"
						for statCategory in topSim["stats"]:
							stats += "<div class='statCategory'><div class='statCategoryHeader'>%s</div>" % statCategory
							stats+= "<div class='stat'><div class='statName'></div><div class='statBuffed statCol'>Raid Buffed</div><div class='statUnbuffed statCol'>Unbuffed</div></div>"
								
							for stat in topSim["stats"][statCategory]:
								stats += "<div class='stat'>"
								stats+= "<div class='statName'>%s</div>" % (stat)
								stats += "<div class='statBuffed'>%s</div><div class='statUnbuffed'>%s</div>" % (topSim["stats"][statCategory][stat]["buffed"], topSim["stats"][statCategory][stat]["unbuffed"])
								stats += "</div>"
							stats += "</div>"
						stats += "</div>"

					leftDiv += "</div>"
					rightDiv += "</div>"
					weaponDiv += "</div>"
					resultsString += "<div id='gear'><div class='header'>Gear</div>"
					resultsString += leftDiv
					resultsString += rightDiv
					resultsString += weaponDiv
					resultsString += "</div>"
					resultsString += scaleFactors
					resultsString += stats
					resultsString += "</div>\n"
				navString += "</ul>"
		index = indexTemplate.read()
		index = index.replace("$navString", navString)
		index = index.replace("$resultsString", resultsString)
		with open(outputIndexName, 'w') as output:
			output.write(index)
	return outputIndexName

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
	else:
		print(config["Sim"]["fightstyle"])
		config["Sim"]["fightstyle"] = config["Sim"]["fightstyle"].replace(" ", "")
		print(config["Sim"]["fightstyle"])

	if config.has_option("Sim", "enemies"):
		config["Sim"]["enemies"] = config["Sim"]["enemies"].replace(" ", "")
		for enemies in config["Sim"]["enemies"].split(","):
			try:
				if int(enemies) <= 0:
					print("WARN: Skill option not a valid number greater than 0. Defaulting to unspecified.")
					config.remove_option("Sim","enemies")
			except Exception:
				print("WARN: Enemies option not a valid number. Defaulting to unspecified.")
				config.remove_option("Sim","enemies")

	if not config.has_option("Sim", "metric"):
		config["Sim"]["metric"] = "dps"
		print("INFO: Defaulting to optimizing %s." % config["Sim"]["metric"])\

	if not config.has_option("Sim", "statweights"):
		config["Sim"]["statweights"] = "0"
		print("INFO: Defaulting to not calculating stat weights.")
	elif config["Sim"]["statweights"] != "0" and config["Sim"]["statweights"] != "1":
		config["Sim"]["statweights"] = "0"
		print("INFO: Invalid statweight option. Defaulting to not calculating stat weights.")

	if not config.has_option("Profile", "skill"):
		config["Profile"]["skill"] = "100"
		print("INFO: Defaulting to elite (100).")
	else:
		try:
			if int(config["Profile"]["skill"]) <= 0 or int(config["Profile"]["skill"]) > 100:
				config["Profile"]["skill"] = "100"
				print("WARN: Skill option not a valid number between 1 and 100. Defaulting to elite (100).")
		except Exception:
			config["Profile"]["skill"] = "100"
			print("WARN: Skill option not a valid number. Defaulting to elite (100).")

	# extend the acronym because simc is stupid
	if config["Sim"]["metric"] == "theck_meloree_index":
		config["Sim"]["metric"] = "tmi"

	validMetrics = ["dps", "prioritydps", "dpse", "hps", "dtps", "theck_meloree_index", "tmi"]
	if config["Sim"]["metric"] not in validMetrics:
		print("Unknown metric value (%s) in config file. Valid Metrics are one of: %s" % (config["Sim"]["metric"], validMetrics))
		sys.exit(98)

	if config.has_option("Profile", "talents"):
		if config["Profile"]["talents"].lower() == "all":
			config["Profile"]["talents"] = allTalents()
		else:
			print(config["Profile"]["talents"])
			config["Profile"]["talents"] = config["Profile"]["talents"].replace(" ", "")
			print(config["Profile"]["talents"])
			for talent in config["Profile"]["talents"].split(","):
				if len(talent) != 7 or not talent.isnumeric() or len([x for x in talent if (not x.isdigit() or int(x) not in [1,2,3])]) != 0:
					print("Invalid talents supplied: %s" % (config["Profile"]["talents"]))
					sys.exit(97)


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

def checkVersion():
	try:
		localVersion = open("VERSION").read().rstrip()
		remoteVersion = urllib.request.urlopen("https://raw.githubusercontent.com/tiberiuslazarus/ExtraAutoSimC/master/VERSION").read().rstrip().decode("utf-8")

		if remoteVersion != localVersion:
			print("--WARN: Your local version (%s) does not match the remote version (%s). Consider updating from: https://github.com/tiberiuslazarus/ExtraAutoSimC/archive/master.zip" % (localVersion, remoteVersion))
	except:
		print("--WARN: Unable to verify version information.")

if __name__ == "__main__":
	start_time = time.time()
	main()
	timeSeconds = (time.time() - start_time)
	m, s = divmod(timeSeconds, 60)
	print("--- Full execution in %s:%s ---" % ('{0:02d}'.format(int(m)), "{0:04.1f}".format(s)))

from generate import *
from simulate import *
from analyze import *

import configparser
import sys
import time
import tempfile

def main():
	cleanTempDir()
	config = loadConfig()
	print("Performing gear comparisons for %s on Fight Styles: %s" % (config["Profile"]["profilename"], config["Sim"]["fightstyle"]))
	print("Using %s threads" % config["Sim"]["maxthreads"])
	print()

	generatedGear = generateGear(config["Gear"])

	metric = config["Sim"]["metric"]
	statWeights = config["Sim"]["statWeights"]
	htmlOutputs = {}
	topSims = {}

	for fightStyle in config["Sim"]["fightstyle"].split(","):
		simInputs = []
		topSims[fightStyle] = getTopSims(fightStyle, generatedGear["valid"], config["Profile"], config["Sim"]["maxthreads"], metric, statWeights)

	for fightStyle, fightTopSims in topSims.items():
		print("---Best %s %s for %s results available at:---" % (len(fightTopSims), metric, fightStyle))
		for i in range(len(fightTopSims)):
			print("%s: %s (%s +/- %s) (Talents: %s)" %
			 (i+1, fightTopSims[i]["htmlOutput"],
			  "{:.1f}".format(fightTopSims[i][metric]),
			  "{:.1f}".format(fightTopSims[i]["error"]),
			  fightTopSims[i]["configProfile"]["talentset"]))
		print("-------")
		print()

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

	if not config.has_option("Sim", "metric"):
		config["Sim"]["metric"] = "dps"
		print("INFO: Defaulting to optimizing %s." % config["Sim"]["metric"])\

	if not config.has_option("Sim", "statWeights"):
		config["Sim"]["statWeights"] = "0"
		print("INFO: Defaulting to not calculating stat weights.")
	elif config["Sim"]["statWeights"] != "0" or config["Sim"]["statWeights"] != "1":
		config["Sim"]["statWeights"] = "0"
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

def cleanTempDir():
	print("Cleaning temporary directory")
	with os.scandir(tempfile.gettempdir()) as tempDir:
		for entry in tempDir:
			if entry.is_file() and (entry.name.startswith("easc_") or (entry.name.endswith('.html') or entry.name.endswith('.json') or entry.name.endswith('.simc'))):
				try:
					os.remove(entry)
				except:
					pass
	print("Done cleaning temporary directory")


if __name__ == "__main__":
	start_time = time.time()
	main()
	timeSeconds = (time.time() - start_time)
	m, s = divmod(timeSeconds, 60)
	print("--- Full execution in %s:%s ---" % ('{0:02d}'.format(int(m)), "{0:04.1f}".format(s)))

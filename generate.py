import sys
import time
import logging
logger = logging.getLogger(__name__)

def generateGear(availableGear):
	logger.debug("started generateGear()")
	generateStartTime = time.time()
	print("---Generating profiles from gear options---")

	# standardize gear names
	if availableGear["shoulder"]:
		availableGear["shoulders"] = availableGear["shoulder"]
	if availableGear["wrist"]:
		availableGear["wrists"] = availableGear["wrist"]
	if not availableGear.get("off_hand"):
		availableGear["off_hand"] = ""

	### Split vars to lists ###
	gearOptions={}
	for slot, slotOptions in availableGear.items():
		gearOptions[slot]=slotOptions.split("|")

	generatedGear = iterateGear(gearOptions)

	valid = len(generatedGear["valid"])
	invalid = generatedGear["invalid"]

	print("%s Gear possibilities" % (valid + invalid))
	print("Invalid gear combinations: %s" % invalid)
	print("Valid gear combinations: %s" % valid)
	print("--- Profiles generated in %s seconds ---" % (format(time.time() - generateStartTime, "0.1f")))
	print()

	return generatedGear

def iterateGear(gearOptions):
	logger.debug("started iterateGear()")
	equippedGear = {}
	gearProfiles = {"valid": [], "invalid": 0}

	for headSlotOption in gearOptions["head"]:
		equippedGear["head"] = headSlotOption
		for neckSlotOption in gearOptions["neck"]:
			equippedGear["neck"] = neckSlotOption
			for shouldersSlotOption in gearOptions["shoulders"]:
				equippedGear["shoulders"] = shouldersSlotOption
				for backSlotOption in gearOptions["back"]:
					equippedGear["back"] = backSlotOption
					for chestSlotOption in gearOptions["chest"]:
						equippedGear["chest"] = chestSlotOption
						for wristsSlotOption in gearOptions["wrists"]:
							equippedGear["wrists"] = wristsSlotOption
							for handsSlotOption in gearOptions["hands"]:
								equippedGear["hands"] = handsSlotOption
								for waistSlotOption in gearOptions["waist"]:
									equippedGear["waist"] = waistSlotOption
									for legsSlotOption in gearOptions["legs"]:
										equippedGear["legs"] = legsSlotOption
										for feetSlotOption in gearOptions["feet"]:
											equippedGear["feet"] = feetSlotOption
											# Reset equipped rings as we are about to start a new iteration of them
											prevRings = []
											for finger1Option in gearOptions["finger1"]:
												equippedGear["finger1"] = finger1Option
												prevRings.append(finger1Option)
												for finger2Option in [x for x in gearOptions["finger2"] if x not in prevRings]:
													equippedGear["finger2"] = finger2Option
													# Reset equipped trinkets as we are about to start a new iteration of them
													prevTrinkets = []
													for trinket1Option in gearOptions["trinket1"]:
														equippedGear["trinket1"] = trinket1Option
														prevTrinkets.append(trinket1Option)
														for trinket2Option in [x for x in gearOptions["trinket2"] if x not in prevTrinkets]:
															equippedGear["trinket2"] = trinket2Option
															for main_handSlotOption in gearOptions["main_hand"]:
																equippedGear["main_hand"] = main_handSlotOption
																for off_handSlotOption in gearOptions["off_hand"]:
																	equippedGear["off_hand"] = off_handSlotOption
																	if usable(equippedGear):
																		gearProfiles["valid"].append(equippedGear.copy())
																	else:
																		gearProfiles["invalid"] += 1

	return gearProfiles

def generateGearProfile(outputFileName, equippedGear, configProfile, enemies):
	logger.debug("started generateGearProfile()")
	gearProfile = []
	gearProfile.append("%s=%s_%s" % (configProfile["class"], configProfile["profilename"], outputFileName))
	gearProfile.append("specialization=%s" % (configProfile["spec"]))
	gearProfile.append("race=%s" % (configProfile["race"]))
	gearProfile.append("level=%s" % (configProfile["level"]))
	gearProfile.append("role=%s" % (configProfile["role"]))
	gearProfile.append("position=%s" % (configProfile["position"]))
	gearProfile.append("talents=%s" % (configProfile["talentset"]))
	gearProfile.append("artifact=%s" % (configProfile["artifact"]))
	gearProfile.append("skill=%s" % (float(configProfile["skill"]) / 100))

	for slot, gear in equippedGear.items():
		if gear != "":
			gearProfile.append("%s=%s" % (slot, (gear if gear[0]!="L" else gear[1:])))

	try:
		for i in range(int(enemies)):
			gearProfile.append("enemy=enemy_%s" % i)
	except:
		pass

	return gearProfile

def usable(equippedGear):
	logger.debug("started usable()")
	legmax=2
	nbLeg=0

	for slotGear in equippedGear:
		if equippedGear[slotGear] != "" and equippedGear[slotGear][0]=="L":
			nbLeg=nbLeg+1
	if nbLeg > legmax:
		return False
	elif equippedGear["finger1"]==equippedGear["finger2"]:
		return False
	elif equippedGear["trinket1"]==equippedGear["trinket2"]:
		return False
	else:
		return True

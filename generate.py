import sys
import time

def generateProfiles(config):
    generateStartTime = time.time()
    print("Generating profiles from gear options...")
    gear = config["Gear"]

    # standardize gear names
    if config.has_option("Gear", "shoulder"):
        gear["shoulders"] = gear["shoulder"]
    if config.has_option("Gear", "wrist"):
        gear["wrists"] = gear["wrist"]
    if not config.has_option("Gear", "off_hand"):
        gear["off_hand"] = ""

    ### Split vars to lists ###
    gearOptions={}
    for slot, slotOptions in gear.items():
        gearOptions[slot]=slotOptions.split("|")

    equippedGear = {}
    gearSlots = ["head","neck","shoulder","back","chest","wrist","hands","waist","legs","feet","finger1","finger2","trinket1","trinket2"]

    generatedProfiles = iterateGear(gearOptions, gearSlots, equippedGear, config)

    valid = 0
    invalid = 0

    for fightStyle in generatedProfiles:
        valid += len(generatedProfiles[fightStyle]["valid"])
        invalid += generatedProfiles[fightStyle]["invalid"]
    print("%s Gear possibilities across %s fight styles" % (valid + invalid, len(generatedProfiles)))
    print("Invalid gear combinations: %s" % invalid)
    print("Valid gear combinations: %s" % valid)
    print("--- Profiles generated in %s seconds ---" % (time.time() - generateStartTime))
    print()

    return generatedProfiles

def iterateGear(gearOptions, gearSlots, equippedGear, config):
    gearSlots = ["head","neck","shoulders","back","chest","wrists","hands","waist","legs","feet","finger1","finger2","trinket1","trinket2","main_hand","off_hand"]
    slot = gearSlots.pop()
    profileId=1

    profiles = {}
    fightStyles = config["Profile"]["fightstyle"].split(",")
    for fightStyle in fightStyles:
        profiles[fightStyle] = {"valid": [], "invalid": 0}

    equippedRings = []
    equippedTrinkets = []

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
                                            for finger1Option in gearOptions["finger1"]:
                                                equippedGear["finger1"] = finger1Option
                                                equippedRings.append(finger1Option)
                                                for finger2Option in gearOptions["finger2"]:
                                                    if (finger2Option in equippedRings):
                                                        continue
                                                    equippedGear["finger2"] = finger2Option
                                                    for trinket1Option in gearOptions["trinket1"]:
                                                        equippedGear["trinket1"] = trinket1Option
                                                        equippedTrinkets.append(trinket1Option)
                                                        for trinket2Option in gearOptions["trinket2"]:
                                                            if (finger2Option in equippedTrinkets):
                                                                continue
                                                            equippedGear["trinket2"] = trinket2Option
                                                            for main_handSlotOption in gearOptions["main_hand"]:
                                                                equippedGear["main_hand"] = main_handSlotOption
                                                                for off_handSlotOption in gearOptions["off_hand"]:
                                                                    equippedGear["off_hand"] = off_handSlotOption
                                                                    for fightStyle in fightStyles:
                                                                        generatedProfile = generateProfile(profileId, equippedGear, config)
                                                                        if (generatedProfile != ""):
                                                                            profiles[fightStyle]["valid"].append((fightStyle, generatedProfile))
                                                                            profileId += 1
                                                                        else:
                                                                            profiles[fightStyle]["invalid"] += 1
    return profiles

### Function to generate a simc profile ###
def generateProfile(profileId, equippedGear, config):
    result = checkUsability(equippedGear)
    if result!="":
        return ""
    else:
        configProfile = config["Profile"]
        profileIdStr = getProfileIdStr(configProfile["profilename"], profileId)
        profileFile=open("profiles\\%s.simc" % profileIdStr, "w")

        profileFile.write("%s=%s_%s\n" % (configProfile["class"], configProfile["profilename"], profileIdStr))
        profileFile.write("specialization=%s\n" % (configProfile["spec"]))
        profileFile.write("race=%s\n" % (configProfile["race"]))
        profileFile.write("level=%s\n" % (configProfile["level"]))
        profileFile.write("role=%s\n" % (configProfile["role"]))
        profileFile.write("position=%s\n" % (configProfile["position"]))
        profileFile.write("talents=%s\n" % (configProfile["talents"]))
        profileFile.write("artifact=%s\n" % (configProfile["artifact"]))

        for slot, gear in equippedGear.items():
            profileFile.write("%s=%s\n" % (slot, (gear if gear[0]!="L" else gear[1:])))

        profileFile.close()

        return profileIdStr


#check if permutation is valid
def checkUsability(equippedGear):
    # print(equippedGear)
    if len(sys.argv) == 3:
        legmax=int(sys.argv[2])
    else:
        legmax=2
    nbLeg=0
    for slotGear in equippedGear:
        if equippedGear[slotGear][0]=="L":
            nbLeg=nbLeg+1
    if nbLeg>legmax:
        return "Too many legendaries (%s)" % nbLeg
    elif equippedGear["finger1"]==equippedGear["finger2"]:
        return "Duplicate ring equipped"
    elif equippedGear["trinket1"]==equippedGear["trinket2"]:
        return "Duplicate trinket equipped"
    else:
        return ""

def getProfileIdStr(profilename, profileId):
    return "%s_%s" % (profilename, str(profileId).zfill(6))

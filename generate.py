import sys
import time

def generateGear(config):
    generateStartTime = time.time()
    print("Generating profiles from gear options...")
    availableGear = config["Gear"]

    # standardize gear names
    if availableGear["shoulder"]:
        availableGear["shoulders"] = availableGear["shoulder"]
    if availableGear["wrist"]:
        availableGear["wrists"] = availableGear["wrist"]
    if not availableGear["off_hand"]:
        availableGear["off_hand"] = ""

    ### Split vars to lists ###
    gearOptions={}
    for slot, slotOptions in availableGear.items():
        gearOptions[slot]=slotOptions.split("|")

    generatedGear = iterateGear(gearOptions, config)

    valid = 0
    invalid = 0

    for fightStyle in generatedGear:
        valid += len(generatedGear[fightStyle]["valid"])
        invalid += generatedGear[fightStyle]["invalid"]
    print("%s Gear possibilities across %s fight styles" % (valid + invalid, len(generatedGear)))
    print("Invalid gear combinations: %s" % invalid)
    print("Valid gear combinations: %s" % valid)
    print("--- Profiles generated in %s seconds ---" % (time.time() - generateStartTime))
    print()

    return generatedGear

def iterateGear(gearOptions, config):
    gearProfiles = {}
    fightStyles = config["Sim"]["fightstyle"].split(",")
    equippedGear = {}
    for fightStyle in fightStyles:
        gearProfiles[fightStyle] = {"valid": [], "invalid": 0}

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
                                            equippedRings = []
                                            for finger1Option in gearOptions["finger1"]:
                                                equippedGear["finger1"] = finger1Option
                                                equippedRings.append(finger1Option)
                                                for finger2Option in gearOptions["finger2"]:
                                                    if (finger2Option in equippedRings):
                                                        continue
                                                    equippedGear["finger2"] = finger2Option
                                                    # Reset equipped trinkets as we are about to start a new iteration of them
                                                    equippedTrinkets = []
                                                    for trinket1Option in gearOptions["trinket1"]:
                                                        equippedGear["trinket1"] = trinket1Option
                                                        equippedTrinkets.append(trinket1Option)
                                                        for trinket2Option in gearOptions["trinket2"]:
                                                            if (trinket2Option in equippedTrinkets):
                                                                continue
                                                            equippedGear["trinket2"] = trinket2Option
                                                            for main_handSlotOption in gearOptions["main_hand"]:
                                                                equippedGear["main_hand"] = main_handSlotOption
                                                                for off_handSlotOption in gearOptions["off_hand"]:
                                                                    equippedGear["off_hand"] = off_handSlotOption
                                                                    for fightStyle in fightStyles:
                                                                        if usable(equippedGear):
                                                                            gearProfiles[fightStyle]["valid"].append(equippedGear)
                                                                        else:
                                                                            gearProfiles[fightStyle]["invalid"] += 1
    return gearProfiles

### Function to generate a simc profile ###

def generateGearProfile(outputFileName, equippedGear, configProfile):
    gearProfile = ""
    gearProfile += "%s=%s_%s\n" % (configProfile["class"], configProfile["profilename"], outputFileName)
    gearProfile += "specialization=%s\n" % (configProfile["spec"])
    gearProfile += "race=%s\n" % (configProfile["race"])
    gearProfile += "level=%s\n" % (configProfile["level"])
    gearProfile += "role=%s\n" % (configProfile["role"])
    gearProfile += "position=%s\n" % (configProfile["position"])
    gearProfile += "talents=%s\n" % (configProfile["talents"])
    gearProfile += "artifact=%s\n" % (configProfile["artifact"])

    for slot, gear in equippedGear.items():
        gearProfile += "%s=%s\n" % (slot, (gear if gear[0]!="L" else gear[1:]))

    return gearProfile


def generateGearProfileOld(outputFile, equippedGear, configProfile):
    outputFile.write("%s=%s_%s\n" % (configProfile["class"], configProfile["profilename"], outputFile.name))
    outputFile.write("specialization=%s\n" % (configProfile["spec"]))
    outputFile.write("race=%s\n" % (configProfile["race"]))
    outputFile.write("level=%s\n" % (configProfile["level"]))
    outputFile.write("role=%s\n" % (configProfile["role"]))
    outputFile.write("position=%s\n" % (configProfile["position"]))
    outputFile.write("talents=%s\n" % (configProfile["talents"]))
    outputFile.write("artifact=%s\n" % (configProfile["artifact"]))

    for slot, gear in equippedGear.items():
        outputFile.write("%s=%s\n" % (slot, (gear if gear[0]!="L" else gear[1:])))

#check if permutation is valid
def usable(equippedGear):
    # print(equippedGear)
    legmax=2

    nbLeg=0
    for slotGear in equippedGear:
        if equippedGear[slotGear][0]=="L":
            nbLeg=nbLeg+1
    if nbLeg>legmax or equippedGear["finger1"]==equippedGear["finger2"] or equippedGear["trinket1"]==equippedGear["trinket2"]:
        return False
    else:
        return True

def getProfileIdStr(profilename, profileId):
    return "%s_%s" % (profilename, str(profileId).zfill(6))

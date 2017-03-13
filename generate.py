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

    profiles = iterateGear(gearOptions, gearSlots, equippedGear, config["player"])

    print("Gear possibilities: %s" % (len(profiles["valid"]) + len(profiles["invalid"])))
    print("Invalid gear combinations: %s" % len(profiles["invalid"]))
    print("Valid gear combinations: %s" % len(profiles["valid"]))
    print("--- Profiles generated in %s seconds ---" % (time.time() - generateStartTime))
    return profiles

def iterateGear(gearOptions, gearSlots, equippedGear, player):
    gearSlots = ["head","neck","shoulders","back","chest","wrists","hands","waist","legs","feet","finger1","finger2","trinket1","trinket2","main_hand","off_hand"]
    slot = gearSlots.pop()
    profileId=1
    profiles = {"valid": [], "invalid": []}
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
                                                for finger2Option in gearOptions["finger2"]:
                                                    equippedGear["finger2"] = finger2Option
                                                    for trinket1Option in gearOptions["trinket1"]:
                                                        equippedGear["trinket1"] = trinket1Option
                                                        for trinket2Option in gearOptions["trinket2"]:
                                                            equippedGear["trinket2"] = trinket2Option
                                                            for main_handSlotOption in gearOptions["main_hand"]:
                                                                equippedGear["main_hand"] = main_handSlotOption
                                                                for off_handSlotOption in gearOptions["off_hand"]:
                                                                    equippedGear["off_hand"] = off_handSlotOption
                                                                    profileIdStr = getProfileIdStr(player['profilename'], profileId)
                                                                    if (generateProfile(profileId, equippedGear, player)):
                                                                        profiles["valid"].append(profileIdStr)
                                                                        profileId += 1
                                                                    else:
                                                                        profiles["invalid"].append(profileIdStr)
    return profiles

### Function to generate a simc profile ###
def generateProfile(profileId, equippedGear, player):
    result = checkUsability(equippedGear)
    profileIdStr = getProfileIdStr(player["profilename"], profileId)
    if result!="":
        return False
    else:
        # print(profileId)
        profileFile=open("profiles\\%s.simc" % profileIdStr, "w")

        profileFile.write(player["class"]+"="+player["profilename"]+"_"+profileIdStr+"\n")
        profileFile.write("specialization="+player["spec"]+"\n")
        profileFile.write("race="+player["race"]+"\n")
        profileFile.write("level="+player["level"]+"\n")
        profileFile.write("role="+player["role"]+"\n")
        profileFile.write("position="+player["position"]+"\n")
        profileFile.write("talents="+player["talents"]+"\n")
        profileFile.write("artifact="+player["artifact"]+"\n")

        for slot, gear in equippedGear.items():
            profileFile.write("%s=%s\n" % (slot, (gear if gear[0]!="L" else gear[1:])))

        profileFile.close()
        return True


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

import sys
import time
import logging
import configparser
logger = logging.getLogger()

class Gear:
    simResults = None
    availableGear = None

    def __init__(self, availableGear):
        # print(type(availableGear))
        if len(availableGear) > 0 and not isinstance(availableGear, configparser.SectionProxy) :
            self.simResults = availableGear
            self.countPossibleGear()
        else:
            if availableGear["shoulder"]:
                availableGear["shoulders"] = availableGear["shoulder"]
            if availableGear["wrist"]:
                availableGear["wrists"] = availableGear["wrist"]
            if not availableGear.get("off_hand"):
                availableGear["off_hand"] = ""

            self.gearOptions = {}
            for slot, slotOptions in availableGear.items():
                self.gearOptions[slot]=slotOptions.split("|")
            self.countPossibleGear()

            self.availableGear = availableGear

    def countPossibleGear(self):
        if self.simResults:
            self.possibleGear = len(self.simResults)
        else:
            possibleGear = 0
            for key in self.gearOptions.keys():
                if possibleGear == 0:
                    possibleGear = len(self.gearOptions[key])
                else:
                    possibleGear *= len(self.gearOptions[key])
            self.possibleGear = possibleGear

    def getPossibleCount(self):
        return self.possibleGear

    def getGear(self, gearQueue, talentSets):
        if self.simResults:
            for result in self.simResults:
                # print(result)
                gearQueue.put((result["equippedGear"], result["configProfile"]["talentset"]))
        else:
            equippedGear = {}

            for talentSet in talentSets:
                if talentSet == "":
                    continue
                for headSlotOption in self.gearOptions["head"]:
                    equippedGear["head"] = headSlotOption
                    for neckSlotOption in self.gearOptions["neck"]:
                        equippedGear["neck"] = neckSlotOption
                        for shouldersSlotOption in self.gearOptions["shoulders"]:
                            equippedGear["shoulders"] = shouldersSlotOption
                            for backSlotOption in self.gearOptions["back"]:
                                equippedGear["back"] = backSlotOption
                                for chestSlotOption in self.gearOptions["chest"]:
                                    equippedGear["chest"] = chestSlotOption
                                    for wristsSlotOption in self.gearOptions["wrists"]:
                                        equippedGear["wrists"] = wristsSlotOption
                                        for handsSlotOption in self.gearOptions["hands"]:
                                            equippedGear["hands"] = handsSlotOption
                                            for waistSlotOption in self.gearOptions["waist"]:
                                                equippedGear["waist"] = waistSlotOption
                                                for legsSlotOption in self.gearOptions["legs"]:
                                                    equippedGear["legs"] = legsSlotOption
                                                    for feetSlotOption in self.gearOptions["feet"]:
                                                        equippedGear["feet"] = feetSlotOption
                                                        # Reset equipped rings as we are about to start a new iteration of them
                                                        prevRings = []
                                                        for finger1Option in self.gearOptions["finger1"]:
                                                            equippedGear["finger1"] = finger1Option
                                                            prevRings.append(finger1Option)
                                                            # for finger2Option in [x for x in self.gearOptions["finger2"] if x not in prevRings]:
                                                            for finger2Option in self.gearOptions["finger2"]:
                                                                equippedGear["finger2"] = finger2Option
                                                                # Reset equipped trinkets as we are about to start a new iteration of them
                                                                prevTrinkets = []
                                                                for trinket1Option in self.gearOptions["trinket1"]:
                                                                    equippedGear["trinket1"] = trinket1Option
                                                                    prevTrinkets.append(trinket1Option)
                                                                    for trinket2Option in self.gearOptions["trinket2"]:
                                                                        equippedGear["trinket2"] = trinket2Option
                                                                        for main_handSlotOption in self.gearOptions["main_hand"]:
                                                                            equippedGear["main_hand"] = main_handSlotOption
                                                                            for off_handSlotOption in self.gearOptions["off_hand"]:
                                                                                equippedGear["off_hand"] = off_handSlotOption
                                                                                if self.usable(equippedGear) and finger2Option not in prevRings and trinket2Option not in prevTrinkets:
                                                                                    gearQueue.put((equippedGear.copy(), talentSet))
                                                                                else:
                                                                                    gearQueue.put(False)

    def usable(self, equippedGear):
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

import os
import time
import json
import heapq
from operator import itemgetter
from multiprocessing import Pool

def processFile(profileId):
    with open("output\\json\\%s.json" % profileId, "r") as simFile:
        simInfo = json.load(simFile)
        return (simInfo["sim"]["players"][0]["collected_data"]["dps"]["mean"],profileId)

def analyzeSims(profiles):
    analysisStartTime = time.time()
    dpsList = Pool().map(processFile, profiles)

    return [dpsTuple for dpsTuple in heapq.nlargest(5,dpsList,key=itemgetter(0))]

if __name__ == "__main__":
    outputFiles = os.listdir(".\\output\\json")
    profiles = []
    for filename in outputFiles:
        profiles.append(os.path.splitext(filename)[0])
    analyzeSims(profiles)

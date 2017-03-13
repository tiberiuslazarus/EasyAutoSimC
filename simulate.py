import multiprocessing
import time
import sys
import subprocess
import os
from analyze import *

simResults = []

def generateHtmlProfiles(profiles):
    runSimsSingleThread(profiles, "html")


def runSims(profiles, maxthreads):
    completedProfiles = 0
    totalProfiles = len(profiles)
    topDps = []
    lastTime = time.time()
    while (len(profiles) > 0):
        batchSize=min(100, len(profiles))
        batchProfiles = profiles[:batchSize]
        del profiles[:batchSize]

        if (int(maxthreads) > 1):
            runSimsMultitThread(batchProfiles, maxthreads)
        else:
            runSimsSingleThread(batchProfiles, "json")

        topDps.extend(analyzeSims(batchProfiles))
        topDps = [dpsTuple for dpsTuple in heapq.nlargest(5,topDps,key=itemgetter(0))]

        for profileId in batchProfiles:
            os.remove("output\\json\\%s.json" % profileId)

        completedProfiles += batchSize
        print("%s of %s profiles completed." % (completedProfiles, totalProfiles))
        print("Last %s profiles simmed in %s seconds" % (batchSize, time.time() - lastTime))
        lastTime = time.time()
    return topDps

def runSimsSingleThread(profiles, outputType):
    print("Simming profiles...")
    for profileId in profiles:
        runSim(profileId, outputType)

def runSimsMultitThread(profiles, maxthreads):
    simStartTime = time.time()
    lastTime = simStartTime
    print("Simming profiles...")
    pool = multiprocessing.Pool(int(maxthreads));
    completedProfiles = 0
    try:
        pool.map(runSim, profiles)
        pool.close()
    except KeyboardInterrupt:
        # **** THIS PART NEVER EXECUTES. ****
        pool.terminate()
        print("Simming cancelled by user after %s profiles" % completedProfiles)
        sys.exit(1)
    except Exception as e:
        pool.terminate()
        print('Simming cancelled by exception: %r, terminating.' % e)
        sys.exit(2)
    finally:
        pool.join()

def runSim(profileId, outputType="json"):
    output = "%s=output\\%s\\%s.%s" % (outputType, outputType, profileId, outputType)
    inputFile = "profiles\\%s.simc" % profileId
    subprocess.check_call(["..\\simc.exe", inputFile, output, "threads=1"], stdout=open(os.devnull, 'wb'))

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
    # maxthreads = config["Sim"]["maxthreads"]

    while (len(profiles) > 0):
        batchSize=min(100, len(profiles))
        batchProfiles = profiles[:batchSize]
        del profiles[:batchSize]

        if (int(maxthreads) > 1):
            runSimsMultiThread(batchProfiles, maxthreads)
        else:
            runSimsSingleThread(batchProfiles, "json")

        topDps.extend(analyzeSims(batchProfiles, maxthreads))
        topDps = [dpsTuple for dpsTuple in heapq.nlargest(5,topDps,key=itemgetter(2))]

        # for fightStyle, profileId in batchProfiles:
        #     os.remove("output\\json\\%s_%s.json" % (fightStyle, profileId))

        completedProfiles += batchSize
        print("%s of %s profiles completed." % (completedProfiles, totalProfiles))
        print("Last %s profiles simmed in %s seconds" % (batchSize, time.time() - lastTime))
        print()
        lastTime = time.time()
    return topDps

def runSimsSingleThread(profiles, outputType):
    for fightStyle, profileId in profiles:
        runSim(fightStyle, profileId, outputType)

def runSimsMultiThread(profiles, maxthreads):
    simStartTime = time.time()
    lastTime = simStartTime
    pool = multiprocessing.Pool(int(maxthreads));
    completedProfiles = 0
    try:
        pool.starmap(runSim, profiles)
        pool.close()
    except KeyboardInterrupt:
        # **** THIS PART NEVER EXECUTES. ****
        pool.terminate()
        print("---Simming cancelled by user after %s profiles---" % completedProfiles)
        sys.exit(1)
    except Exception as e:
        pool.terminate()
        print('---Simming cancelled by exception: %r, terminating---' % e)
        sys.exit(2)
    finally:
        pool.join()

def runSim(fightStyle, profileId, outputType="json"):
    output = "%s=output\\%s\\%s_%s.%s" % (outputType, outputType, fightStyle, profileId, outputType)
    inputFile = "profiles\\%s.simc" % profileId
    subprocess.check_call(["..\\simc.exe", inputFile, output, "threads=1", "fight_style=%s" % fightStyle], stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))

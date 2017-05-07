import os
import time
import json
import heapq
import re
from operator import itemgetter
from multiprocessing import Pool

def processOutput(simcOutput, metric):
	for line in simcOutput.split("\n"):
		if "%s:" % metric.upper() in line:
			vals = re.findall("\d+\.?\d*", line)
			return (float(vals[0]), float(vals[1]))

	print("WARN: Metric not found in simc output. This is weird...")
	# print("WARN: Simc Output")
	# print(simcOutput)
	# print("WARN: End Simc Output")
	return (0,0)

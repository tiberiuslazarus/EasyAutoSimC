ExtraAutoSimC
========

System to generate gearing options from owned items for WoW characters and then feed them to SimulationCraft to provide optimal gear choices. Heavily based off of AutoSimC (https://github.com/SimCMinMax/AutoSimC)

Created to work in Python3. Maybe 2? Idk.

********VERY EXPERIMENTAL. DO NOT MAKE ANY PERMANENT GEAR DECISIONS BASED ON THIS OUTPUT.********



SimC Verison
----
simc-715-02-win64-13c760b



Usage
----
1) Run: `launch.bat` *or* from command line: `python main.py`

2) Enter name of a file containing an export of data in autosimc format from SimPermut (file name can also be passed as first argument on command line)

3) Html format results from SimC for the top 5 dps profiles will be saved in ./output/html/ . Open those to see what gear os equipped for that profile.


The system will attempt to spawn multiple threads for simming. If more than 2 CPUs are available this value will be ([# of CPUs] - 2), otherwise only 1 thread will perform sims.

This default can be overriden in a config file by adding the following:

```
[Sim]
maxthreads=#
```


Future
----
1) Cleaner output of gear for top profiles. Having to open separate html files kind of sucks.
2) Clean up simc profiles after execution. Currently if you run a large number of gear combinations a new file for each will be created and stay around in `.\profiles\` until after all sims are done.
3) Configuration options:
  to sim multiple fight types (patchwerk, heavy movement, cleave)
  to optimise for a different metric (DPS, DPS to Primary target in cleave fights, DTPS)

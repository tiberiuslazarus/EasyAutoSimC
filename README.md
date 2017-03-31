# ExtraAutoSimC (EASC)
---

System to generate gearing options from owned items for WoW characters and then feed them to [SimulationCraft](http://simulationcraft.org/) to provide optimal gear choices. Heavily based off of [AutoSimC](https://github.com/SimCMinMax/AutoSimC).

Created to work in Python3 on Windows 64bit. It is likely possible to replace the included simcraft/simc.exe file with a 32 bit. But that seems dumb.

*** VERY EXPERIMENTAL. DO NOT MAKE ANY PERMANENT GEAR DECISIONS BASED ON THIS OUTPUT ***


## SimC Verison

simc-720-01-win64-17969b1


## Usage

1) Export your gear options you would like to compare from [SimPermut](https://mods.curse.com/addons/wow/254069-simpermut) in AutoSimC format. Copy and paste the export to a file.

2) Run: `launch.bat` *or* from command line: `python main.py`

3) Enter the name of a file containing an export of data in autosimc format from SimPermut. Optionally the file name can be passed as the first argument on command line.

4) Html format results from SimC for the top 5 dps profiles will be saved in ./output/html/ . Open those to see what gear is equipped for that profile.


### CPU Usage

The system will attempt to spawn multiple threads for simming. If more than 2 CPUs are available this value will be ([# of CPUs] - 2), otherwise only 1 thread will perform sims. This default can be overridden in a config file by adding the following:

```
[Sim]
maxthreads=#
```


### Fight Styles

Fight styles can be configured and the top 5 dps for each fight style will be output.

```
[Sim]
fightstyle=HelterSkelter,Patchwerk,HecticAddCleave,Ultraxion,Beastlord
```


### Metric Optimization

```
[Sim]
metric=dps
```

Valid metric options:
 * dps
 * prioritydps
 * dpse
 * hps
 * dtps
 * dmg_taken
 * theck_meloree_index / tmi
 * effective_theck_meloree_index / etmi


## Future

* Cleaner output of gear for top profiles. Having to open separate html files to see the equipped gear kind of sucks and is not very Auto. -- * In process *
* ~~Clean up SimC profiles after execution~~ -- DONE
* Configuration options:
  * ~~to sim multiple fight types (patchwerk, heavy movement, cleave)~~ -- DONE
  * ~~to optimise for a different metric (DPS, DPS to Primary target in cleave fights, DTPS)~~ -- DONE
  * to compare talent sets as well as gear

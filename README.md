# ExtraAutoSimC (EASC)
---

System to generate gearing options from owned items for WoW characters and then feed them to [SimulationCraft](http://simulationcraft.org/) to provide optimal gear choices. Heavily inspired by and initially based off of [AutoSimC](https://github.com/SimCMinMax/AutoSimC).

Created to work in Python3 on Windows 64bit. It is likely possible to replace the included simcraft/simc.exe file with a 32 bit. But that seems dumb.

*** VERY EXPERIMENTAL. DO NOT MAKE ANY PERMANENT GEAR DECISIONS BASED ON THIS OUTPUT ***


## SimC Verison

simc-720-03-win64-8301cad


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

### Talents

Talent sets can be defined in your profile file. All fight styles will be simmed with all available talent sets. The top combinations of gear and talents will be returned.

```
[Profile]
talents=1111321
```

```
[Profile]
talents=1111321,1111111,2222222,3333333
```

Alternatively, may run sim against all possible talent combinations. This may take quite long time.

```
[Profile]
talents=all
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
 * theck_meloree_index / tmi

### Stat Weights

Calculate stat weights for top simming gear sets. This will likely add significant time to the final portion of your run.

```
[Sim]
statweights=1
```


### Player Skill

Set the skill level of the player in the sim. Accepts numbers 1-100.

SimC Equivalents:
 * Elite: 100
 * Good: 95
 * Average: 85
 * Ouch! Fire is hot!: 75

```
[Profile]
skill=100
```

## Future

* Cleaner output of gear for top profiles. Having to open separate html files to see the equipped gear kind of sucks and is not very Auto. -- * In process *
* ~~Clean up SimC profiles after execution~~ -- DONE
* Configuration options:
  * ~~Sim multiple fight types (patchwerk, heavy movement, cleave)~~ -- DONE
  * ~~Optimise for a different metric (DPS, DPS to Primary target in cleave fights, DTPS)~~ -- DONE
  * ~~Compare talent sets as well as gear~~ -- Done
  * ~~Player skill level~~
  * ~~Calculate stat weights for top simming gear sets~~
  * Plot stats for top simming gear sets
  * Modify food and potions. Possibly in the same vein as talents with ability to sim multiple/all?
* GUI of some sort

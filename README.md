# ExtraAutoSimC (EASC)
---

System to generate gearing options from owned items for WoW characters and then feed them to [SimulationCraft](http://simulationcraft.org/) to provide optimal gear choices. Heavily inspired by and initially based off of [AutoSimC](https://github.com/SimCMinMax/AutoSimC).

Created to work in Python3 on Windows 64bit. It is likely possible to replace the included simcraft/simc.exe file with a 32 bit. But that seems dumb.

*** MOSTLY EXPERIMENTAL. DO NOT MAKE ANY PERMANENT GEAR DECISIONS BASED ON THIS OUTPUT ***


## Quick Start

1) Download and install [python for 64 bit Windows](https://www.python.org/ftp/python/3.6.3/python-3.6.3-amd64.exe)

    For ease of use, choose to "Customise installation" and ensure "Add python to environment variables" is selected

2) Download and extract the latest version of this application [here](https://github.com/tiberiuslazarus/ExtraAutoSimC/archive/master.zip)

3) Install WoW addon [SimPermut](https://mods.curse.com/addons/wow/254069-simpermut). Export your gear options you would like to compare from in AutoSimC format. Copy, paste, and save the export to a file.

4) Run: `launch.bat` *or* from command line: `python main.py`

5) Enter the name of a file containing an export of data in autosimc format from SimPermut. Optionally the file name can be passed as the first argument on command line.

6) Html format results from SimC for the top 5 dps profiles will be saved in ./output/html/ . Open those to see what gear is equipped for that profile.


### CPU Usage

The system will attempt to spawn multiple threads for simming this may impact performance of other applications you are running (WoW tends to behave interestingly if you run sims and raid at the same time). If more than 2 CPUs are available this value will be ([# of CPUs] - 2), otherwise only 1 thread will perform sims. This default can be overridden in a config file by adding the following:

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

### Enemies

Set number of enemies to sim against. This will likely have weird impact on non-Patchwerk fights.

```
[Sim]
enemies=2
```

```
[Sim]
enemies=1,2,3
```

### Talents

Talent sets can be defined in your profile file. By default simpermut will export your currently selected talents. To override those talents modify the 'talents=' line in your config. 

```
[Profile]
talents=1111321
```

You may also choose to sim your gear against multiple talent sets. All fight styles will be simmed with all available talent sets. The top combinations of gear and talents will be returned.

```
[Profile]
talents=1111321,1111111,2222222,3333333
```

Alternatively, you may run sims against all possible talent combinations. This may take quite a long time as this results in running 2187 sims for each combination of gear available.

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

* ~~Cleaner output of gear for top profiles. Having to open separate html files to see the equipped gear kind of sucks and is not very Auto.~~ -- WHOO!
* ~~Clean up SimC profiles after execution~~ -- DONE
* Configuration options:
  * ~~Sim multiple fight types (patchwerk, heavy movement, cleave)~~ -- DONE
  * ~~Optimise for a different metric (DPS, DPS to Primary target in cleave fights, DTPS)~~ -- DONE
  * ~~Compare talent sets as well as gear~~ -- Done
  * ~~Player skill level~~
  * ~~Calculate stat weights for top simming gear sets~~
  * Plot stats for top simming gear sets -- Not a priority
  * Modify food and potions. Possibly in the same vein as talents with ability to sim multiple/all? -- Not a priority
* GUI of some sort


## Troubleshooting

If you run in to any issues with this program, need advice, or just have some questions, feel free pop over to our Discord channel: https://discord.gg/xctxcvh

## SimC Verison

simc-730-03-win64-65c8b3c92.7z	2018-01-24 04:57

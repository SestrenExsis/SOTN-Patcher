# SOTN-Patcher

A tool for generating PPF files for modifying SOTN, given JSON files describing the desired changes.

## Current status of the project

This project is still actively in the research and prototyping phase of development. It almost definitely still has bugs, may cause softlocks, and may even corrupt the game BIN in its current state. Use at your own risk.

While still in the prototyping and proof-of-concept phase, much of this project will be coded in Python. As the project matures, it may be translated to Javascript over time.

## Usage

Make a copy of your target BIN (SLUS-00067) in a folder called `build` and make sure it is called `Castlevania - Symphony of the Night (Track 1).bin`.

Run the `setup.bat` script, which will generate a template changes file containing data as it was found in the target BIN. You can then modify and/or rename this changes file, within reason.

After you are satisfied with the changes made to the changes file, run the `patch.bat` script to generate a PPF of your changes.

The changes.ppf file that is generated can then be used in conjunction with [ppf.sotn.io](https://ppf.sotn.io/) to apply the changes found in the PPF to your BIN file.

There is also a `sotn_address.py` utility that can be invoked from the command line to convert addresses found on the disc to canonical gamedata addresses (and vice versa).

## Acknowledgements

Most of the knowledge present in this project is only possible due to the immense efforts of the SOTN and rom-hacking community:

- Forat Negre, for their research into room layouts, which helped demystify a lot of how stages and rooms worked in this game
- [TalicZealot](https://github.com/taliczealot), for furthering knowledge about the game and making available tons of SOTN-related resources
- [MainMemory](https://github.com/MainMemory), for their [CastleEditor](https://github.com/MainMemory/SotNCastleEditor) project, which provided key insight into a few addresses as well as extremely helpful visualizations of the castle stages
- [Mottzilla](https://github.com/MottZilla), for their _StartAnywhere_ and _TileMapFind_ scripts, which dramatically improved turnaround time during playtesting
- [meunierd](https://github.com/meunierd), for the PPF file format
- [Fatalis](https://github.com/fatalis), for their Drop Calculator
- Contributors and maintainers of the [SOTN-Decomp](https://github.com/Xeeynamo/sotn-decomp) project, including:
  - [Xeeynamo](https://github.com/Xeeynamo)
  - [Bismurphy](https://github.com/bismurphy)
  - [Sozud](https://github.com/sozud)
  - [Sonic Dreamcaster](https://github.com/sonicdcer)
- Contributors and maintainers of the [SOTN-Randomizer](https://github.com/3snowp7im/SotN-Randomizer) project, including:
  - [3snowp7im](https://github.com/3snowp7im) (Wild Mouse)
  - [Mottzilla](https://github.com/MottZilla)
  - [eldri7ch](https://github.com/eldri7ch2)
  - [LuciaRolon](https://github.com/LuciaRolon)
- The entire SOTN community, for their generosity and kindness
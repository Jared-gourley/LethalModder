# LethalModder

Due to dealing with the difficulty of having to help people set up game files for Lethal Company modded multiplayer too many times, I decided to make a program which downloads from a zip file I make which has the necessary mod files and moves them to be placed in the correct locations in the user's game files. To further aid ease of use, the program is able to automatically locate where Lethal Company is installed and thus can be ran from anywhere* on the user's computer. 

Note that this was solely designed for Windows users since as of the time of creation, Lethal Company only exists on the Windows version of Steam. (This program can be used inside software like Whisky though if you also add it as a runnable program).

*(This makes use of Steam's libraryfolders.vdf file which points to where every game install location could be, and it is assumed that Steam itself is installed to the default location for the sake of finding the libraryfolders.vdf file. If this isn't possible then the program can be placed inside the game files location and it will recognize this and be able to work from there).

## Program Design
To quote the "More Info" page from the program:

```
This process works by locating your Lethal Company game files install, then downloading mod files and configuring/replacing them as necessary. For transparency this is the detailed process about what the modder is actually doing:

1. Finding game install location (if you haven't seen an error then this part has already worked)
- if you did get an error, your game install location is in some unusual spot and likely you installed Steam somewhere other than the default location. You can solve this problem by moving LethalModder.exe into the instal location of your game (Steam should be able to show you where this is). This program will recognize if it is in the game files location already and can work from there (you can make a shortcut to the exe if needed).

2. Making temp folder
- This program needs a temporary empty space to download and unzip the mod pack to, so a folder is made with a name like temp1. This folder should be deleted automatically once the install is done, so if you see this folder you can delete it (this could happen if you close the program before it cleans the folder for example).

3. Downloading the mod pack
- On the Google Drive is the LethalCompanyMods.zip (or similarly named) file which contains the current mods that we intend to use. This program downloads that file into the temp folder.

4. Installing the mod pack
- Inside the zip is a BepInEx folder, a doorstop_config.ini file, and a winhttp.dll file. For the latter two files, if they already exist in your game files they are just left untouched. However for the BepInEx folder the old one will be deleted if it exists and this new one will be put in its place.

5. Cleaning up the temp folder
- Now that the mod files have been set up, the temp folder and whatever is left inside it can simply be deleted and the game is ready to be run with mods!

- For the reverting to vanilla feature, this can simply be done by deleting BepInEx, doorstop_config.ini and winhttp.dll and this is what the modder does.
```

## Usage
If you want to make use of this program, you can do so by simply making a zip file on Google Drive (which has public view access to anyone with the link). This zip file should contain in it a complete BepInEx folder, a doorstop_config.ini file, and a winhttp.dll file. It should be the case that you could extract the zip file and drag+drop all three items (which are in the same directory) into your game files with no other setup.

I convert the python program into an exe by using Pyinstaller. It can be done using a command like this:
```
pyinstaller --noconfirm --onefile --windowed --add-data "lethalcursed.ico;." -i "lethalcursed.ico" LethalModder.py
```
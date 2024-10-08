'''
Code with the functions for the mod managing capabilities as well as the GUI

Some print statements are still left in but cannot be seen after converting the 
.py to a .exe file so they are left as debugging for development
'''

from gdown import download
from vdf import parse
import os, sys, glob, zipfile
from shutil import rmtree
from charset_normalizer import md__mypyc # for pyinstaller to work

from tkinter import Button, Tk, Label, Toplevel, LEFT, BOTH

tempFolderName = ''
IS_ACTION_RUNNING = False

# ============================= FUNCTIONS ==================================
def initTempFolder(downloadLocation):
    global tempFolderName
    i = 1
    while True: # Find a tempx name that isn't taken
        if not os.path.isdir(downloadLocation + "\\" + "temp" + str(i)):
            break
        if i > 10:
            print("There are too many temp files, exiting")
            return False

        i += 1

    tempFolderName = "temp" + str(i)
    os.mkdir(downloadLocation + "\\" + tempFolderName)
    return True
# ------ end of initFiles()


def cleanupFiles(downloadLocation):
    # MAKE SURE the temp folder is a child of the download location before we accidentally delete something bad
    if tempFolderName == "":
        print("Error: Something went very wrong, but no damage was caused. Exiting")
        return False
    
    if not os.path.isdir(downloadLocation + "\\" + tempFolderName):
        print("Error: Cannot find temp folder to delete, exiting")
        return False
    
    # Delete it...
    rmtree(downloadLocation + "\\" + tempFolderName)

    # Check if any other temp folders got made somehow and get rid of them as well
    for i in range(1, 11):
        if os.path.isdir(downloadLocation + "\\temp" + str(i)):
            rmtree(downloadLocation + "\\temp" + str(i))

    print("Files cleaned up")
    return True
# ------ end cleanupFiles()


def uninstallMods(downloadLocation):
    # MAKE SURE we're in the right location by checking that the "lethal company.exe" is here
    if not os.path.exists(downloadLocation + "\\Lethal Company.exe"):
        print("ERROR: somehow not in game files location: operation cancelled")
        return False

    # Delete BepInEx, doorstop_config.ini, and winhttp.dll if they exist
    if os.path.exists(downloadLocation + "\\BepInEx"):
        rmtree(downloadLocation + "\\BepInEx")
    if os.path.exists(downloadLocation + "\\doorstop_config.ini"):
        os.remove(downloadLocation + "\\doorstop_config.ini")
    if os.path.exists(downloadLocation + "\\winhttp.dll"):
        os.remove(downloadLocation + "\\winhttp.dll")

    return True
# ------ end uninstallMods()


def downloadModFiles(downloadLocation):
        
    # id of the LethalCompanyMods zip
    id = "1cmnZ6RfMpQLLZVMIzTKTFEqyFwJ1N8Gp"
    try:
        file = download(id=id, output=downloadLocation + "\\" + tempFolderName + "\\")
    except Exception as e:
        print("File download failed:", e)
        return None
    
    print("downloaded file path:", file)

    if file == None:
        print("Error: Files were unable to download. Process failed to complete")
        return None
    else:
        return file
# ------ end downloadModFiles()

def installModFiles(downloadLocation, zipName):
    # Knowing that the files have been downloaded, install them accordingly

    # Unzip the folder
    with zipfile.ZipFile(downloadLocation + "\\" + tempFolderName + "\\" + zipName, "r") as zip_ref:
        zip_ref.extractall(downloadLocation + "\\" + tempFolderName)

    # Get the name of the unzipped folder where the downloaded files we need are
    files = glob.glob(downloadLocation + "\\" + tempFolderName + "\\*\\doorstop_config.ini")
    modFilesLocation = files[0].replace("\\doorstop_config.ini", "")
    print("modFileLocation:", modFilesLocation)

    # Check if doorstop_config.ini and winhttp.dll already exist and add if not
    if not os.path.exists(downloadLocation + "\\doorstop_config.ini"):
        os.rename(modFilesLocation + "\\doorstop_config.ini", downloadLocation + "\\doorstop_config.ini")
    if not os.path.exists(downloadLocation + "\\winhttp.dll"):
        os.rename(modFilesLocation + "\\winhttp.dll", downloadLocation + "\\winhttp.dll")

    # Delete the BepInEx folder if it exists 
    if os.path.exists(downloadLocation + "\\BepInEx"):
        rmtree(downloadLocation + "\\BepInEx")
        print("BepInEx folder deleted")
    
    # Put in the new BepInEx folder
    os.rename(modFilesLocation + "\\BepInEx", downloadLocation + "\\BepInEx")
# ------ end installModFiles()


def findLCInstall():
    # Attempt to go to Program Files (x86)\Steam\steamapps\common\Lethal Company (default lethal company install location)
    dir = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Lethal Company"
    if os.path.exists(dir + "\\Lethal Company.exe"):
        return dir

    # Check if LethalModder is saved in the Lethal Company directory itself
    if os.path.exists("Lethal Company.exe"):
        #print("Holy shoot I just hit a clip")
        return "." # We're already in the right location
    
    # If not there, then go look for the libraryfolders.vdf file and check every steam install location
    vdfDir = "C:\\Program Files (x86)\\Steam\\steamapps\\libraryfolders.vdf"
    if not os.path.exists(vdfDir):
        print("Error: Cannot locate lethal company game files location after checking default install location and current directory. Fix this by dragging the LethalModder program into your game files.")
        return False


    vdfDict = parse(open(vdfDir))
    for key in vdfDict['libraryfolders']:
        #print(vdfDict['libraryfolders'][key])

        # Lethal company app ID: 1966720
        if '1966720' in vdfDict['libraryfolders'][key]['apps']:
            print('WE GOT EM')
            print(vdfDict['libraryfolders'][key]['path'] + "\\steamapps\\common\\Lethal Company")
            return vdfDict['libraryfolders'][key]['path'] + "\\steamapps\\common\\Lethal Company"

    print("Error: Lethal company is not installed? Process failed")
    return False
# ------ end findLCInstall()


def installButtonClicked():
    global IS_ACTION_RUNNING, progressText, window, progressLabel, LCInstallDir, tempFolderName

    # DO NOT ACTIVATE IF ONE IS ALREADY RUNNING
    if IS_ACTION_RUNNING:
        return
    
    IS_ACTION_RUNNING = True

    # Create the temp folder
    if not initTempFolder(LCInstallDir):
        progressText = 'ERROR: Could not create a temp folder (there are too many already). Go delete some and try again'
        progressLabel.config(text=progressText)
        window.update()
        IS_ACTION_RUNNING = False
        return
    
    # Move on to download step
    progressText = 'Downloading mod zip file from Google Drive, please be patient...'
    progressLabel.config(text=progressText)
    window.update()

    file = downloadModFiles(LCInstallDir)
    if file == None:
        progressText = 'ERROR: Could not download the zip file from Google Drive'
        progressLabel.config(text=progressText)
        window.update()
        cleanupFiles(LCInstallDir)
        IS_ACTION_RUNNING = False
        return

    # Move on to the install step
    progressText = 'Extracting zip file and setting up files...'
    progressLabel.config(text=progressText)
    window.update()

    zipFileName = file.split("\\")[-1] # Get just the filename we want
    installModFiles(LCInstallDir, zipFileName)

    # Move on to cleaning the temp folder (final step)
    progressText = 'Cleaning up temp folder...'
    progressLabel.config(text=progressText)
    window.update()

    if not cleanupFiles(LCInstallDir):
        progressText = 'Mods downloaded successfully, but temp folder could not be deleted'
        progressLabel.config(text=progressText)
        window.update()
        IS_ACTION_RUNNING = False
        return

    # If we got here we successfully did everything!
    progressText = 'Mod install successful!'
    progressLabel.config(text=progressText)
    window.update()

    IS_ACTION_RUNNING = False
    return


def revertButtonClicked():
    global IS_ACTION_RUNNING, progressText, window, progressLabel, LCInstallDir

    # DO NOT ACTIVATE IF ONE IS ALREADY RUNNING
    if IS_ACTION_RUNNING:
        return
    
    IS_ACTION_RUNNING = True

    progressText = 'Deleting mod files...'
    progressLabel.config(text=progressText)
    window.update()

    if not uninstallMods(LCInstallDir):
        progressText = 'ERROR: Mod uninstall was unsuccessful'
        progressLabel.config(text=progressText)
        window.update()
        IS_ACTION_RUNNING = False
        return
    
    # If here then the uninstall must have worked
    progressText = "Mod files deleted! You're now playing vanilla Lethal Company"
    progressLabel.config(text=progressText)
    window.update()

    IS_ACTION_RUNNING = False
    return


def showMoreInfo(window):
    top= Toplevel(window)
    top.geometry("800x700")
    top.title("LethalModder Info")
    top.iconbitmap(windowIconPath)

    Label(top, text="More Info", font=('Arial', 24)).pack()

    text = " \
This process works by locating your Lethal Company game files install, then \
downloading mod files and configuring/replacing them as necessary. For transparency \
this is the detailed process about what the modder is actually doing:\n\n \
        \
1. Finding game install location (if you haven't seen an error then this part has already worked)\n \
- if you did get an error, your game install location is in some unusual spot and likely you installed Steam \
somewhere other than the default location. You can solve this problem by moving LethalModder.exe into the install \
location of your game (Steam should be able to show you where this is). This program will \
recognize if it is in the game files location already and can work from there (you can make a shortcut to the exe if needed).\n\n \
        \
2. Making temp folder\n \
- This program needs a temporary empty space to download and unzip the mod pack to, so a folder is made \
with a name like temp1. This folder should be deleted automatically once the install is done, so if you see this folder \
you can delete it (this could happen if you close the program before it cleans the folder for example).\n\n \
        \
3. Downloading the mod pack\n \
- On the Google Drive is the LethalCompanyMods.zip (or similarly named) file which contains the current mods \
that we intend to use. This program downloads that file into the temp folder.\n\n \
        \
4. Installing the mod pack\n \
- Inside the zip is a BepInEx folder, a doorstop_config.ini file, and a winhttp.dll file. For the \
latter two files, if they already exist in your game files they are just left untouched. However for the BepInEx folder \
the old one will be deleted if it exists and this new one will be put in its place.\n\n \
        \
5. Cleaning up the temp folder\n \
- Now that the mod files have been set up, the temp folder and whatever is left inside it can simply be deleted and \
the game is ready to be run with mods!\n\n \
        \
- For the reverting to vanilla feature, this can simply be done by deleting BepInEx, doorstop_config.ini and \
winhttp.dll and this is what the modder does."
    textLabel = Label(top, text=text, font=('Arial', 12), justify=LEFT)
    textLabel.bind('<Configure>', lambda e: textLabel.config(wraplength=textLabel.winfo_width()))
    textLabel.pack(fill=BOTH, expand=True, padx=10)
# ------ End of showMoreInfo()


# ================================ GUI CODE ==================================

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(
        sys,
        '_MEIPASS',
        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

windowIconPath = resource_path('lethalcursed.ico')

window = Tk()
window.title('LethalModder')
window.geometry("650x600")
window.resizable(False, False)
window.iconbitmap(windowIconPath)


# Make sure we can find the install location, otherwise we can't run the app anyway
LCInstallDir = findLCInstall()

titleLabel = Label(window, pady=10, text='Lethal Modder', font=('Arial', 48, 'bold'))
titleLabel.pack()

subTitleLabel = Label(window, text='A simple tool to automatically download and install\nthe current modpack on the Google Drive', font=('Arial', 14))
subTitleLabel.pack()

# Show more info button
gameButton = Button(window, text='More details', font=('Arial', 14), command=lambda rootWindow=window: showMoreInfo(rootWindow))
gameButton.pack(pady=10)


# If unable to find game install, print the error string and don't continue
if not LCInstallDir:
    failText = "Could not find Lethal Company install. You can fix this by moving LethalModder.exe into your game files folder."
    errorLabel = Label(window, text="ERROR: " + failText, font=('Arial', 20), wraplength=600)
    errorLabel.pack(padx=10, pady=10)
    window.mainloop() # Gets the program stuck at this spot forever
    quit() # Makes sure no further commands get ran in the last few seconds that the window is closing


# Make space for the (currently) empty progress text for when an action happens
progressText = ''
progressLabel = Label(window, pady=80, padx=10, text=progressText, font=('Arial', 16), wraplength=600)
progressLabel.pack()


noticeText = "(Don't worry if the window goes unresponsive for a few moments while installing, this is normal)"
noticeLabel = Label(window, padx=10, text=noticeText, font=('Arial', 12), wraplength=400)
noticeLabel.place(x=130, y=480)

# Make the Install button and Revert button
installButton = Button(window, text='Install Latest Mod', font=('Arial', 14), command=installButtonClicked)
installButton.place(x=50, y=530)

revertButton = Button(window, text='Revert to Vanilla', font=('Arial', 14), command=revertButtonClicked)
revertButton.place(x=450, y=530)

window.mainloop()

import subprocess
import os
import shutil
import requests
import zipfile
import logging
import vdf
import configparser

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Read configuration
config = configparser.ConfigParser()
config.read('server.cfg')

STEAMCMD_URL = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
STEAMCMD_DIR = os.path.abspath("steamcmd")
STEAMCMD_EXE = os.path.join(STEAMCMD_DIR, "steamcmd.exe")

SERVER_APP_ID = config['Server']['server_app_id']
GAME_APP_ID = config['Server']['game_app_id']
MOD_IDS = [mod_id.strip() for mod_id in config['Mods']['mod_ids'].split(',')]

def ensure_steamcmd_installed():
    if not os.path.exists(STEAMCMD_EXE):
        print(f"SteamCMD not found at {STEAMCMD_EXE}. Installing...")
        if not os.path.exists(STEAMCMD_DIR):
            os.makedirs(STEAMCMD_DIR)
        
        print(f"Downloading SteamCMD to {STEAMCMD_DIR}...")
        response = requests.get(STEAMCMD_URL)
        zip_path = os.path.join(STEAMCMD_DIR, "steamcmd.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Extracting SteamCMD to {STEAMCMD_DIR}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(STEAMCMD_DIR)
        
        os.remove(zip_path)
        
        print("Running SteamCMD for initial setup...")
        subprocess.run([STEAMCMD_EXE, "+quit"], check=True)
        
        print(f"SteamCMD installed successfully at {STEAMCMD_EXE}")
    else:
        print(f"SteamCMD is already installed at {STEAMCMD_EXE}")

def run_steamcmd(commands):
    ensure_steamcmd_installed()
    
    full_command = [STEAMCMD_EXE] + commands
    
    print(f"Executing SteamCMD with commands: {full_command}")
    process = subprocess.Popen(full_command, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               universal_newlines=True)
    
    stdout, stderr = process.communicate()
    
    print("SteamCMD execution completed")
    print(f"Stdout: {stdout}")
    if stderr:
        print(f"Stderr: {stderr}")
    return stdout, stderr

def update_app(app_id):
    print(f"Checking for updates for app ID: {app_id}")
    
    commands = [
        "+login anonymous",
        f"+app_update {app_id} validate",
        "+quit"
    ]
    
    stdout, stderr = run_steamcmd(commands)
    
    if f"Success! App '{app_id}' already up to date." in stdout:
        print(f"App {app_id} is already up to date.")
        return False
    elif f"Success! App '{app_id}' fully installed." in stdout:
        print(f"Successfully updated app {app_id}")
        return True
    else:
        print(f"Unexpected result while updating app {app_id}")
        print(f"Error: {stderr}")
        return False

def find_install_directory(app_id):
    print(f"Searching for install directory of app {app_id}")
    steamapps_dir = os.path.join(STEAMCMD_DIR, "steamapps")
    print(f"Checking steamapps directory: {steamapps_dir}")
    
    library_folders_file = os.path.join(steamapps_dir, "libraryfolders.vdf")
    print(f"Checking for libraryfolders.vdf at: {library_folders_file}")
    
    if os.path.exists(library_folders_file):
        print(f"Found libraryfolders.vdf, parsing...")
        with open(library_folders_file, 'r') as f:
            data = vdf.load(f)
        
        for folder_id, folder_data in data.get('libraryfolders', {}).items():
            print(f"Checking library folder: {folder_data.get('path', 'Unknown path')}")
            apps = folder_data.get('apps', {})
            if app_id in apps:
                install_path = os.path.join(folder_data['path'], 'steamapps', 'common', 'Harsh Doorstop Developer Build Dedicated Server')
                print(f"Found app {app_id} in library folder. Expected install path: {install_path}")
                return install_path
    else:
        print(f"libraryfolders.vdf not found at {library_folders_file}")
    
    print(f"App {app_id} not found in libraryfolders.vdf, searching steamapps directory...")
    for root, dirs, files in os.walk(steamapps_dir):
        print(f"Searching in directory: {root}")
        if 'Harsh Doorstop Developer Build Dedicated Server' in dirs:
            install_path = os.path.join(root, 'Harsh Doorstop Developer Build Dedicated Server')
            print(f"Found server directory at: {install_path}")
            return install_path
    
    print(f"Could not find install directory for app {app_id}")
    return None

def copy_server_files(app_id):
    source_path = find_install_directory(app_id)
    destination_path = "server"

    if source_path:
        print(f"Attempting to copy server files from {source_path} to {destination_path}")

        # Backup the Saved directory if it exists
        saved_path = os.path.join(destination_path, "HarshDoorstop", "Saved")
        backup_path = os.path.join(destination_path, "HarshDoorstop_Saved_Backup")
        if os.path.exists(saved_path):
            print(f"Backing up {saved_path} to {backup_path}")
            shutil.copytree(saved_path, backup_path, dirs_exist_ok=True)

        if os.path.exists(destination_path):
            print(f"Removing existing destination directory: {destination_path}")
            shutil.rmtree(destination_path)
        
        print(f"Copying files...")
        shutil.copytree(source_path, destination_path)

        # Restore the Saved directory
        if os.path.exists(backup_path):
            print(f"Restoring {backup_path} to {saved_path}")
            shutil.copytree(backup_path, saved_path, dirs_exist_ok=True)
            shutil.rmtree(backup_path)

        print(f"Successfully copied server files to {destination_path}")
    else:
        print(f"Could not find the server files for app ID: {app_id}")

def download_workshop_mods(mod_ids):
    workshop_path = os.path.join(STEAMCMD_DIR, "steamapps", "workshop", "content", GAME_APP_ID)
    mods_destination = os.path.join("server", "HarshDoorstop", "Mods")

    os.makedirs(mods_destination, exist_ok=True)

    for mod_id in mod_ids:
        print(f"\nDownloading mod ID: {mod_id}")
        
        commands = [
            "+login anonymous",
            f"+workshop_download_item {GAME_APP_ID} {mod_id}",
            "+quit"
        ]
        stdout, stderr = run_steamcmd(commands)

        if "Success. Downloaded item" in stdout:
            print(f"Successfully downloaded workshop item {mod_id}")
            
            mod_source = os.path.join(workshop_path, mod_id)
            
            if os.path.exists(mod_source):
                subdirs = [d for d in os.listdir(mod_source) if os.path.isdir(os.path.join(mod_source, d))]
                if subdirs:
                    subdir_source = os.path.join(mod_source, subdirs[0])
                    subdir_dest = os.path.join(mods_destination, subdirs[0])
                    
                    if os.path.exists(subdir_dest):
                        shutil.rmtree(subdir_dest)
                    
                    shutil.copytree(subdir_source, subdir_dest)
                    print(f"Moved contents of mod {mod_id} to {subdir_dest}")
                else:
                    print(f"No subdirectory found in mod {mod_id}. Contents of {mod_source}: {os.listdir(mod_source)}")
                    # If no subdirectory, copy the entire mod_source
                    subdir_dest = os.path.join(mods_destination, f"mod_{mod_id}")
                    if os.path.exists(subdir_dest):
                        shutil.rmtree(subdir_dest)
                    shutil.copytree(mod_source, subdir_dest)
                    print(f"Copied entire mod {mod_id} to {subdir_dest}")
            else:
                print(f"Mod directory not found for {mod_id}. Expected at: {mod_source}")
        else:
            print(f"Failed to download workshop item {mod_id}")
            print(f"Error: {stderr}")

# Main execution
if __name__ == "__main__":
    ensure_steamcmd_installed()

    print("Checking for updates...")
    if update_app(SERVER_APP_ID):
        copy_server_files(SERVER_APP_ID)
    else:
        print("No updates available for the main app.")

    print("\nDownloading and updating workshop mods...")
    download_workshop_mods(MOD_IDS)

    print("Script execution completed.")

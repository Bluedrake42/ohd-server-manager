import subprocess
import os
import shutil

def run_steamcmd(commands):
    steamcmd_path = "steamcmd/steamcmd.exe"  # Update this path
    
    full_command = [steamcmd_path] + commands
    
    process = subprocess.Popen(full_command, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               universal_newlines=True)
    
    stdout, stderr = process.communicate()
    
    return stdout, stderr

def check_for_updates(app_id):
    commands = [
        "+login anonymous",
        f"+app_info_update 1",
        f"+app_status {app_id}",
        "+quit"
    ]
    
    stdout, stderr = run_steamcmd(commands)
    
    return "version mismatch" in stdout.lower()

def update_app(app_id):
    commands = [
        "+login anonymous",
        f"+app_update {app_id}",
        "+quit"
    ]
    
    stdout, stderr = run_steamcmd(commands)
    
    if "Success!" in stdout:
        print(f"Successfully updated app {app_id}")
        return True
    else:
        print(f"Failed to update app {app_id}")
        print("Error:", stderr)
        return False

def copy_server_files():
    source_path = os.path.join("steamcmd", "steamapps", "common", "Harsh Doorstop Developer Build Dedicated Server")
    destination_path = "server"

    if os.path.exists(source_path):
        if os.path.exists(destination_path):
            shutil.rmtree(destination_path)
        shutil.copytree(source_path, destination_path)
        print(f"Successfully copied server files to {destination_path}")
    else:
        print(f"Source directory not found: {source_path}")

def check_workshop_item_update(game_id, mod_id):
    commands = [
        "+login anonymous",
        f"+workshop_status {game_id} {mod_id}",
        "+quit"
    ]
    
    stdout, stderr = run_steamcmd(commands)
    
    return "needs update" in stdout.lower()

def download_and_move_workshop_mods(mod_ids):
    game_id = "1307180"  # Harsh Doorstop game ID
    workshop_path = os.path.join("steamcmd", "steamapps", "workshop", "content", game_id)
    mods_destination = os.path.join("server", "HarshDoorstop", "Mods")

    os.makedirs(mods_destination, exist_ok=True)

    for mod_id in mod_ids:
        if check_workshop_item_update(game_id, mod_id):
            print(f"\nUpdating mod ID: {mod_id}")
            
            commands = [
                "+login anonymous",
                f"+workshop_download_item {game_id} {mod_id}",
                "+quit"
            ]
            stdout, stderr = run_steamcmd(commands)

            if "Success." in stdout:
                print(f"Successfully updated workshop item {mod_id}")
                
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
                        print(f"No subdirectory found in mod {mod_id}")
                else:
                    print(f"Mod directory not found for {mod_id}")
            else:
                print(f"Failed to update workshop item {mod_id}")
                print("Error:", stderr)
        else:
            print(f"\nMod ID {mod_id} is up to date. Skipping.")

# Main execution
app_id = "1316480"  # Harsh Doorstop Dedicated Server app ID
mod_ids = ["3303068735"]  # Example mod IDs

if check_for_updates(app_id):
    print("Updates available for the main app. Updating...")
    if update_app(app_id):
        copy_server_files()
else:
    print("No updates available for the main app.")

print("\nChecking for mod updates...")
download_and_move_workshop_mods(mod_ids)

import subprocess
import os

def run_steamcmd(commands):
    steamcmd_path = "path/to/steamcmd.exe"  # Update this path
    
    # Prepare the full command
    full_command = [steamcmd_path] + commands
    
    # Run SteamCMD
    process = subprocess.Popen(full_command, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               universal_newlines=True)
    
    # Capture output
    stdout, stderr = process.communicate()
    
    return stdout, stderr

def update_app(app_id):
    commands = [
        "+login anonymous",
        f"+app_update {app_id}",
        "+quit"
    ]
    
    stdout, stderr = run_steamcmd(commands)
    
    if "Success!" in stdout:
        print(f"Successfully updated app {app_id}")
    else:
        print(f"Failed to update app {app_id}")
        print("Error:", stderr)

# Example usage
update_app("1316480")  # Update CS:GO Dedicated Server

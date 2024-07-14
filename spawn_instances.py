import os
import subprocess
import time
import shutil

# Function to copy required files to each instance folder
def copy_files_to_instances(num_instances, root_dir):
    # Ensure files exist in root directory
    cookies_file = os.path.join(root_dir, 'cookies.txt')
    script_file = os.path.join(root_dir, 'board_registration_and_testing.py')

    if not os.path.exists(cookies_file):
        print(f"Error: {cookies_file} not found in root directory.")
        return False

    if not os.path.exists(script_file):
        print(f"Error: {script_file} not found in root directory.")
        return False

    # Copy files to each instance folder
    for i in range(num_instances):
        instance_dir = os.path.join(root_dir, f'instance_{i+1}')
        if not os.path.exists(instance_dir):
            os.makedirs(instance_dir)
        
        # Copy cookies.txt and board_registration_and_testing.py to instance folder
        shutil.copy(cookies_file, instance_dir)
        shutil.copy(script_file, instance_dir)

    return True

# Function to spawn instances
def spawn_instances(num_instances, boards_per_instance, root_dir):
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Get current directory of this script

    # Copy required files to each instance folder
    if not copy_files_to_instances(num_instances, root_dir):
        return

    # Spawn instances
    for i in range(num_instances):
        instance_dir = os.path.join(root_dir, f'instance_{i+1}')
        start_id = i * boards_per_instance + 1
        end_id = start_id + boards_per_instance - 1

        # Command to run the script in each folder
        script_path = os.path.join(instance_dir, 'board_registration_and_testing.py')

        # Construct command to run in a separate terminal
        if os.name == 'posix':  # Unix/Linux/MacOS
            command = f"gnome-terminal -- python3 {script_path} {start_id} {end_id}"
        elif os.name == 'nt':  # Windows
            command = f"start cmd /k py {script_path} {start_id} {end_id}"
        else:
            print("Unsupported OS.")
            return
        
        # Run the command in the corresponding folder
        subprocess.Popen(command, shell=True, cwd=instance_dir)
        print(f"Instance {i+1} spawned to handle boards {start_id} to {end_id}.")
        time.sleep(1)  # Optional delay between spawning instances

if __name__ == "__main__":
    num_instances = 10  # Number of instances to spawn
    boards_per_instance = 1000  # Number of boards each instance will handle
    root_dir = os.path.dirname(os.path.abspath(__file__))  # Root directory where cookies.txt and board_registration_and_testing.py are located
    
    spawn_instances(num_instances, boards_per_instance, root_dir)

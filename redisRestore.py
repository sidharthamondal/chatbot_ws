import os
import subprocess

def restore_redis(input_file):
    try:
        # Stop the Redis server inside the Docker container
        subprocess.run(['docker', 'exec', 'sweet_wing', 'redis-cli', 'SHUTDOWN'])

        # Wait for the Redis server to stop
        subprocess.run(['docker', 'wait', 'sweet_wing'])

        # Copy the backup file from the host machine to the Docker container
        current_directory = os.getcwd()
        backup_path_host = os.path.join(current_directory, input_file)
        
        subprocess.run(['docker', 'cp', backup_path_host, 'sweet_wing:/data/dump.rdb'])
        
        # Start the Redis server inside the Docker container
        subprocess.run(['docker', 'start', 'sweet_wing'])

        print(f"Restore completed using {backup_path_host}")

    except Exception as e:
        print(f"Restore failed: {str(e)}")

# Example usage
restore_redis('redis_backup.rdb')

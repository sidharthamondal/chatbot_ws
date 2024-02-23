import os
import subprocess

def backup_redis(output_file):
    try:
        # Use redis-cli to perform a background save inside the Docker container
        subprocess.run(['docker', 'exec', 'websocket-chat-server-redis_server-1', 'redis-cli', 'BGSAVE'])

        # Wait for the background save to complete
        subprocess.run(['docker', 'exec', 'websocket-chat-server-redis_server-1', 'redis-cli', 'LASTSAVE'])
        
        # Save the RDB file to the current working directory on the host machine
        current_directory = os.getcwd()
        backup_path_host = os.path.join(current_directory, output_file)
        
        # Copy the backup file from the Docker container to the host machine
        subprocess.run(['docker', 'cp', 'websocket-chat-server-redis_server-1:/data/dump.rdb', backup_path_host])
        
        print(f"Backup completed and saved to {backup_path_host}")

    except Exception as e:
        print(f"Backup failed: {str(e)}")

# Example usage
backup_redis('redis_backup.rdb')

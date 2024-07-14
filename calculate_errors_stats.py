import os
import json
from datetime import datetime

def calculate_errors_stats():
    error_stats = {
        'total_errors': 0,
        'error_types': {},
        'total_requests': 0,
        'successful_requests': 0,
        'error_percentage': 0.0
    }

    instances_folder = 'instances'
    instance_folders = [name for name in os.listdir(instances_folder) if os.path.isdir(os.path.join(instances_folder, name))]

    total_error_time = 0.0

    for instance_folder in instance_folders:
        instance_folder_path = os.path.join(instances_folder, instance_folder)
        log_file = os.path.join(instance_folder_path, 'log.txt')

        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()

                for line in lines:
                    if 'Error' in line:
                        error_stats['total_errors'] += 1
                        error_type = line.split('Error: ')[1].split('.')[0]
                        if error_type in error_stats['error_types']:
                            error_stats['error_types'][error_type] += 1
                        else:
                            error_stats['error_types'][error_type] = 1

                    elif 'registered successfully' in line or 'Sent command' in line:
                        error_stats['successful_requests'] += 1

                    error_stats['total_requests'] += 1

                    if 'Error: ' in line:
                        total_error_time += float(line.split(' ')[-2][:-2])

    if error_stats['total_requests'] > 0:
        error_stats['error_percentage'] = (error_stats['total_errors'] / error_stats['total_requests']) * 100

    return error_stats, total_error_time

def main():
    error_stats, total_error_time = calculate_errors_stats()

    print(f"Total errors: {error_stats['total_errors']}")
    print("Error types:")
    for error_type, count in error_stats['error_types'].items():
        print(f"- {error_type}: {count}")

    print(f"Total requests: {error_stats['total_requests']}")
    print(f"Successful requests: {error_stats['successful_requests']}")
    print(f"Error percentage: {error_stats['error_percentage']:.2f}%")

    print(f"Total time spent in error state (seconds): {total_error_time:.2f}")

if __name__ == "__main__":
    main()

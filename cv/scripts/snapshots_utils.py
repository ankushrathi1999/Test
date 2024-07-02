import sys
sys.path.append('..')

import os
import datetime
from collections import defaultdict
import shutil

from config.config import config

api_config = config['api_artifact']
snapshots_dir = api_config.get('snapshots_dir')
metadata_dir = api_config.get('metadata_dir')

def move_to_date_folder(date, directory):
    for file in os.listdir(directory):
        filepath = os.path.join(directory, file)
        if not os.path.isfile(filepath):
            continue
        vehicle_model, cam_type = file.split('_')[1:3]
        creation_time = os.path.getctime(filepath)
        file_date = datetime.datetime.fromtimestamp(creation_time).strftime('%Y%m%d')
        if file_date != date:
            continue
        dest_dir = os.path.join(directory, date, vehicle_model, cam_type)
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, file)
        print("Moving:", filepath, dest_path)
        shutil.move(filepath, dest_path)

def count_files_by_date(directory):
    date_counts = defaultdict(int)
    for file in os.listdir(directory):
        filepath = os.path.join(directory, file)
        if not os.path.isfile(filepath):
            continue
        creation_time = os.path.getctime(filepath)
        date = datetime.datetime.fromtimestamp(creation_time).strftime('%Y%m%d')
        date_counts[date] += 1

    # Print out the counts in the required format
    for date, count in sorted(date_counts.items()):
        print(f"{date}: {count}")

def count_files_by_group(directory, mode='vehicle'):
    counts = defaultdict(int)
    for file in os.listdir(directory):
        filepath = os.path.join(directory, file)
        if not os.path.isfile(filepath):
            continue
        group = file.split('_')[{
            'chassis': 0,
            'vehicle': 1,
        }[mode]]
        counts[group] += 1
    for group, count in sorted(counts.items()):
        print(f"{group}: {count}")

if __name__ == '__main__':
    mode = sys.argv[1]
    assert mode in {'countbydate', 'countbymodel', 'countbychassis', 'movetodatedir'}, 'Invalid mode'

    if mode == 'countbydate':
        print("Count of Snapshot files:")
        count_files_by_date(snapshots_dir)
        print("Count of Metadata files:")
        count_files_by_date(metadata_dir)
    elif mode == 'countbymodel':
        print("Count of Snapshot files:")
        count_files_by_group(snapshots_dir, mode='vehicle')
        print("Count of Metadata files:")
        count_files_by_group(metadata_dir, mode='vehicle')
    elif mode == 'countbychassis':
        print("Count of Snapshot files:")
        count_files_by_group(snapshots_dir, mode='chassis')
        print("Count of Metadata files:")
        count_files_by_group(metadata_dir, mode='chassis')
    elif mode == 'movetodatedir':
        date = sys.argv[2]
        print("Moving Snapshot files to:", date)
        move_to_date_folder(date, snapshots_dir)
        print("Moving Metadata files to:", date)
        move_to_date_folder(date, metadata_dir)
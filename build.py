import os
import os.path
import shutil

from recent_archives import *

#get the archive
versions = generate_archive_dict()
#sort the archive
for entry in versions:
    versions[entry] = sorted(versions[entry], key = archive_sort_function)

def copy_archive(quarter, output_path=None):
    """
    Takes a quarter identifier (e.g., 'fall2016') and copys the archive to its
    own folder.
    """
    if output_path is None:
        output_path = 'data_{}/'.format(quarter)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for entry in archive_at_season(quarter, versions):
        shutil.copyfile('data/'+ entry, output_path + entry.split('-',1)[1])
 

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('quarter', help='Quarter identifier (e.g., fall2016)')
    args = parser.parse_args()

    copy_archive(args.quarter)

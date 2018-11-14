import os
import os.path
import shutil
import time

from corpusbuilder import get_season
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
        outfile = output_path + entry.split('-',1)[1]
        outfile = outfile.replace('.txt', '')
        shutil.copyfile('data/'+ entry, outfile)
 

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('quarter', help='Quarter identifier (e.g., fall2016)', default=None)
    parser.add_argument('-o', '--output', help='Output directory', default=None)
    args = parser.parse_args()
    
    if args.quarter is None:
        # Default to the previous quarter
        SECONDS_IN_MONTH = 60 * 60 * 24 * 90
        args.quarter = get_season(time.time() - SECONDS_IN_MONTH)

    copy_archive(args.quarter, output=args.output)

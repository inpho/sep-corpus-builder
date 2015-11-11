import os
from glob import glob
from collections import defaultdict

def generate_archive_dict():
     entries = defaultdict(list)
     files = [os.path.basename(x) for x in glob('/home/jessiepusateri/sep-corpus-builder/data/*.txt')]
     for filename in files:
         season, article = filename.replace('.txt', ',').split('-', 1)
         entries[article].append(season)


if __name__ == '__main__':
    generate_archive_dict()

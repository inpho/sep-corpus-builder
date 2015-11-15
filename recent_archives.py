import os
import operator
from glob import glob
from collections import defaultdict

def generate_archive_dict():
     entries = defaultdict(list)
     files = [os.path.basename(x) for x in glob('/home/jessiepusateri/sep-corpus-builder/data/*.txt')]
     for filename in files:
         season, article = filename.replace('.txt', '').split('-', 1)
         entries[article].append(season)
     return entries
    
def archive_sort_function(date):
    season_order = ["spr", "sum", "fall", "win"]
    return date[-4:], season_order.index(date[:-4])
    
def sort_seasons(season_list):
    return sorted(season_list, key = archive_sort_function)

if __name__ == '__main__':
    versions = generate_archive_dict()
    for entry in versions:
        print sort_seasons(versions[entry])


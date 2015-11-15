import os
import operator
from glob import glob
from collections import defaultdict

def generate_archive_dict():
     """
     Returns a dictionary of archives and their versions:
       key: entry name
       value: a list of all the version dates associated with that entry
       For example, 'introspection': ['spr2012', 'win2010', 'spr2010'].
     """
     entries = defaultdict(list)
     files = [os.path.basename(x) for x in glob('/home/jessiepusateri/sep-corpus-builder/data/*.txt')]
     for filename in files:
         season, article = filename.replace('.txt', '').split('-', 1)
         entries[article].append(season)
     return entries

def archive_sort_function(date):
    """
      Takes in a {season}{year} date and returns a tuple to be used by the built-in sort function 
      and sorted by year and month.
      For example, sorted(['spr2012', 'win2010', 'spr2010'], key = archive_sort_function) returns 
      ['spr2010', 'win2010', 'spr2012'].
     """
    season_order = ["spr", "sum", "fall", "win"]
    return date[-4:], season_order.index(date[:-4])

if __name__ == '__main__':
    versions = generate_archive_dict()
    for entry in versions:
        print sorted(versions[entry], key = archive_sort_function)


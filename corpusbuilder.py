import os
import os.path
import logging
import sys
from codecs import open
from BeautifulSoup import BeautifulSoup
import HTMLParser
import rython
import re
from datetime import datetime
from collections import defaultdict

def get_season(timestamp):
    date = datetime.fromtimestamp(timestamp)

    if (date.month >= 3 and date.day >= 20 and
        date.month < 6 and date.day < 21):
        season = "sum"
    elif (date.month >= 6 and date.day >= 20 and
        date.month < 9 and date.day < 21):
        season = "fall"
    elif (date.month >= 9 and date.date >= 20 and
        date.month < 12 and date.day < 21):
        season = "win"
    else:
        season = "spr"

    return season + str(date.year)

def create_data_entries(unique_articles, output_dir = "/data"):
    #TODO: check if output_dir exists, if not make it
    
    for entry, season_path in unique_articles.iteritems():
        for season, path in season_path.iteritems():
            output_path = os.getcwd() + output_dir + '/' + season + '-' + entry + '.txt'
            
            # check if the index file that corresponds to the article name exists
            filename = path + 'index.html'
            if not os.path.exists(filename):
                logging.warning('No file for %s', entry)
                continue
            with open(output_path, 'a+', 'utf-8') as plainfile:
                plainfile.write(extract_article_body(path + 'index.html'))
  
        
def build_archive_corpus(codes=None):
    """
    Takes the log file for each entry and finds the corresponding archive for
    each published version or revised version. Each version is then copied into
    a single directory containing all unique versions of all articles for future 
    topic modeling.

    Returns a dictionary with keys of entry names and values of a list of 
    filenames corresponding to the unique articles.
    """
    # set default codes
    if codes is None:
        codes = ["eP101", "ep101", "eR101"]
        
    # set log path and iterate over logs, each file is a entry
    path = "/home/sep/SEPMirror/SEPMirror/usr/encyclopedia/logs"
    path = "/var/inphosemantics/sep-archives/logs"
    archive_path = '/var/inphosemantics/sep-archives/raw/{season}/entries/{entry}/'
    results = defaultdict(dict)
    for entry in os.listdir(path):
       # archives stores unique versions
        versions = set()
        with open(path+'/'+entry, 'r') as f:
            for line_num, line in enumerate(f):
                line_data = line.split("::")
                try:
                    if(line_data[2] in codes):
                        timestamp = float(line_data[1])
                        versions.add(get_season(timestamp))
                except IndexError:
                    logging.info("Index error on line: %s", line_num)
        for season in versions:
            #dictionary: key - season, value - path
            #season_path[season] = archive_path.format(season=season,
            #entry=entry)
            results[entry][season] = archive_path.format(season=season,
            entry=entry)
            #results[entry].append(archive_path.format(season=season,
            #entry=entry))
    return results

def getStyleBibliography(biblioList):
    ctx = rython.RubyContext(requires=["rubygems", "anystyle/parser"])
    ctx("Encoding.default_internal = 'UTF-8'")
    ctx("Encoding.default_external = 'UTF-8'")
    anystyle = ctx("Anystyle.parser")
    anyStyleList = []
    h =  HTMLParser.HTMLParser()
    for biblio in biblioList:
        parsed = anystyle.parse((h.unescape(biblio).encode('utf-8')))
        anyStyleList.append(parsed)
    return anyStyleList	

def extract_bibliography(filename):
	f = open(filename)
        doc = f.read()
        soup = BeautifulSoup(doc, convertEntities=["xml", "html"])
        bibliography = soup.findAll('ul',{"class":"hanging"})
        bib =[]
        if bibliography:
                for ul in bibliography:
                        for li in ul.findAll('li'):
                                bib.append(li.text)
        else:
            logging.warning("No bibliography found")

        return bib

def extract_article_body(filename):
    """
    Extracts the article body from the SEP article at the given filename. Some
    error handling is done to guarantee that this function returns at least the
    empty string. Check the error log.
    """
    try:
      f = open(filename)
      doc = f.read()
      soup = BeautifulSoup(doc, convertEntities=["xml", "html"])

      # rip out bibliography
      biblio_root = soup.findAll('h2', text='Bibliography')
      if biblio_root:
          biblio_root = biblio_root[-1].findParent('h2')
          if biblio_root:
              biblio = [biblio_root]
              biblio.extend(biblio_root.findNextSiblings())
              biblio = [elm.extract() for elm in biblio]
          else:
              logging.error('Could not extract bibliography from %s' % filename)

      # grab modified body 
      body = soup.find("div", id="aueditable")
      if body is not None:
          # remove HTML escaped characters
          body = re.sub("&\w+;", "", body.text)
          return body
      else:
          logging.error('Could not extract text from %s' % filename)
          return ''
    except:
      logging.error('File at path %s does not exist.' % filename)
      return ''
    
def process_archives():
    for root,dirs,files in os.walk("/var/inphosemantics/sep-archives/db/"):
        for sem_year in dirs:
            year = sem_year[-4:]
            if int(year) > 2006:
                path = root+sem_year+"/entries.txt"
                logging.info("Current path: %s", path) 
                build_corpus(path ,"data/" + sem_year + "/", sem_year)

if __name__ == '__main__':
    """
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Script to build a corpus from SEP id list")
    parser.add_argument("entries",
        help="SEP Entries csv or txt file")
    parser.add_argument("output",
        help="output directory for parsed corpus")
    args = parser.parse_args()

    build_corpus(args.entries, args.output)
    """
    logging.basicConfig(format='%(levelname)s:%(message)s', filename='sep_corpus.log', level = logging.INFO)
    create_data_entries(build_archive_corpus())

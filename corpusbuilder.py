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
    """
    Takes a nested dictionary that contains the information about the unique articles and 
    writes out each article body to a file of format '{season}-{entry}.txt'. For example, 
    'spr2012-epistemology.txt'
    
    See build_archive_corpus for information about the format of the nested dictionary.
    """
    #TODO: check if output_dir exists, if not make it
    
    for entry, season_path in unique_articles.iteritems():
        for season, path in season_path.iteritems():
            output_path = os.getcwd() + output_dir + '/' + season + '-' + entry + '.txt'
            
            # check if the index file that corresponds to the article name exists
            filename = path + 'index.html'
            if not os.path.exists(filename):
                logging.warning('No file for %s during %s', entry, season)
                continue
            # writes out each article body to a file
            with open(output_path, 'a+', 'utf-8') as plainfile:
                plainfile.write(extract_article_body(entry, path + 'index.html'))
  
def build_archive_corpus(codes=None):
    """
    Takes the log file for each entry and finds the corresponding archive for
    each published version or revised version. Each version is then copied into
    a single directory containing all unique versions of all articles for future 
    topic modeling.

    Returns the information about the unique articles via a dictionary:
      key: entry name
      value: dictionary:
        key': season
        value': filename corresponding to the unique article
    """
    # set default codes
    if codes is None:
        codes = ["eP100", "eP101", "ep101", "eR101"]
        
    # set log path and iterate over logs, each file is a entry
    path = "/var/inphosemantics/sep-archives/logs"
    archive_path = '/var/inphosemantics/sep-archives/raw/{season}/entries/{entry}/'
    unique_articles = defaultdict(dict)
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
            unique_articles[entry][season] = archive_path.format(season=season,
            entry=entry)
    return unique_articles

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

def get_titles():
    """
    Returns a dictionary of { sep_dir : title } pairs.
    """
    entries = "/var/inphosemantics/sep-archives/db/win2014/entries.txt"
    
    titles = {}
    with open(entries) as f:
        for line in f:
            sep_dir, title, rest = line.split('::', 2)
            title = title.replace(r"\'", "'")
            titles[sep_dir] = title

    return titles

def extract_article_body(entry, filename):
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
          body = re.sub("&\w+;", "", body.getText(' '))
          body = re.sub("DO NOT MODIFY THIS LINE AND ABOVE", "", body)
          return body
      
      #Extract differently formatted archives from before 2006 using Beautiful Soup
      else:
        #get titles from recent archive
        titles = get_titles()
        #use title to find the beginning of the article
        finder = soup.find(re.compile('^h'), text=titles[entry])
        #join together list of all the next 
        new_body = ' '.join([tag.getText(' ') for tag in finder.findAllNext()])

        if new_body:
          # remove HTML escaped characters 
          new_body = re.sub("&\w+;", "", new_body)
          return new_body
        else:
          logging.error('Could not extract text from %s' % filename)
          return ''
    except:
      logging.error('File at path %s does not exist.' % filename)
      return ''


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
    logging.basicConfig(format='%(levelname)s:%(message)s', filename='sep_corpus.log', level = logging.WARNING)
    create_data_entries(build_archive_corpus())

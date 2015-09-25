import os
import os.path
import logging
import sys
from codecs import open
from BeautifulSoup import BeautifulSoup
import HTMLParser
import rython
import re

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

def process_archives():
    for root,dirs,files in os.walk("/var/inphosemantics/sep-archives/db/"):
        for sem_year in dirs:
            year = sem_year[-4:]
            if int(year) > 2006:
                path = root+sem_year+"/entries.txt"
                logging.info("Current path: %s", path) 
                build_corpus(path ,"data/" + sem_year + "/", sem_year);

def extract_article_body(filename):
    """
    Extracts the article body from the SEP article at the given filename. Some
    error handling is done to guarantee that this function returns at least the
    empty string. Check the error log.
    """
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

def build_corpus(entriesfile, output_dir,sem_year):
    # check if output_dir exists, if not make it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # keep of tally of the successful reads
    success_read = 0
    with open(entriesfile, 'rb') as csvfile:
        for row in csvfile:
            sep_dir = row.split("::")[0]
            filename="/var/inphosemantics/sep-archives/raw/"+sem_year+"/entries/"+sep_dir+"/index.html"
            if not os.path.exists(filename):
                logging.warning('No file for %s', sep_dir)
                continue
            else:
                success_read = success_read + 1
            plain_filename = os.path.join(output_dir, '%s.txt' % sep_dir)
            with open(plain_filename, 'wb', 'utf-8') as plainfile:
                plainfile.write(extract_article_body(filename))
        logging.info("Successful reads: %d", success_read)

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
    process_archives()

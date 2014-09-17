import os
import os.path
import sys
from codecs import open

def process_archives():
    for root,dirs,files in os.walk("/Users/sep/SEPMirror/usr/encyclopedia/archives/"):
        path = root+"/entries.txt"
        sem_year = root.split('/')[7]
        build_corpus(path ,"/some folder path",sem_year);

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

        return '':


def build_corpus(entriesfile, output_dir,sem_year):
    # check if output_dir exists, if not make it
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    with open(entriesfile, 'rb') as csvfile:
        for row in csvfile:
            sep_dir = row.split("::")[0]
            filename="/Users/sep/SEPMirror/usr/etc/httpd/htdocs/archives/"+sem-year+"/entries/"+sep_dir+"/index.html"
            if not filename:
                print "NO FILE FOR", sep_dir
                continue
            plain_filename = os.path.join(output_dir, '%s.txt' % sep_dir)
            with open(plain_filename, 'wb', 'utf-8') as plainfile:
                plainfile.write(extract_article_body(filename))

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Script to build a corpus from SEP id list")
    parser.add_argument("entries",
        help="SEP Entries csv or txt file")
    parser.add_argument("output",
        help="output directory for parsed corpus")
    args = parser.parse_args()

    build_corpus(args.entries, args.output)

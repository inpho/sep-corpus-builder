import os
import os.path
import sys

import inpho.corpus.sep as sep
from codecs import open

def build_corpus(entriesfile, output_dir):
    # check if output_dir exists, if not make it
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    with open(entriesfile, 'rb') as csvfile:
        for row in csvfile:
            sep_dir = row.split("::")[0]
            filename = sep.article_path(sep_dir)
            if not filename:
                print "NO FILE FOR", sep_dir
                continue
            plain_filename = os.path.join(output_dir, '%s.txt' % sep_dir)
            with open(plain_filename, 'wb', 'utf-8') as plainfile:
                plainfile.write(sep.extract_article_body(filename))

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Script to build a corpus from SEP id list")
    parser.add_argument("entries",
        help="SEP Entries csv or txt file")
    parser.add_argument("output",
        help="output directory for parsed corpus")
    args = parser.parse_args()

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    build_corpus(args.entries, args.output)

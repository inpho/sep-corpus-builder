import os
import os.path
import sys

import inpho.corpus.sep as sep
from codecs import open

def get_season(timestamp):
    value = datetime.datetime.fromtimestamp(timestamp)
    #print(value.strftime('%Y-%m-%d %H:%M:%S'))
    #print(value.strftime('%m'))
    # convert date to month and day as integer (md), e.g. 4/21 = 421, 11/17 = 1117, etc.
    y = value.strftime('%Y')
    m = int(value.strftime('%m')) * 100
    d = int(value.strftime('%d'))
    md = m + d
    
    if ((md > 320) and (md < 621)):
        s = "sum"
    elif ((md > 620) and (md < 921)):
        s = "fall"
    elif ((md > 920) and (md < 1221)):
        s = "win"
    else:
        s = "spr"

    return s+y



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

def build_archive_corpus(codes=None):
    if codes is None:
        codes = ["eP101", "ep101", "eR101"]
    path = "/home/sep/SEPMirror/SEPMirror/usr/encyclopedia/logs"
    for file in os.listdir(path):
        archives = set();
        with open(path+'/'+file, 'r') as f:
            for line in f:
                line_data = line.split("::")
                try:
                    if(line_data[2] in codes):
                        timestamp = float(line_data[1])
                        #print timestamp
                        archives.add(get_season(timestamp))
                except IndexError:
                    print "Index error"
            
            for year in archives:
                try:
                    src = "/home/rzawar/data/"+year+"/"+file+".txt"
                    dest = "/home/jammurdo/separchive/"+year+"-"+file+".txt"
                    shutil.copyfile(src,dest)
                except IOError:
                    with open("errorNoExist.txt", 'a') as ferror:
                        ferror.write("cannot find "+src+"\n")

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Script to build a corpus from SEP id list")
    parser.add_argument("--archives", help="create archives")
    parser.add_argument("entries",
        help="SEP Entries csv or txt file")
    parser.add_argument("output",
        help="output directory for parsed corpus")
    args = parser.parse_args()

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    build_corpus(args.entries, args.output)

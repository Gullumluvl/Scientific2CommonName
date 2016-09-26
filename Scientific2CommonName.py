#!/usr/bin/env python

""" Converts common species names to scientific, and conversely.
Can take one name per line from stdin"""

import requests
import bs4
import argparse
import fileinput

url = "http://www.ncbi.nlm.nih.gov/taxonomy/"
nametype = "Scientific Name"
report = "info"


def main(names, nametype=None):
    searchedfield = 'Scientific Name:' if nametype == 'Common Name' else 'genbank common name:'
    # Check if names are given as arguments of the script. If not, read stdin.
    # TODO: error when no data provided to stdin after some time lapse.
    if not names: names = [line.rstrip() for line in fileinput.input(('-',))]
    for name in names:
        data = {"term": "%s[%s]" % (name, nametype),
                "report": report} 
        #print data
        r = requests.post(url, data=data)
        if r.status_code != requests.codes.ok:
            raise r.raise_for_status()
        soup = bs4.BeautifulSoup(r.text, 'lxml')
        #print soup.dl
        out = 'NA'
        for dl in soup.findAll('dl'): # description lists
            if dl.dt.text == searchedfield:
                out = dl.dd.text
                break
        print out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-c", "--common", action='store_const', 
                        dest="nametype", const="Common Name",
                        default="Scientific Name",
                        help="Indicate your input is the common name (default: scientific)")
    parser.add_argument("names", nargs='*', help="species names to convert, if empty, read from stdin")
    args = parser.parse_args()
    #print args
    main(**vars(args))


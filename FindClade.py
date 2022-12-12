#!/usr/bin/env python


from __future__ import print_function


""" Takes a taxonomical term (scientific/common species name), and returns
a higher clade name (family, order, phylum...)"""


import sys
import requests
import bs4
import argparse
import fileinput


# Seem to be forbidden when not http secure.
URL = "https://www.ncbi.nlm.nih.gov/taxonomy/"
URL_ASSEMBLY = "https://www.ncbi.nlm.nih.gov/assembly/"
REPORT = "info"


def main(names, level='family', http=False, na='NA', assembly=False):
    # Check if names are given as arguments of the script. If not, read stdin.
    # TODO: error when no data provided to stdin after some time lapse.
    url = URL.replace('https', 'http') if http else URL
    if not names: names = [line.rstrip() for line in fileinput.input(('-',))]
    for name in names:
        data = {"term": "%s" % name,
                "report": REPORT}
        r = requests.post(url, data=data)
        if not r.ok:
            print("Reason:", r.reason, file=sys.stderr)
            raise r.raise_for_status()
        soup = bs4.BeautifulSoup(r.text, 'lxml')
        out = na
        for dl in soup.findAll('dl'): # description lists
            if dl.dt.text == "Lineage:": # title of the description list item
                for a in dl.findAll('a'): # link
                    atitle = a.attrs.get('title')
                    if atitle == level:
                        out = a.text
                        break
                break
        print(out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-l", "--level", default="family",
                        help="taxonomic level to fetch [%(default)s]")
    parser.add_argument("names", nargs='*',
                        help="species names to convert, if empty, read from stdin")
    parser.add_argument("--http", action='store_true',
                        help="Use http:// instead of https://")
    parser.add_argument("--NAempty", action='store_const', dest='na',
                        const='', default='NA',
                        help="prints the empty string when not found (otherwise %(default)r)")
    args = parser.parse_args()
    main(**vars(args))

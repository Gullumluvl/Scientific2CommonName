#!/usr/bin/env python2.7

""" Converts common species names to scientific, and conversely.
Can take one name per line from stdin"""

import requests
import bs4
import argparse
import fileinput

URL = "https://www.ncbi.nlm.nih.gov/taxonomy/"
#url = "http://www.ncbi.nlm.nih.gov/taxonomy/"
REPORT = "info"


def main(names, inputtype=None, searchedfield='Scientific Name', rank=None):
    #searchedfield = 'Scientific Name:' if inputtype != 'Scientific Name' else 'genbank common name:'
    # Check if names are given as arguments of the script. If not, read stdin.
    # TODO: error when no data provided to stdin after some time lapse.
    if not names: names = [line.rstrip() for line in fileinput.input(('-',))]
    for name in names:
        data = {"term": "%s[%s]" % (name, inputtype) if inputtype else name,
                "report": REPORT} 
        #print data
        r = requests.post(URL, data=data)
        if r.status_code != requests.codes.ok:
            raise r.raise_for_status()
        soup = bs4.BeautifulSoup(r.text, 'lxml')
        #print soup.dl
        out = []
        for rslt in soup.findAll('div', attrs={'class': 'rslt'}): 
            rank_out = rslt.findNext('dt', text='Rank:').parent.dd.text
            found = rslt.findAll('dt', text=(searchedfield+':'))
            if not found:
                #raise KeyError("Invalid searched field: %r" % searchedfield)
                found = [None]

            assert len(found) == 1
            found, = found

            if found is None:
                rslt_out = 'None'
            else:
                rslt_out = ';'.join(dd.text for dd in found.parent.findAll('dd'))

            if not rank or rank_out == rank:
                out.append(rslt_out)

        if not out:
            out = ['NA']

        print '\t'.join(out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-c", "--common", action='store_const', 
                        dest="searchedfield", const="genbank common name",
                        default="Scientific Name",
                        help="Search for the genbank common name") # (default: scientific)")
    parser.add_argument("-t", "--taxid", action='store_const', 
                        dest="searchedfield", const="Taxonomy ID",
                        default="Scientific Name",
                        help="Search for the taxonomy id") # (default: scientific)")
    parser.add_argument("-s", "--synonym", action='store_const', 
                        dest="searchedfield", const="synonym",
                        default="Scientific Name",
                        help="Search for the synonymous scientific names") # (default: scientific)")
    parser.add_argument("-l", "--lineage", action='store_const', 
                        dest="searchedfield", const="Lineage",
                        default="Scientific Name",
                        help="Search for the lineage") # (default: scientific)")
    parser.add_argument("-i", "--inputtype", choices=["Scientific Name", "Common Name", "genbank common name", "Synonym", "Taxonomy ID"],
                        help="Specify the input type.")
    parser.add_argument("-r", "--rank", help="Limit output to the matching ranks (species, genus, class, etc)")
    parser.add_argument("names", nargs='*', help="species names to convert, if empty, read from stdin")
    args = parser.parse_args()
    #print args
    main(**vars(args))


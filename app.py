import os, sys, getopt, time
from subprocess import Popen, PIPE
import subprocess, urllib2, re
import itertools
from bs4 import BeautifulSoup
from constants import CATEGORIES, ORDERS
from tpb import TPB
from flask import Flask, jsonify, request


app = Flask(__name__)

@app.route('/', methods=['POST', 'OPTIONS'])
def whf_scrape():

    content = request.get_json()

    if content != {}:
        res = {}

        keywords = get_keywords(content['url'])

        # combs = create_combinations(keywords)
        # for c in list(combs):
        #     print c

        # create TPB object
        # t = TPB('https://thepiratebay.org')




        return jsonify(res)


    return jsonify('Provide valid URL')



def get_keywords(url):

    # get page html
    page_html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page_html, "lxml")

    # get title
    title = soup.findAll('div', attrs={'class':'post-title'})[0].find('h1').text

    # extract keywords from title
    keywords = [kw.strip().split(' ') for kw in re.sub(r'\([^)]*\)', '', title).replace(',', '').split(' - ')]

    # flatten keywords
    flattened_kw = list(set([k.lower() for sublist in keywords for k in sublist if k.lower() not in ['and', 'with']]))

    # remove doubles
	# TODO

    return flattened_kw



def create_combinations(kw_list):
    return itertools.combinations(kw_list, 2)




def find_torrents(pattern, tpb):

    torrents = []

    # perform search using TPB API
    search = tpb.search(pattern).order(ORDERS.SEEDERS.DES)

    if search:
        for torrent in search:
            torrents.append({'title': torrent.title,
                             'magnet': torrent.magnet_link,
                             'seeders': torrent.seeders,
                             'size': torrent.size})

    return torrents




if __name__ == '__main__':
    app.run(use_reloader=True, port=3000)

import urllib2, re, itertools
from bs4 import BeautifulSoup
from tpb import TPB
from constants import CATEGORIES, ORDERS
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import logging

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST', 'OPTIONS'])
@cross_origin()
def scrape():

	content = request.get_json()

	if content != {}:
		res = {}
		
		keywords = get_keywords(content['page_url'])    
		unique_kws = create_unique_combinations(keywords)
		
		tpb, torrents = TPB('https://thepiratebay.org'), []
		
		for kw in unique_kws:
			existing_magnets = [t['magnet'] for t in torrents]
			new_torrents = find_torrents('{} {}'.format(kw[0], kw[1]), tpb)
			
			for t in new_torrents:
				if t['magnet'] not in existing_magnets:
					torrents.append(t)
			
		torrents = sorted(torrents, key=lambda torrent: (torrent['seeders']))[-3:]


		return jsonify(torrents)
		
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
    flattened_kw = set(flattened_kw)

    return flattened_kw



def create_unique_combinations(kw_list):
    return set([tuple(i) for i in map(sorted, itertools.combinations(kw_list, 2))])




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

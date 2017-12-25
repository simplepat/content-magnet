'use strict'

const torrentsPane = document.getElementById('torrents-pane')
const configPane = document.getElementById('config-pane')


for (const opener of document.querySelectorAll('.config-opener')) {
	opener.addEventListener('click', e => {
		browser.runtime.openOptionsPage()
	})
}

function showConfig (server) {
	// Prompts pane with link to configure remote server
	torrentsPane.hidden = true
	configPane.hidden = false
}

const torrentsList = document.getElementById('torrents-list')
const torrentsError = document.getElementById('torrents-error')


function refreshTorrents (server, url) {
		
	return browser.storage.local.get('server').then(({server}) => {
		
		function createNode(element) {
		  return document.createElement(element);
		}

		function append(parent, el) {
			return parent.appendChild(el);
		}
		
		function timeout(ms, promise) {
		  return new Promise(function(resolve, reject) {
			setTimeout(function() {
			  reject(new Error("timeout"))
			}, ms)
			promise.then(resolve, reject)
		  })
		}
		
		
		browser.tabs.query({active: true, currentWindow: true}).then((tabs) => {
			var packe = tabs[0].url;
			
			console.log(packe);
			
			// Create our request constructor with all the parameters we need
			var request = new Request(server.base_url, {
				headers: {
				  'Accept': 'application/json',
				  'Content-Type': 'application/json'
				},
				method: 'POST',
				body: JSON.stringify({page_url: packe})
			});
		

			timeout(15000, fetch(request))
			.then((resp) => resp.json())
			.then(function(data) {
				
				let torrents = data;
				document.getElementById('torrents-list').innerHTML = "";
				
				return torrents.map(function(torrent) {
					let li = createNode('li'),
					span = createNode('span'),
					img = createNode('img'),
					a = createNode('a');
					
					img.src = "icons/magnet.png";
					a.href = `${torrent.magnet}`;
					span.innerHTML = `${torrent.seeders} ${torrent.title} ${torrent.size}`;
					append(a, img);
					append(li, a);
					append(li, span);
					append(torrentsList, li);
				})
			});	
		}).catch(function(error) {
			console.log(error);
		});
	})
}

function refreshTorrentsLogErr (server) {
	return refreshTorrents(server).catch(err => {
		console.error(err)
		torrentsError.textContent = 'Error: ' + err.toString()
	})
}

function showTorrents (server, url) {
	
	// show torrents pane
	torrentsPane.hidden = false
	configPane.hidden = true
	
	// replace link to transmission server with link from server
	for (const opener of document.querySelectorAll('.webui-opener')) {
		opener.href = 'https://github.com/simplepat/content-magnet'
	}
	
	// try to refresh torrents pane, otherwise throw error
	refreshTorrents(server, url).catch(_ => refreshTorrentsLogErr(server))
	
}

browser.storage.local.get('server').then(({server}) => {
	/* if flask server url is set in browser storage, use it to perform request
	 *	otherwise redirect to options page to configure it
	 */
	if (server && server.base_url && server.base_url !== '') {
		showTorrents(server)
	} else {
		showConfig(server)
	}
})

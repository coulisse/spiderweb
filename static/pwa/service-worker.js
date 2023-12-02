// Dichiarazione della costante per il nome della cache
const CACHE_NAME = 'pwa-spiderweb_v2.5.2'

// Dichiarazione della costante per gli URL da mettere in cache
const URLS_TO_CACHE = [
	'/static/images/background.webp',
	'/static/css/rel/style.min.css',
	'/static/images/icons/favicon.ico',
	'/static/images/icons/icon-144x144.png',
	'/static/images/icons/icon-152x152.png',
	'/static/images/icons/icon-192x192.png',
	'/static/images/icons/icon-128x128.png',
	'/static/images/icons/icon-256x256.png',
	'/static/images/icons/icon-384x384.png',
	'/static/images/icons/icon-512x512-solid.png',
	'/static/images/icons/icon-512x512-transparent.png',
	'/static/images/icons/icon-72x72.png',
	'/static/images/icons/icon-96x96.png',
	'/static/images/icons/icon-apple.png',
	'/static/images/icons/spider_ico_master.svg',
	'/static/js/rel/callsign_inline.min.js',
	'/static/js/rel/callsign_search.min.js',
	'/static/js/rel/common.min.js',
	'/index.html',	
	'/plots.html',		
	'/privacy.html',
	'/cookies.html'
];


// Install
self.addEventListener('install', event => {
	event.waitUntil(
		caches.open(CACHE_NAME)
			.then(cache => {
				return cache.addAll(URLS_TO_CACHE);
			})
	);
});

// Activation
self.addEventListener('activate', event => {
	event.waitUntil(
		caches.keys().then(cacheNames => {
			return Promise.all(
				cacheNames.map(cacheName => {
					if (cacheName !== CACHE_NAME) {
						return caches.delete(cacheName);
					}
				})
			);
		})
	);
});

//Managing request
self.addEventListener('fetch', event => {
	console.log(event.request.url);				
	event.respondWith(
		caches.match(event.request)
			.then(response => {
				if (response) {
					return response;
				}
				return fetch(event.request)
					.then(response => {
						if (response.status === 502) {
							console.log("response status: " + response.status);
							return caches.match('/index.html');
						}
						if (!response || response.status !== 200 || response.type !== 'basic') {
							console.log("response: " + response.status);
							return response;
						}
						let responseToCache = response.clone();
						caches.open(CACHE_NAME)
							.then(cache => {
								cache.put(event.request, responseToCache);
							});
						return response;
					})
					.catch(error => {
						console.log(error);
						return caches.match('/index.html');
					});
			})
	);
});
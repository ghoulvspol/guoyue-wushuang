const CACHE_NAME = 'guoyue-wushuang-v8';
const CORE_ASSETS = [
  './',
  'index.html',
  'static/styles.css?v=8',
  'static/app.js?v=8',
  'manifest.webmanifest',
  'static/data/instruments.json',
  'static/photos/bianzhong.jpg',
  'static/photos/bo.jpg',
  'static/photos/dizi.jpg',
  'static/photos/erhu.jpg',
  'static/photos/guqin.jpg',
  'static/photos/guzheng.jpg',
  'static/photos/hulusi.jpg',
  'static/photos/konghou.jpg',
  'static/photos/matouqin.jpg',
  'static/photos/pipa.jpg',
  'static/photos/sanxian.jpg',
  'static/photos/sheng.jpg',
  'static/photos/suona.jpg',
  'static/photos/xiao.jpg',
  'static/photos/xun.jpg',
  'static/photos/yangqin.jpg',
  'static/photos/zhongruan.jpg',
];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(CORE_ASSETS)));
  self.skipWaiting();
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key)))));
  self.clients.claim();
});
self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.pathname.includes('/api/')) {
    event.respondWith(fetch(request));
    return;
  }
  event.respondWith(fetch(request).then(response => {
    const copy = response.clone();
    caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
    return response;
  }).catch(() => caches.match(request).then(cached => cached || caches.match('./'))));
});

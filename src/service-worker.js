const CACHE_NAME = "wortlauf-v0.0.28";
const APP_FILES = [
  "./", "./index.html", "./manifest.webmanifest", "./icon.svg", "./config.json",
  "./wordbank/adjectives.json",
  "./wordbank/adverbs.json",
  "./wordbank/animals.json",
  "./wordbank/body.json",
  "./wordbank/city.json",
  "./wordbank/clothing.json",
  "./wordbank/colors.json",
  "./wordbank/communication.json",
  "./wordbank/countries.json",
  "./wordbank/culture.json",
  "./wordbank/drinks.json",
  "./wordbank/emotions.json",
  "./wordbank/everyday.json",
  "./wordbank/food.json",
  "./wordbank/function.json",
  "./wordbank/garden.json",
  "./wordbank/grammar.json",
  "./wordbank/health.json",
  "./wordbank/hobbies.json",
  "./wordbank/home.json",
  "./wordbank/index.json",
  "./wordbank/kitchen.json",
  "./wordbank/learning.json",
  "./wordbank/life.json",
  "./wordbank/materials.json",
  "./wordbank/media.json",
  "./wordbank/modals.json",
  "./wordbank/money.json",
  "./wordbank/music.json",
  "./wordbank/nature.json",
  "./wordbank/numbers.json",
  "./wordbank/office.json",
  "./wordbank/people.json",
  "./wordbank/personality.json",
  "./wordbank/prepositions.json",
  "./wordbank/restaurant.json",
  "./wordbank/science.json",
  "./wordbank/sentence-builder.json",
  "./wordbank/shopping.json",
  "./wordbank/society.json",
  "./wordbank/spelling.json",
  "./wordbank/sport.json",
  "./wordbank/technology.json",
  "./wordbank/time.json",
  "./wordbank/tools.json",
  "./wordbank/transport.json",
  "./wordbank/travel.json",
  "./wordbank/verbs.json",
  "./wordbank/weather.json",
  "./wordbank/work.json",
  "./levels/chapter-1.json",
  "./levels/chapter-2.json",
  "./levels/index.json"
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_FILES)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))))
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  if (event.request.mode === "navigate") {
    event.respondWith(fetch(event.request).then((response) => {
      if (response.ok) {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
      }
      return response;
    }).catch(() => caches.match(event.request)));
    return;
  }
  if (url.hostname === "localhost" || url.hostname === "127.0.0.1") {
    event.respondWith(fetch(event.request));
    return;
  }
  if (url.origin === self.location.origin && url.pathname.endsWith(".json")) {
    const key = url.origin + url.pathname;
    event.respondWith(fetch(event.request).then((response) => {
      if (response.ok) {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(key, copy));
      }
      return response;
    }).catch(() => caches.match(event.request, { ignoreSearch: true })));
    return;
  }
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request).then((response) => {
      if (response.ok && new URL(event.request.url).origin === self.location.origin) {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
      }
      return response;
    }))
  );
});
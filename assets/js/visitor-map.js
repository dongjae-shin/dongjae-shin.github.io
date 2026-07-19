document.addEventListener("readystatechange", () => {
  if (document.readyState !== "complete") return;

  const mapElement = document.getElementById("visitor-map");
  const dataElement = document.getElementById("visitor-stats-data");
  const modeSelect = document.getElementById("visitor-map-mode");
  if (!mapElement || !dataElement || typeof L === "undefined") return;

  const stats = JSON.parse(dataElement.textContent || "{}");
  const map = L.map(mapElement, {
    worldCopyJump: true,
    minZoom: 2,
  }).setView([20, 0], 2);

  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map);

  const layer = L.layerGroup().addTo(map);
  const greenIcon = L.divIcon({
    className: "visitor-pin",
    html: '<span class="visitor-pin-dot"></span>',
    iconSize: [28, 40],
    iconAnchor: [14, 38],
    popupAnchor: [0, -34],
  });

  const countryCenters = {
    AU: [-25.2744, 133.7751],
    BR: [-14.235, -51.9253],
    CA: [56.1304, -106.3468],
    CN: [35.8617, 104.1954],
    DE: [51.1657, 10.4515],
    FR: [46.2276, 2.2137],
    GB: [55.3781, -3.436],
    IE: [53.4129, -8.2439],
    IN: [20.5937, 78.9629],
    JP: [36.2048, 138.2529],
    KR: [35.9078, 127.7669],
    NL: [52.1326, 5.2913],
    SG: [1.3521, 103.8198],
    US: [39.8283, -98.5795],
  };

  const cityCenters = {
    "Ashburn|US": [39.0438, -77.4874],
    "Atlanta|US": [33.749, -84.388],
    "Boston|US": [42.3601, -71.0589],
    "Chicago|US": [41.8781, -87.6298],
    "Dublin|IE": [53.3498, -6.2603],
    "London|GB": [51.5072, -0.1276],
    "Los Angeles|US": [34.0522, -118.2437],
    "New York|US": [40.7128, -74.006],
    "Palo Alto|US": [37.4419, -122.143],
    "San Francisco|US": [37.7749, -122.4194],
    "São Paulo|BR": [-23.5558, -46.6396],
    "Seoul|KR": [37.5665, 126.978],
    "Singapore|SG": [1.3521, 103.8198],
    "Sydney|AU": [-33.8688, 151.2093],
    "Tokyo|JP": [35.6762, 139.6503],
  };

  const coordFor = (item, mode) => {
    if (Number.isFinite(item.latitude) && Number.isFinite(item.longitude)) return [item.latitude, item.longitude];
    if (mode === "city") {
      const cityKey = `${item.city}|${item.country_id}`;
      if (cityCenters[cityKey]) return cityCenters[cityKey];
    }
    return countryCenters[item.country_id] || null;
  };

  const rowsForMode = (mode) => (mode === "country" ? stats.countries || [] : stats.cities || []);

  const render = (mode) => {
    layer.clearLayers();
    const bounds = [];

    rowsForMode(mode).forEach((item) => {
      const coord = coordFor(item, mode);
      if (!coord) return;

      const label = mode === "country" ? item.country : `${item.country}${item.city && item.city !== "(not set)" ? `, ${item.city}` : ""}`;
      const marker = L.marker(coord, { icon: greenIcon }).bindPopup(
        `<strong>${label}</strong><br>${item.active_users} visitor${item.active_users === 1 ? "" : "s"}`
      );
      marker.addTo(layer);
      bounds.push(coord);
    });

    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 5 });
    } else {
      map.setView([20, 0], 2);
    }
  };

  modeSelect?.addEventListener("change", (event) => render(event.target.value));
  render(modeSelect?.value || "city");
});

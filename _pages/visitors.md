---
layout: page
permalink: /visitors/
title: visitors
description:
nav: true
nav_order: 5.5
map: true
visitor_map: true
---

{% assign stats = site.data.visitor_stats %}

<div class="visitor-stats">
  <div class="visitor-map-shell">
    <div id="visitor-map" class="visitor-map" aria-label="Visitor locations map"></div>
    <div class="visitor-map-filter">
      <label for="visitor-map-mode">Filter By</label>
      <select id="visitor-map-mode">
        <option value="city">City</option>
        <option value="country">Country</option>
      </select>
    </div>
  </div>

  <div class="visitor-summary">
    <div class="visitor-summary-item">
      <span class="visitor-summary-label">All time</span>
      <strong>{{ stats.date_ranges.all_time.active_users | default: 0 }}</strong>
    </div>
    <div class="visitor-summary-item">
      <span class="visitor-summary-label">Last 30 days</span>
      <strong>{{ stats.date_ranges.last_30_days.active_users | default: 0 }}</strong>
    </div>
    <div class="visitor-summary-item">
      <span class="visitor-summary-label">Last updated</span>
      <strong>{% if stats.configured %}{{ stats.updated_at | date: '%Y-%m-%d' }}{% else %}Not configured{% endif %}</strong>
    </div>
  </div>

{% unless stats.configured %}

<p class="text-muted">Visitor statistics are not configured yet. The map will populate after Google Analytics secrets are added and the updater runs.</p>
{% endunless %}

  <div class="visitor-tables">
    <div class="visitor-table-panel">
      <div class="visitor-table-heading">City</div>
      <div class="table-responsive">
        <table class="table table-sm mb-0">
          <tbody>
            {% for city in stats.cities %}
              <tr>
                <td class="visitor-count">{{ city.active_users }}</td>
                <td>{{ city.country }}{% if city.city and city.city != '(not set)' %}, {{ city.city }}{% endif %}</td>
              </tr>
            {% endfor %}
            {% if stats.cities.size == 0 %}
              <tr>
                <td colspan="2" class="text-muted">No city data available yet.</td>
              </tr>
            {% endif %}
          </tbody>
        </table>
      </div>
    </div>

    <div class="visitor-table-panel">
      <div class="visitor-table-heading">Country</div>
      <div class="table-responsive">
        <table class="table table-sm mb-0">
          <tbody>
            {% for country in stats.countries %}
              <tr>
                <td class="visitor-count">{{ country.active_users }}</td>
                <td>{{ country.country }}</td>
              </tr>
            {% endfor %}
            {% if stats.countries.size == 0 %}
              <tr>
                <td colspan="2" class="text-muted">No country data available yet.</td>
              </tr>
            {% endif %}
          </tbody>
        </table>
      </div>
    </div>

  </div>

  <script id="visitor-stats-data" type="application/json">
    {{ stats | jsonify }}
  </script>
</div>

<style>
  .visitor-map-shell {
    position: relative;
    border-top: 4px solid #007fac;
    box-shadow: 0 1px 3px rgb(0 0 0 / 18%);
  }

  .visitor-map {
    width: 100%;
    height: min(58vh, 560px);
    min-height: 360px;
    background: #bfdde7;
    overflow: hidden;
  }

  .visitor-map .leaflet-pane,
  .visitor-map .leaflet-tile,
  .visitor-map .leaflet-marker-icon,
  .visitor-map .leaflet-marker-shadow,
  .visitor-map .leaflet-tile-container,
  .visitor-map .leaflet-pane > svg,
  .visitor-map .leaflet-pane > canvas,
  .visitor-map .leaflet-zoom-box,
  .visitor-map .leaflet-image-layer,
  .visitor-map .leaflet-layer {
    position: absolute;
    top: 0;
    left: 0;
  }

  .visitor-map .leaflet-tile,
  .visitor-map .leaflet-marker-icon,
  .visitor-map .leaflet-marker-shadow {
    max-width: none !important;
    max-height: none !important;
  }

  .visitor-map .leaflet-pane {
    z-index: 400;
  }

  .visitor-map .leaflet-tile-pane {
    z-index: 200;
  }

  .visitor-map .leaflet-overlay-pane {
    z-index: 400;
  }

  .visitor-map .leaflet-shadow-pane {
    z-index: 500;
  }

  .visitor-map .leaflet-marker-pane {
    z-index: 600;
  }

  .visitor-map .leaflet-tooltip-pane {
    z-index: 650;
  }

  .visitor-map .leaflet-popup-pane {
    z-index: 700;
  }

  .visitor-map .leaflet-map-pane canvas {
    z-index: 100;
  }

  .visitor-map .leaflet-map-pane svg {
    z-index: 200;
  }

  .visitor-map .leaflet-control {
    position: relative;
    z-index: 800;
    float: left;
    clear: both;
    pointer-events: auto;
  }

  .visitor-map .leaflet-top,
  .visitor-map .leaflet-bottom {
    position: absolute;
    z-index: 1000;
    pointer-events: none;
  }

  .visitor-map .leaflet-top {
    top: 0;
  }

  .visitor-map .leaflet-right {
    right: 0;
  }

  .visitor-map .leaflet-bottom {
    bottom: 0;
  }

  .visitor-map .leaflet-left {
    left: 0;
  }

  .visitor-map .leaflet-control-zoom {
    margin-top: 10px;
    margin-left: 10px;
    border: 2px solid rgb(0 0 0 / 20%);
    border-radius: 4px;
    background: #fff;
  }

  .visitor-map .leaflet-control-zoom a {
    display: block;
    width: 30px;
    height: 30px;
    color: #111;
    font: bold 18px/30px Arial, sans-serif;
    text-align: center;
    text-decoration: none;
    background: #fff;
    border-bottom: 1px solid #ccc;
  }

  .visitor-map .leaflet-control-zoom a:last-child {
    border-bottom: 0;
  }

  .visitor-map .leaflet-control-attribution {
    margin: 0;
    padding: 0 5px;
    color: #333;
    font-size: 11px;
    line-height: 1.4;
    background: rgb(255 255 255 / 80%);
  }

  .visitor-map-filter {
    position: absolute;
    top: 1rem;
    right: 1rem;
    z-index: 500;
    display: flex;
    align-items: center;
    background: #fff;
    border-radius: 4px;
    box-shadow: 0 1px 6px rgb(0 0 0 / 30%);
    overflow: hidden;
  }

  .visitor-map-filter label {
    margin: 0;
    padding: 0.65rem 0.75rem;
    color: #555;
    border-right: 1px solid #e5e5e5;
  }

  .visitor-map-filter select {
    height: 2.7rem;
    padding: 0 2rem 0 0.75rem;
    border: 0;
    color: #117da7;
    font-weight: 600;
    background: #fff;
  }

  .visitor-summary {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
  }

  .visitor-summary-item {
    padding: 1rem;
    border: 1px solid var(--global-divider-color);
    border-radius: 6px;
  }

  .visitor-summary-label {
    display: block;
    color: var(--global-text-color-light);
    font-size: 0.9rem;
  }

  .visitor-summary-item strong {
    display: block;
    margin-top: 0.25rem;
    font-size: 1.5rem;
  }

  .visitor-tables {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1.5rem;
  }

  .visitor-table-panel {
    border: 1px solid var(--global-divider-color);
  }

  .visitor-table-heading {
    padding: 0.75rem 1rem;
    color: #fff;
    font-weight: 700;
    background: #007fac;
  }

  .visitor-table-panel td {
    vertical-align: middle;
  }

  .visitor-pin {
    position: relative;
    width: 28px;
    height: 40px;
  }

  .visitor-pin::before {
    position: absolute;
    inset: 0;
    content: "";
    background: #1dab34;
    border: 1px solid #168f2b;
    border-radius: 50% 50% 50% 0;
    box-shadow: 0 2px 5px rgb(0 0 0 / 35%);
    transform: rotate(-45deg);
  }

  .visitor-pin-dot {
    position: absolute;
    top: 8px;
    left: 8px;
    z-index: 1;
    width: 10px;
    height: 10px;
    background: #fff;
    border-radius: 50%;
  }

  .visitor-count {
    width: 4rem;
    color: #007fac;
    font-weight: 700;
    text-align: right;
  }

  @media (max-width: 768px) {
    .visitor-map {
      min-height: 320px;
    }

    .visitor-summary,
    .visitor-tables {
      grid-template-columns: 1fr;
    }

    .visitor-map-filter {
      top: 0.75rem;
      right: 0.75rem;
    }
  }
</style>

---
layout: page
permalink: /visitors/
title: visitors
description:
nav: true
nav_order: 5.5
---

{% assign stats = site.data.visitor_stats %}

<div class="visitor-stats">
  {% if stats.configured %}
    <div class="row">
      <div class="col-md-6 mb-3">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title mb-2">All time</h5>
            <p class="display-4 mb-1">{{ stats.date_ranges.all_time.active_users }}</p>
            <p class="text-muted mb-0">{{ stats.date_ranges.all_time.start_date }} to {{ stats.date_ranges.all_time.end_date }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-6 mb-3">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title mb-2">Last 30 days</h5>
            <p class="display-4 mb-1">{{ stats.date_ranges.last_30_days.active_users }}</p>
            <p class="text-muted mb-0">{{ stats.date_ranges.last_30_days.start_date }} to {{ stats.date_ranges.last_30_days.end_date }}</p>
          </div>
        </div>
      </div>
    </div>

    <p class="text-muted">Last updated: {{ stats.updated_at }}</p>

    <div class="table-responsive">
      <table class="table table-sm table-hover">
        <thead>
          <tr>
            <th scope="col">Country</th>
            <th scope="col" class="text-right">Visitors</th>
          </tr>
        </thead>
        <tbody>
          {% for country in stats.countries %}
            <tr>
              <td>{{ country.country }}</td>
              <td class="text-right">{{ country.active_users }}</td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>

{% else %}

<p>Visitor statistics are not configured yet.</p>
{% endif %}

</div>

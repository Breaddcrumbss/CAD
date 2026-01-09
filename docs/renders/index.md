---
layout: default
title: Renders
---

# Design Renders

Automatically generated renders from all boat configurations.

{% assign render_files = site.static_files | where_exp: "file", "file.path contains '/renders/'" | sort: "path" %}

<div style="max-width: 1200px; margin: 0 auto;">
{% for file in render_files %}
  {% if file.extname == ".png" %}
    {% assign parts = file.name | split: "." %}
    {% assign boat = parts[0] %}
    {% assign config = parts[1] %}
    {% assign view = parts[3] %}
    
    <div style="margin-bottom: 40px; border-bottom: 1px solid #ddd; padding-bottom: 20px;">
      <h3>{{ boat | upcase }} - {{ config | capitalize }} - {{ view }}</h3>
      <p style="color: #666; font-size: 0.9em;">
        {{ file.path }} • {{ file.modified_time | date: "%Y-%m-%d %H:%M" }}
      </p>
      <img src="{{ file.path }}" alt="{{ boat }} {{ config }} {{ view }}" style="max-width: 100%; height: auto; border: 1px solid #ddd;">
    </div>
  {% endif %}
{% endfor %}
</div>

---

[← Back to Home](/)

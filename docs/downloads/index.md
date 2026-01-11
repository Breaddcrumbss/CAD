---
layout: default
title: Downloads
---

# Design Downloads

FreeCAD design files (`.FCStd`) for all boat configurations.

These files can be opened in [FreeCAD](https://www.freecadweb.org/) for inspection, modification, or 3D printing preparation.

{% assign fcstd_files = site.static_files | where_exp: "file", "file.path contains '/downloads/'" | where_exp: "file", "file.extname == '.FCStd'" | sort: "path" %}

<table style="width: 100%; border-collapse: collapse;">
  <thead>
    <tr style="background: #f0f0f0;">
      <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Boat</th>
      <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Configuration</th>
      <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">File</th>
      <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Last Modified</th>
      <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Download</th>
    </tr>
  </thead>
  <tbody>
{% for file in fcstd_files %}
  {% assign parts = file.name | split: "." %}
  {% assign boat = parts[0] %}
  {% assign config = parts[1] %}
  <tr>
    <td style="padding: 10px; border: 1px solid #ddd;"><strong>{{ boat | upcase }}</strong></td>
    <td style="padding: 10px; border: 1px solid #ddd;">{{ config | capitalize }}</td>
    <td style="padding: 10px; border: 1px solid #ddd; font-family: monospace; font-size: 0.9em;">{{ file.name }}</td>
    <td style="padding: 10px; border: 1px solid #ddd;">{{ file.modified_time | date: "%Y-%m-%d %H:%M" }}</td>
    <td style="padding: 10px; border: 1px solid #ddd;">
      <a href="{{ file.path }}" download style="background: #007bff; color: white; padding: 5px 15px; border-radius: 3px; text-decoration: none;">⬇ Download</a>
    </td>
  </tr>
{% endfor %}
  </tbody>
</table>

## How to Use

1. **Install FreeCAD**: Download from [freecadweb.org](https://www.freecadweb.org/)
2. **Download a file**: Click the download button above
3. **Open in FreeCAD**: File → Open → Select the downloaded `.FCStd` file
4. **Explore**: All components should be visible and editable

## File Naming Convention

Files are named: `{boat}.{configuration}.color.FCStd`

- **boat**: `rp1`, `rp2`, `rp3` (Roti Proa models 1, 2, 3)
- **configuration**: Sailing configuration (closehaul, beamreach, etc.)

---

[← Back to Home](/)

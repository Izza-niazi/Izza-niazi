<div align="center">

<h3><code>izza@github ~ $ ./contributions.sh</code></h3>
<img src="./contrib-heatmap.svg" width="860" alt="Contribution heatmap" />

<br><br>

<h3><code>izza@github ~ $ whoami</code></h3>
<table>
  <tr>
    <td valign="top"><img src="./avi-ascii.svg" width="370" alt="ASCII portrait" /></td>
    <td valign="top"><img src="./info-card.svg" width="490" alt="neofetch info card" /></td>
  </tr>
</table>

</div>

<!--
  Layout notes (GitHub markdown gotchas):
  - Inline style="..." is stripped. The only vertical spacing GitHub honors is <br>.
  - <h1>/<h2> draw a full-width underline rule; use <h3> for a title with no line.
  - No JavaScript and no external CSS — every animation lives inside its SVG.
  - Heatmap width (860) == portrait (370) + card (490) so the edges line up.
  - Regenerate portrait/card locally when they change:
      python scripts/prep_photo.py source-photo.jpg
      python scripts/make_ascii_svg.py
      python scripts/make_info_card.py
    The heatmap refreshes itself daily via .github/workflows/update-profile-art.yml
-->

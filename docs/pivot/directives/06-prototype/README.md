# Directive 06 prototype

Chapters 2 and 3 of the explorer, generated from the verified funding panel. Directive 06 moves these files to
`scripts/emit_visual.py` and `site/template.html` and deletes this folder.

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
python3 docs/pivot/directives/06-prototype/emit_visual.py /tmp/funding_panel.csv . docs/pivot/directives/06-prototype/template.html /tmp/explorer.html
```

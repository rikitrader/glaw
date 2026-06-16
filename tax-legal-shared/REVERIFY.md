# Reverify Procedure

Refresh `current-figures.md` before the max-age window expires or whenever a
workflow depends on a figure that may have changed.

1. Pull the current primary source.
2. Add or update the `FIG-YYYY-####` entry with the exact value, tax period,
   `as_of`, `source_url`, and reviewer.
3. Re-run the affected workflow and `bin/glaw-doctor`.
4. Keep stale or superseded figures in the matter workpaper only if they are
   needed for historical audit trail; do not reuse them as current figures.

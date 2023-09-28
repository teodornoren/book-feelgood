# book-feelgood
Book activity using a self-hosted github runner with secrets for feelgood.wondr.se login.

## yaml layout
```yaml
---
day_offset: <day_offset>
facility: <facility_uuid>
activities:
  - name: <activity_1>
    time: "<time>"
    day: <week_day>
  - name: <activity_2>
    time: "<time>"
    day: <week_day>
```
See the [activities](activities) directory for examples.

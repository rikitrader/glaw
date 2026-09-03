UPDATE discovery_objects
SET source_id = json_extract(payload_json, '$.sourceId')
WHERE source_id IS NULL
  AND json_extract(payload_json, '$.sourceId') IS NOT NULL;

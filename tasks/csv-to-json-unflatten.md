# CSV to JSON Unflatten Feature

## Problem

When converting nested JSON → CSV → JSON, the original structure is lost:

### Original JSON
```json
{
  "id": "0001",
  "batters": {
    "batter": [
      { "id": "1001", "type": "Regular" }
    ]
  },
  "topping": [
    { "id": "5001", "type": "None" }
  ]
}
```

### After JSON → CSV → JSON (current behavior)
```json
{
  "id": 1,
  "batters.batter": "[{\"id\": \"1001\", \"type\": \"Regular\"}]",
  "topping": "[{\"id\": \"5001\", \"type\": \"None\"}]"
}
```

## Issues to Fix

1. **Dot notation not unflattened**: `batters.batter` stays flat instead of becoming `{"batters": {"batter": [...]}}`
2. **JSON strings not parsed**: Array/object values stored as strings aren't parsed back to JSON
3. **Type coercion**: `"0001"` becomes `1` instead of staying as string

## Proposed Solution

Add an `unflatten` export mode or parameter to CSV→JSON conversion that:

1. **Parses embedded JSON strings** - Detect and parse `[{...}]` or `{...}` strings back to arrays/objects
2. **Expands dot notation** - Convert `batters.batter` key to nested `{"batters": {"batter": value}}`
3. **Preserves string types** - Keep values like `"0001"` as strings when they appear quoted in original

## Implementation Notes

- File to modify: `backend/converters/csv_to_json.py`
- May need new utility function for unflattening nested keys
- Related to Phase 1 "JSON flatten/unflatten transformations" in ROADMAP.md
- Test file available: `tests/sample_files/nested3.json`

## Test Case

Input CSV:
```csv
id,type,name,ppu,batters.batter,topping
0001,donut,Cake,0.55,"[{""id"": ""1001"", ""type"": ""Regular""}]","[{""id"": ""5001"", ""type"": ""None""}]"
```

Expected output with unflatten:
```json
[
  {
    "id": "0001",
    "type": "donut",
    "name": "Cake",
    "ppu": 0.55,
    "batters": {
      "batter": [
        { "id": "1001", "type": "Regular" }
      ]
    },
    "topping": [
      { "id": "5001", "type": "None" }
    ]
  }
]
```
"""Data validation utilities for mockapi JSON files.

Checks for common data quality issues:
- Duplicate IDs within collections
- Missing ID fields
- Inconsistent field types across records
- Empty collections

Usage:
    >>> from mockapi.validate import validate_db
    >>> issues = validate_db({"users": [{"id": 1}, {"id": 1}]})
    >>> print(issues)  # ["'users' has duplicate IDs: [1]"]
"""


def validate_db(data):
    """Validate a mockapi database dict and return a list of issue strings.

    Args:
        data: dict loaded from JSON file, where keys are collection names
              and values are lists of record dicts.

    Returns:
        List of human-readable issue descriptions. Empty list means valid.
    """
    issues = []

    if not isinstance(data, dict):
        issues.append("Root element must be a JSON object")
        return issues

    if not data:
        issues.append("Database is empty (no collections)")
        return issues

    for name, records in data.items():
        if not isinstance(records, list):
            issues.append(f"'{name}' is not an array (expected a list of records)")
            continue

        if len(records) == 0:
            issues.append(f"'{name}' is empty")
            continue

        # Check that records are dicts
        non_dict = sum(1 for r in records if not isinstance(r, dict))
        if non_dict > 0:
            issues.append(f"'{name}' has {non_dict} non-object entries")
            continue

        # Check for id field
        missing_id = sum(1 for r in records if 'id' not in r)
        if missing_id > 0:
            issues.append(
                f"'{name}' has {missing_id}/{len(records)} records without 'id' field"
            )

        # Check for duplicate IDs
        ids = [r['id'] for r in records if 'id' in r]
        seen = set()
        dupes = set()
        for rid in ids:
            if rid in seen:
                dupes.add(rid)
            seen.add(rid)
        if dupes:
            issues.append(f"'{name}' has duplicate IDs: {sorted(dupes, key=str)}")

        # Check field type consistency (allow NoneType mixed with any single type)
        field_types = {}
        for r in records:
            for k, v in r.items():
                t = type(v).__name__
                if k not in field_types:
                    field_types[k] = set()
                field_types[k].add(t)
        for field, types in field_types.items():
            real_types = types - {'NoneType'}
            if len(real_types) > 1:
                issues.append(
                    f"'{name}.{field}' has mixed types: {sorted(real_types)}"
                )

    return issues

"""Append-only inventory history: serving/extraction reads active revisions only."""
def active_records(rows):
    by_id = {r['source_id']: r for r in rows}
    if len(by_id) != len(rows):
        raise ValueError('Duplicate source_id')
    superseded = set()
    seen = set()
    for row in rows:
        old = row.get('supersedes')
        if old:
            if old not in seen or by_id[old]['relative_path'] != row['relative_path'] or old in superseded:
                raise ValueError('Invalid supersedes chain: ' + row['source_id'])
            superseded.add(old)
        seen.add(row['source_id'])
    result = [r for r in rows if r['source_id'] not in superseded]
    paths = [r['relative_path'].replace('\\', '/').casefold() for r in result]
    if len(paths) != len(set(paths)):
        raise ValueError('Multiple active records for one path')
    return result

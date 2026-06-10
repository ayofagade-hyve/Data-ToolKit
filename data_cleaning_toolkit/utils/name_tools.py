"""Name splitting and standardisation utilities."""

def split_full_name(name: str) -> tuple:
    """Split a full name into (first_name, last_name)."""
    name = str(name).strip()
    if not name:
        return ("", "")
    parts = name.split()
    if len(parts) == 1:
        return (parts[0].title(), "")
    elif len(parts) == 2:
        return (parts[0].title(), parts[1].title())
    else:
        return (parts[0].title(), " ".join(p.title() for p in parts[1:]))

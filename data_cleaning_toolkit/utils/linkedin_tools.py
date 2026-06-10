"""LinkedIn URL generation utilities."""
import urllib.parse

def generate_linkedin_search_url(first_name: str = "", last_name: str = "", company: str = "") -> str:
    parts = []
    if first_name: parts.append(str(first_name).strip())
    if last_name: parts.append(str(last_name).strip())
    if company: parts.append(str(company).strip())
    query = " ".join(parts)
    if not query.strip():
        return ""
    encoded = urllib.parse.quote_plus(query)
    return f"https://www.linkedin.com/search/results/people/?keywords={encoded}"

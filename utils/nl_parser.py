"""Natural Language Command Parser for the Formula Bar.

Tier 1: Regex-based pattern matching (free, instant, offline)
Tier 2: Gemini AI fallback (optional, needs API key)
"""
import re
import json
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class ParsedCommand:
    """Structured representation of a parsed natural language command."""
    action: str = ""           # e.g. remove_rows, keep_rows, replace_values, etc.
    column: str = ""           # target column name
    value: str = ""            # primary value (search term, new value, etc.)
    value2: str = ""           # secondary value (replacement, delimiter, etc.)
    condition: str = ""        # contains, equals, is_empty, not_empty, starts_with, ends_with
    case_mode: str = ""        # upper, lower, title, sentence
    sort_order: str = "asc"    # asc or desc
    confidence: float = 0.0    # 0.0 - 1.0 confidence score
    source: str = ""           # "regex" or "ai"
    raw_input: str = ""        # original user input
    error: str = ""            # error message if parsing failed
    extra: dict = field(default_factory=dict)  # additional parameters


# ──────────────────────────────────────────────────────────────
# Column matching helpers
# ──────────────────────────────────────────────────────────────

def _match_column(user_col: str, df_columns: list) -> Optional[str]:
    """Fuzzy-match a user-typed column name to actual DataFrame columns.
    
    Tries: exact → case-insensitive → stripped/normalised → partial match.
    """
    user_col = user_col.strip()
    if not user_col:
        return None
    
    # 1. Exact match
    if user_col in df_columns:
        return user_col
    
    # 2. Case-insensitive
    lower_map = {c.lower(): c for c in df_columns}
    if user_col.lower() in lower_map:
        return lower_map[user_col.lower()]
    
    # 3. Normalised (strip spaces, underscores, hyphens)
    def norm(s):
        return re.sub(r'[\s_\-]+', '', s.lower())
    
    norm_map = {norm(c): c for c in df_columns}
    if norm(user_col) in norm_map:
        return norm_map[norm(user_col)]
    
    # 4. Partial match (user_col is substring of a column name, or vice versa)
    user_lower = user_col.lower()
    for col in df_columns:
        if user_lower in col.lower() or col.lower() in user_lower:
            return col
    
    # 5. No match found
    return None


def _extract_quoted(text: str) -> tuple:
    """Extract a quoted string and return (extracted, remaining_text).
    Handles both single and double quotes.
    """
    match = re.search(r'["\'](.+?)["\']', text)
    if match:
        return match.group(1), text[:match.start()] + text[match.end():]
    return None, text


# ──────────────────────────────────────────────────────────────
# TIER 1: Regex parser
# ──────────────────────────────────────────────────────────────

def _parse_regex(user_input: str, df_columns: list) -> Optional[ParsedCommand]:
    """Parse a natural language command using regex patterns.
    
    Returns a ParsedCommand if successful, None if no pattern matched.
    """
    text = user_input.strip()
    text_lower = text.lower()
    cmd = ParsedCommand(raw_input=user_input, source="regex")
    
    # ── REMOVE / DELETE ROWS ──
    # "remove rows where email contains test"
    # "delete rows where country equals UK"
    # "remove rows where phone is empty"
    m = re.match(
        r'(?:remove|delete)\s+(?:all\s+)?rows?\s+(?:where|with|if|when)\s+'
        r'(.+?)\s+(contains?|equals?|is\s+empty|is\s+not\s+empty|is\s+blank|'
        r'is\s+not\s+blank|starts?\s+with|ends?\s+with)\s*(.*)',
        text_lower
    )
    if m:
        col_raw, condition_raw, val_raw = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        # Clean up condition
        cond = condition_raw.replace(" ", "_")
        if cond in ("contain", "contains"): cond = "contains"
        elif cond in ("equal", "equals"): cond = "equals"
        elif cond in ("is_empty", "is_blank"): cond = "is_empty"
        elif cond in ("is_not_empty", "is_not_blank"): cond = "not_empty"
        elif cond in ("start_with", "starts_with"): cond = "starts_with"
        elif cond in ("end_with", "ends_with"): cond = "ends_with"
        
        # Try quoted value first
        quoted, _ = _extract_quoted(val_raw)
        val = quoted if quoted else val_raw.strip().strip("'\"")
        
        col = _match_column(col_raw, df_columns)
        if col:
            cmd.action = "remove_rows"
            cmd.column = col
            cmd.condition = cond
            cmd.value = val
            cmd.confidence = 0.95
            return cmd
    
    # ── KEEP / FILTER ROWS ──
    m = re.match(
        r'(?:keep|filter|show)\s+(?:only\s+)?rows?\s+(?:where|with|if|when)\s+'
        r'(.+?)\s+(contains?|equals?|is\s+empty|is\s+not\s+empty|is\s+blank|'
        r'is\s+not\s+blank|starts?\s+with|ends?\s+with)\s*(.*)',
        text_lower
    )
    if m:
        col_raw, condition_raw, val_raw = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        cond = condition_raw.replace(" ", "_")
        if cond in ("contain", "contains"): cond = "contains"
        elif cond in ("equal", "equals"): cond = "equals"
        elif cond in ("is_empty", "is_blank"): cond = "is_empty"
        elif cond in ("is_not_empty", "is_not_blank"): cond = "not_empty"
        elif cond in ("start_with", "starts_with"): cond = "starts_with"
        elif cond in ("end_with", "ends_with"): cond = "ends_with"
        quoted, _ = _extract_quoted(val_raw)
        val = quoted if quoted else val_raw.strip().strip("'\"")
        col = _match_column(col_raw, df_columns)
        if col:
            cmd.action = "keep_rows"
            cmd.column = col
            cmd.condition = cond
            cmd.value = val
            cmd.confidence = 0.95
            return cmd
    
    # ── REPLACE VALUES ──
    # "replace UK with United Kingdom in country"
    # "replace "test" with "live" in status"
    m = re.match(
        r'(?:replace|change|swap)\s+["\']?(.+?)["\']?\s+with\s+["\']?(.+?)["\']?\s+'
        r'(?:in|on|for)\s+(?:column\s+)?(.+)',
        text_lower
    )
    if m:
        find_val, replace_val, col_raw = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        col = _match_column(col_raw, df_columns)
        if col:
            cmd.action = "replace_values"
            cmd.column = col
            cmd.value = find_val
            cmd.value2 = replace_val
            cmd.confidence = 0.90
            return cmd
    
    # ── DELETE COLUMN ──
    m = re.match(
        r'(?:delete|remove|drop)\s+(?:the\s+)?column\s+(.+)',
        text_lower
    )
    if m:
        col_raw = m.group(1).strip().strip("'\"")
        col = _match_column(col_raw, df_columns)
        if col:
            cmd.action = "delete_column"
            cmd.column = col
            cmd.confidence = 0.95
            return cmd
    
    # ── FILL BLANKS ──
    # "fill blanks in country with Unknown"
    m = re.match(
        r'(?:fill|populate)\s+(?:blanks?|empty|empties|missing)\s+(?:in|on|for)\s+'
        r'(?:column\s+)?(.+?)\s+with\s+(.+)',
        text_lower
    )
    if m:
        col_raw, val = m.group(1).strip(), m.group(2).strip().strip("'\"")
        col = _match_column(col_raw, df_columns)
        if col:
            cmd.action = "fill_blanks"
            cmd.column = col
            cmd.value = val
            cmd.confidence = 0.95
            return cmd
    
    # ── CHANGE CASE ──
    # "uppercase email"  /  "lowercase country"  /  "titlecase name"
    m = re.match(
        r'(uppercase|upper case|upper|lowercase|lower case|lower|titlecase|'
        r'title case|title|sentencecase|sentence case|capitalise|capitalize)\s+'
        r'(?:the\s+)?(?:column\s+)?(.+)',
        text_lower
    )
    if m:
        case_raw, col_raw = m.group(1).strip(), m.group(2).strip().strip("'\"")
        col = _match_column(col_raw, df_columns)
        if col:
            if "upper" in case_raw:
                mode = "upper"
            elif "lower" in case_raw:
                mode = "lower"
            elif "title" in case_raw or "capital" in case_raw:
                mode = "title"
            elif "sentence" in case_raw:
                mode = "sentence"
            else:
                mode = "title"
            cmd.action = "change_case"
            cmd.column = col
            cmd.case_mode = mode
            cmd.confidence = 0.95
            return cmd
    
    # ── TRIM ──
    m = re.match(
        r'(?:trim|strip|clean)\s+(?:whitespace\s+(?:in|from)\s+)?(?:column\s+)?(.+)',
        text_lower
    )
    if m:
        col_raw = m.group(1).strip().strip("'\"")
        col = _match_column(col_raw, df_columns)
        if col:
            cmd.action = "trim"
            cmd.column = col
            cmd.confidence = 0.90
            return cmd
    
    # ── SORT ──
    m = re.match(
        r'sort\s+(?:by\s+)?(?:column\s+)?(.+?)\s*(asc|ascending|desc|descending|a-z|z-a)?$',
        text_lower
    )
    if m:
        col_raw = m.group(1).strip().strip("'\"")
        order_raw = (m.group(2) or "asc").strip()
        col = _match_column(col_raw, df_columns)
        if col:
            cmd.action = "sort"
            cmd.column = col
            cmd.sort_order = "desc" if order_raw in ("desc", "descending", "z-a") else "asc"
            cmd.confidence = 0.95
            return cmd
    
    # ── REMOVE DUPLICATES ──
    m = re.match(
        r'(?:remove|delete|drop)\s+(?:duplicate|duplicates|dupes|dups)\s+'
        r'(?:in|on|from|by)\s+(?:column\s+)?(.+)',
        text_lower
    )
    if m:
        col_raw = m.group(1).strip().strip("'\"")
        col = _match_column(col_raw, df_columns)
        if col:
            cmd.action = "remove_dupes"
            cmd.column = col
            cmd.confidence = 0.90
            return cmd
    
    # Also: "dedupe column email"
    m = re.match(r'dedup(?:e|licate)?\s+(?:column\s+)?(.+)', text_lower)
    if m:
        col_raw = m.group(1).strip().strip("'\"")
        col = _match_column(col_raw, df_columns)
        if col:
            cmd.action = "remove_dupes"
            cmd.column = col
            cmd.confidence = 0.85
            return cmd
    
    # ── ADD COLUMN ──
    m = re.match(
        r'(?:add|create|new)\s+(?:a\s+)?column\s+["\']?(.+?)["\']?\s+'
        r'(?:with\s+(?:value|default)?\s*)?(.+)',
        text_lower
    )
    if m:
        col_name, val = m.group(1).strip(), m.group(2).strip().strip("'\"")
        cmd.action = "add_column"
        cmd.column = col_name
        cmd.value = val
        cmd.confidence = 0.90
        return cmd
    
    # ── RENAME COLUMN ──
    m = re.match(
        r'rename\s+(?:column\s+)?["\']?(.+?)["\']?\s+to\s+["\']?(.+?)["\']?$',
        text_lower
    )
    if m:
        old_col_raw, new_name = m.group(1).strip(), m.group(2).strip()
        col = _match_column(old_col_raw, df_columns)
        if col:
            cmd.action = "rename_column"
            cmd.column = col
            cmd.value = new_name
            cmd.confidence = 0.95
            return cmd
    
    # ── EXTRACT DOMAIN ──
    m = re.match(
        r'extract\s+domain[s]?\s+(?:from\s+)?(?:column\s+)?(.+)',
        text_lower
    )
    if m:
        col_raw = m.group(1).strip().strip("'\"")
        col = _match_column(col_raw, df_columns)
        if col:
            cmd.action = "extract_domain"
            cmd.column = col
            cmd.confidence = 0.90
            return cmd
    
    # ── SPLIT COLUMN ──
    # "split name by space into first name and last name"
    m = re.match(
        r'split\s+(?:column\s+)?(.+?)\s+by\s+["\']?(.+?)["\']?\s+'
        r'into\s+["\']?(.+?)["\']?\s+and\s+["\']?(.+?)["\']?$',
        text_lower
    )
    if m:
        col_raw = m.group(1).strip()
        delimiter = m.group(2).strip()
        name1, name2 = m.group(3).strip(), m.group(4).strip()
        col = _match_column(col_raw, df_columns)
        if col:
            cmd.action = "split_column"
            cmd.column = col
            cmd.value = delimiter if delimiter != "space" else " "
            cmd.extra = {"new_columns": [name1, name2]}
            cmd.confidence = 0.85
            return cmd
    
    # ── MERGE COLUMNS ──
    # "merge first name and last name into full name"
    m = re.match(
        r'(?:merge|combine|join|concat)\s+(?:column[s]?\s+)?["\']?(.+?)["\']?\s+'
        r'and\s+["\']?(.+?)["\']?\s+into\s+["\']?(.+?)["\']?$',
        text_lower
    )
    if m:
        col1_raw, col2_raw = m.group(1).strip(), m.group(2).strip()
        new_name = m.group(3).strip()
        col1 = _match_column(col1_raw, df_columns)
        col2 = _match_column(col2_raw, df_columns)
        if col1 and col2:
            cmd.action = "merge_columns"
            cmd.column = col1
            cmd.value = col2
            cmd.value2 = new_name
            cmd.confidence = 0.85
            return cmd
    
    # ── COUNT ROWS ──
    m = re.match(
        r'(?:count|how many)\s+rows?\s+(?:where|with|if|when)\s+'
        r'(.+?)\s+(contains?|equals?|is\s+empty|is\s+not\s+empty)\s*(.*)',
        text_lower
    )
    if m:
        col_raw, cond_raw, val_raw = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        cond = cond_raw.replace(" ", "_")
        if cond in ("contain", "contains"): cond = "contains"
        elif cond in ("equal", "equals"): cond = "equals"
        elif cond in ("is_empty", "is_blank"): cond = "is_empty"
        elif cond in ("is_not_empty",): cond = "not_empty"
        quoted, _ = _extract_quoted(val_raw)
        val = quoted if quoted else val_raw.strip().strip("'\"")
        col = _match_column(col_raw, df_columns)
        if col:
            cmd.action = "count"
            cmd.column = col
            cmd.condition = cond
            cmd.value = val
            cmd.confidence = 0.90
            return cmd
    
    # No pattern matched
    return None


# ──────────────────────────────────────────────────────────────
# TIER 2: Gemini AI fallback
# ──────────────────────────────────────────────────────────────

GEMINI_PROMPT_TEMPLATE = """You are a data operations assistant. The user wants to manipulate a CSV file.

The CSV has these columns: {columns}

User request: "{user_input}"

Parse this into a structured JSON command. Respond with ONLY valid JSON, no markdown.

Available actions:
- remove_rows: Remove rows matching a condition
- keep_rows: Keep only rows matching a condition
- replace_values: Find and replace in a column
- delete_column: Delete a column
- fill_blanks: Fill empty cells in a column with a value
- change_case: Change text case (upper/lower/title/sentence)
- trim: Strip whitespace from a column
- sort: Sort by a column
- remove_dupes: Remove duplicates in a column
- add_column: Add a new column with a value
- rename_column: Rename a column
- extract_domain: Extract email domain into new column
- split_column: Split a column by delimiter
- merge_columns: Merge two columns
- count: Count rows matching condition

Available conditions (for remove_rows/keep_rows/count):
- contains, equals, is_empty, not_empty, starts_with, ends_with

Respond with this JSON structure:
{{
    "action": "action_name",
    "column": "exact column name from the list above",
    "value": "primary value",
    "value2": "secondary value (for replace, merge, split)",
    "condition": "condition type",
    "case_mode": "upper/lower/title/sentence (for change_case only)",
    "sort_order": "asc/desc (for sort only)",
    "extra": {{}}
}}

Use the EXACT column names from the list. If a column can't be identified, use your best guess from the available columns."""


def parse_with_ai(user_input, columns, api_key, model="llama-3.3-70b-versatile", provider="groq"):
    """Parse a command using AI (Groq or Gemini)."""
    try:
        if provider == "groq":
            from openai import OpenAI
            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key,
            )
            prompt = GEMINI_PROMPT.format(columns=", ".join(columns), user_input=user_input)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            text = response.choices[0].message.content.strip()
        else:
            # Gemini fallback
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            prompt = GEMINI_PROMPT.format(columns=", ".join(columns), user_input=user_input)
            gen_model = genai.GenerativeModel(model)
            response = gen_model.generate_content(prompt)
            text = response.text.strip()

        if text.startswith("```"):
            text = re.sub(r'^```(?:json)?\n?', '', text)
            text = re.sub(r'\n?```$', '', text)
        data = json.loads(text)
        cmd = ParsedCommand(
            action=data.get("action", ""), column=data.get("column", ""),
            value=data.get("value", ""), value2=data.get("value2", ""),
            condition=data.get("condition", ""), case_mode=data.get("case_mode", ""),
            sort_order=data.get("sort_order", "asc"), confidence=0.80,
            source="ai", raw_input=user_input, extra=data.get("extra", {}),
        )
        return cmd if cmd.action else None
    except Exception as e:
        return ParsedCommand(raw_input=user_input, source="ai", error=f"AI error: {e}")

# ──────────────────────────────────────────────────────────────
# Main parse function
# ──────────────────────────────────────────────────────────────

# Example commands for the help text
EXAMPLE_COMMANDS = [
    ("Remove rows", 'remove rows where email contains "test"'),
    ("Keep rows", 'keep rows where country equals "United Kingdom"'),
    ("Find & replace", 'replace "UK" with "United Kingdom" in country'),
    ("Delete column", "delete column phone_2"),
    ("Fill blanks", 'fill blanks in country with "Unknown"'),
    ("Change case", "uppercase email"),
    ("Trim whitespace", "trim company"),
    ("Sort", "sort by last name a-z"),
    ("Remove duplicates", "remove duplicates in email"),
    ("Add column", 'add column source with "Web Signup"'),
    ("Rename", "rename company to organisation"),
    ("Extract domain", "extract domain from email"),
    ("Split column", 'split full name by space into first name and last name'),
    ("Merge columns", "merge first name and last name into full name"),
    ("Count", 'count rows where country contains "UK"'),
]


def parse_command(user_input: str, df_columns: list,
                   api_key: str = None) -> ParsedCommand:
    """Parse a natural language command into a structured command.
    
    Tier 1: Tries regex patterns first (free, instant)
    Tier 2: Falls back to Gemini AI if regex fails and API key provided
    
    Args:
        user_input: Natural language command from the user
        df_columns: List of column names in the DataFrame
        api_key: Optional Gemini API key for AI fallback
    
    Returns:
        ParsedCommand with the parsed action and parameters
    """
    if not user_input or not user_input.strip():
        return ParsedCommand(raw_input=user_input, error="Please enter a command.")
    
    # Tier 1: Regex parser
    result = _parse_regex(user_input, df_columns)
    if result and result.action:
        return result
    
    # Tier 2: Gemini AI fallback
    if api_key:
        result = parse_with_gemini(user_input, df_columns, api_key)
        if result and result.action and not result.error:
            return result
        elif result and result.error:
            return result
    
    # Nothing worked
    return ParsedCommand(
        raw_input=user_input,
        error=(
            "Couldn't understand that command. "
            + ("" if api_key else "💡 Add a Gemini API key in the sidebar for AI-powered parsing, or ")
            + "try one of the example commands below."
        )
    )

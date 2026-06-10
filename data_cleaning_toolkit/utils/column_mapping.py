"""Column auto-detection via alias matching."""
import pandas as pd
from typing import Optional

COLUMN_ALIASES = {
    "email": ["email", "e-mail", "work email", "email address", "e-mail address",
              "email_address", "emailaddress", "contact email"],
    "first_name": ["first name", "firstname", "first_name", "fname", "given name",
                    "givenname", "prenom"],
    "last_name": ["last name", "lastname", "last_name", "lname", "surname",
                   "family name", "familyname", "nom"],
    "full_name": ["full name", "fullname", "full_name", "name", "contact name",
                   "display name"],
    "company": ["company", "organization", "organisation", "account", "company name",
                 "account name", "employer", "business name"],
    "job_title": ["job title", "title", "jobtitle", "job_title", "position",
                   "role", "designation"],
    "phone": ["phone", "telephone", "phone number", "tel", "mobile", "cell",
               "work phone", "direct phone", "phone_number"],
    "website": ["website", "web", "url", "company website", "domain",
                 "company url", "homepage", "site"],
    "linkedin": ["linkedin", "linkedin url", "linkedin profile", "linkedin_url",
                  "linkedinurl", "li url"],
    "city": ["city", "town", "locality"],
    "state": ["state", "province", "region", "state/province", "county"],
    "country": ["country", "nation", "country/region", "country name"],
    "industry": ["industry", "sector", "vertical", "industry type"],
    "department": ["department", "dept", "division", "team", "business unit"],
    "seniority": ["seniority", "seniority level", "management level", "level", "job level"],
}


def find_column(df: pd.DataFrame, field: str) -> Optional[str]:
    """Find a column in the DataFrame matching the given field alias."""
    aliases = COLUMN_ALIASES.get(field, [])
    df_cols_lower = {c.lower().strip(): c for c in df.columns}
    for alias in aliases:
        if alias.lower() in df_cols_lower:
            return df_cols_lower[alias.lower()]
    return None


def get_series(df: pd.DataFrame, field: str) -> pd.Series:
    """Get a Series for the given field, falling back to empty strings."""
    col = find_column(df, field)
    if col is not None:
        return df[col].fillna("").astype(str).str.strip()
    return pd.Series([""] * len(df), index=df.index)

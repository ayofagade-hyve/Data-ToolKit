"""
Basic tests for the classifier utilities.
Run with: python -m pytest tests/
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.classifiers import classify_seniority, classify_job_function, classify_org_type
from utils.matching import levenshtein, similarity_pct
from utils.name_tools import split_name, extract_company_from_title
from utils.domain_tools import extract_domain_from_email, is_personal_domain


# ── Seniority ──────────────────────────────────────────────────

def test_seniority_ceo():
    assert classify_seniority("Chief Executive Officer") == "C-level or equivalent"

def test_seniority_founder():
    assert classify_seniority("Co-Founder & CEO") == "C-level or equivalent"

def test_seniority_president():
    """Plain 'President' (no 'vice') should be C-level."""
    assert classify_seniority("President") == "C-level or equivalent"

def test_seniority_managing_director():
    assert classify_seniority("Managing Director, EMEA") == "C-level or equivalent"

def test_seniority_vp():
    """'Vice President' must be caught by VP check before 'president' in C-level."""
    assert classify_seniority("Senior Vice President, Sales") == "VP level (EVP, SVP, AVP)"

def test_seniority_vp_short():
    assert classify_seniority("VP of Engineering") == "VP level (EVP, SVP, AVP)"

def test_seniority_director():
    assert classify_seniority("Director of Engineering") == "Director level"

def test_seniority_director_regional():
    assert classify_seniority("Regional Director") == "Director level"

def test_seniority_manager():
    assert classify_seniority("Head of Marketing") == "Manager level"

def test_seniority_associate():
    assert classify_seniority("Business Analyst") == "Associate level"

def test_seniority_intern():
    assert classify_seniority("Summer Intern") == "Associate level"

def test_seniority_other():
    assert classify_seniority("Freelancer") == "Other"


# ── Job Function ───────────────────────────────────────────────

def test_function_sales():
    assert classify_job_function("Account Executive") == "Sales"

def test_function_marketing():
    assert classify_job_function("Brand Manager") == "Marketing"

def test_function_it():
    assert classify_job_function("Software Engineer") == "IT"

def test_function_legal():
    assert classify_job_function("Compliance Officer") == "Legal"

def test_function_hr():
    assert classify_job_function("Talent Acquisition Manager") == "Human Resources"

def test_function_finance():
    assert classify_job_function("Treasury Analyst") == "Finance"


# ── Org Type ───────────────────────────────────────────────────

def test_org_insurance():
    assert classify_org_type(company="AXA Insurance") == "Insurance company"

def test_org_fintech():
    assert classify_org_type(company="Stripe", industries="fintech") == "Established fintech or solution provider"

def test_org_bank():
    assert classify_org_type(company="HSBC Banking") == "Commercial or corporate bank"

def test_org_university():
    assert classify_org_type(company="MIT", industries="education") == "Higher education"


# ── Matching ───────────────────────────────────────────────────

def test_levenshtein_identical():
    assert levenshtein("hello", "hello") == 0

def test_levenshtein_one_edit():
    assert levenshtein("hello", "hallo") == 1

def test_similarity_100():
    assert similarity_pct("Acme Corp", "Acme Corp") == 100

def test_similarity_different():
    pct = similarity_pct("Acme Corp", "Acme Corporation")
    assert 50 < pct < 100


# ── Name Tools ─────────────────────────────────────────────────

def test_split_name():
    assert split_name("John Smith") == ("John", "Smith")

def test_split_name_single():
    assert split_name("Madonna") == ("Madonna", "")

def test_split_name_three_parts():
    first, last = split_name("Mary Jane Watson")
    assert first == "Mary"
    assert last == "Jane Watson"

def test_extract_company():
    assert extract_company_from_title("John Doe at Acme Corp") == "Acme Corp"

def test_extract_company_no_at():
    assert extract_company_from_title("John Doe") == ""


# ── Domain Tools ───────────────────────────────────────────────

def test_extract_domain():
    assert extract_domain_from_email("john@acme.com") == "acme.com"

def test_personal_domain():
    assert is_personal_domain("gmail.com") is True
    assert extract_domain_from_email("john@gmail.com") is None

def test_extract_domain_none():
    assert extract_domain_from_email("not-an-email") is None


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

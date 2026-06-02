"""
Job Seniority, Function & Organisation-Type Classifiers
========================================================
Ported from the most comprehensive version in ``consolidate.gs``,
which includes French, Portuguese, and Spanish job title keywords.

IMPORTANT: ``_has_any`` uses regex word-boundary matching so that
short acronyms like "cto" don't accidentally match inside longer
words like "director".
"""

from __future__ import annotations
import re
import unicodedata
from functools import lru_cache


def _normalize(value: str) -> str:
    """Lower-case, strip accents, remove punctuation, collapse spaces."""
    text = str(value or "").lower()
    text = unicodedata.normalize("NFD", text)
    text = re.sub(r"[\u0300-\u036f]", "", text)       # strip accents
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@lru_cache(maxsize=4096)
def _compile_pattern(phrase: str) -> re.Pattern:
    """Compile a word-boundary regex for *phrase*."""
    escaped = re.escape(phrase)
    return re.compile(r"\b" + escaped + r"\b")


def _has_any(text: str, phrases: tuple) -> bool:
    """Return True if *text* contains any of the *phrases* as whole words.

    Uses ``\\b`` (word-boundary) matching so that e.g. ``'cto'`` does NOT
    match inside ``'director'``.
    """
    for phrase in phrases:
        if _compile_pattern(phrase).search(text):
            return True
    return False


# ── SENIORITY ──────────────────────────────────────────────────

def classify_seniority(job_title: str, original_seniority: str = "") -> str:
    """Classify a job title into a seniority level.

    Returns one of:
      - C-level or equivalent
      - VP level (EVP, SVP, AVP)
      - Director level
      - Manager level
      - Associate level
      - Other

    NOTE: VP is checked **before** C-level so that "Vice President"
    titles don't accidentally match the "president" C-level keyword.
    """
    t = _normalize(job_title)
    s = _normalize(original_seniority)

    # ── VP level (must be checked FIRST because "vice president"
    #    contains the substring "president") ────────────────────
    if s == "senior leadership" or _has_any(t, (
        "evp", "executive vice president",
        "svp", "senior vice president",
        "avp", "assistant vice president", "associate vice president",
        "vp", "vice president",
        "vpe", "vice president engineering",
    )):
        return "VP level (EVP, SVP, AVP)"

    # ── C-level or equivalent ─────────────────────────────────
    if s in ("executive level", "cxo") or _has_any(t, (
        "ceo", "chief executive officer",
        "cto", "chief technology officer",
        "cfo", "chief financial officer",
        "coo", "chief operating officer",
        "cmo", "chief marketing officer",
        "cro", "chief revenue officer",
        "cio", "chief information officer",
        "ciso", "chief information security officer",
        "cpo", "chief product officer",
        "clo", "chief legal officer",
        "chro", "chief human resources officer",
        "chief people officer",
        "chief data officer",
        "chief risk officer",
        "chief compliance officer",
        "chief commercial officer",
        "chief strategy officer",
        "chief investment officer",
        "founder", "co founder", "cofounder",
        "president",
        "managing director", "managing dr",
        "board member", "executive board member",
        "chair", "chairman", "chairwoman", "chairperson",
        "owner", "general partner", "managing partner",
        "investor",
        "pdg", "directeur general", "diretor geral",
    )):
        return "C-level or equivalent"

    # ── Director level ────────────────────────────────────────
    # Exclude "managing director" (already caught as C-level above)
    # and deputy/adjoint variants.
    if _has_any(t, (
        "director", "directeur", "directrice", "diretor", "diretora",
    )) and not _has_any(t, (
        "managing director", "managing dr",
        "adjoint", "adjointe", "adjunta",
        "deputy", "subdiretor", "sub director",
    )):
        return "Director level"

    # ── Manager level ─────────────────────────────────────────
    if s in ("team lead", "middle management") or _has_any(t, (
        "manager", "head of", "head",
        "lead", "team lead", "supervisor", "principal",
        "responsable", "gerente", "gestor", "gestora",
        "subgerente", "coordenador", "coordinator",
        "adjoint", "adjointe", "adjunta", "deputy",
    )):
        return "Manager level"

    # ── Associate level ───────────────────────────────────────
    if s == "entry level" or _has_any(t, (
        "associate", "analyst", "analyste", "analista",
        "representative", "coordinator", "assistant", "assistente",
        "assessor", "assessora", "conseiller", "conseillere",
        "charge", "chargee", "technicien", "technicienne",
        "tecnico", "tecnica", "employe", "employee",
        "bancaria", "bancario",
        "officer", "specialist", "specialista",
        "stagiaire", "instructor", "advisor",
        "administrador", "administrator",
        "graduate", "intern", "trainee",
        "consultant", "researcher", "fellow",
        "account executive", "development executive",
        "executive",
    )):
        return "Associate level"

    return "Other"


# ── JOB FUNCTION ───────────────────────────────────────────────

def classify_job_function(job_title: str, department: str = "") -> str:
    """Classify into a job function category."""
    t = _normalize(job_title)
    d = _normalize(department)
    combined = f"{t} {d}".strip()

    if _has_any(combined, (
        "sales", "business development", "account executive",
        "account manager", "relationship manager",
        "client officer", "private banker", "business banker",
        "financial advisor",
        "gestor de cliente", "gestora de cliente",
        "gestor comercial", "gestora comercial",
        "gerente de clientes", "gerente de empresas",
        "conseiller client", "conseiller clientele",
        "charge de clientele", "chargee de clientele",
        "conseillere clientele", "gestionnaire de clientele",
        "bancaria", "bancario", "clientele", "clientes",
        "commercial", "ventas", "vente", "vendite",
        "partnership", "partnerships", "growth",
        "demand generation", "export development", "revenue",
    )):
        return "Sales"

    if _has_any(combined, (
        "marketing", "brand", "communications", "communication",
        "public relations", "product marketing",
        "gestor de marketing", "relations publiques",
        "demand gen", "content", "pr",
    )):
        return "Marketing"

    if _has_any(combined, (
        "operations", "ops", "backoffice", "back office",
        "front office", "service clients", "service clientele",
        "technicien de banque", "technicienne de banque",
        "employe de banque", "employee de banque",
        "assistente de operacoes", "tecnico de operacoes",
        "customer success", "client success", "client experience",
        "program management", "programme management",
        "implementation", "delivery", "enablement",
        "operacoes", "processos",
        "reconciliation specialist",
        "project management officer", "pmo officer",
        "scrum master", "assistente administrativo",
        "administrator",
    )):
        return "Operations"

    if _has_any(combined, (
        "product", "product manager", "product lead",
        "product management", "payment solutions",
        "application specialist",
        "digital channels specialist",
    )):
        return "Product"

    if _has_any(combined, (
        "human resources", "resources humaines",
        "ressources humaines",
        "learning development",
        "gestionnaire paie",
        "charge de ressources humaines",
        "chargee des ressources humaines",
        "hr", "talent", "people", "recruit", "recruitment",
    )):
        return "Human Resources"

    if _has_any(combined, (
        "finance", "financial", "financial reporting",
        "credit", "credito", "analista de risco",
        "risk analyst", "assessor financeiro",
        "controleuse de gestion",
        "gestionnaire actif passif",
        "real estate investment analyst",
        "capital markets", "factoring", "confirming",
        "banca de empresas", "corporate banking",
        "payments", "payment", "banking",
        "embedded banking", "treasury", "investment",
    )):
        return "Finance"

    if _has_any(combined, (
        "technology", "technical",
        "software engineer", "software analyst",
        "ingenieur developpement logiciels", "developpeur",
        "ingenieur d etudes et de developpement",
        "cybersecurite", "business system analyst",
        "business analyst", "chef de projet bi",
        "data analyst", "analyste de donnees",
        "chief data officer", "data governance manager",
        "cto", "chief technology officer",
        "engineer", "engineering", "developer",
        "software", "architect", "security", "data",
    )):
        return "IT"

    if _has_any(combined, (
        "legal", "juriste", "juriste conseil",
        "juriste contentieux bancaire",
        "compliance", "compliance officer",
        "charge de conformite", "chargee de conformite",
        "conformite", "fatca", "crs", "kyc", "aml",
        "lcbft", "due diligence",
        "data protection officer", "dpo",
        "governo corporativo",
        "counsel", "attorney", "regulatory",
    )):
        return "Legal"

    if _has_any(combined, (
        "esg", "sustainability",
        "chief sustainability officer", "environmental",
    )):
        return "Environmental, Social, and Governance"

    if _has_any(combined, (
        "faculty", "professor", "teacher", "lecturer",
        "professeur", "docente",
    )):
        return "Teaching & Faculty"

    if _has_any(combined, (
        "government", "public sector", "ministry",
        "promotora publica",
    )):
        return "Government"

    return "Executive Leadership"


# ── ORGANISATION TYPE ──────────────────────────────────────────

def classify_org_type(
    industries: str = "",
    company: str = "",
    job_title: str = "",
    website: str = "",
    company_type: str = "",
    company_tech: str = "",
) -> str:
    """Classify into an organisation-type category."""
    combined = " ".join([
        _normalize(industries),
        _normalize(company),
        _normalize(job_title),
        _normalize(website),
        _normalize(company_type),
        _normalize(company_tech),
    ])

    if _has_any(combined, ("credit union service organization", "cuso")):
        return "Credit union service organization (CUSO)"
    if _has_any(combined, ("credit union",)):
        return "Credit union"
    if _has_any(combined, ("insurance", "assurance", "seguros", "insurtech", "insurer")):
        return "Insurance company"
    if _has_any(combined, (
        "wealth management", "asset management",
        "private wealth", "investment management", "patrimoine",
    )):
        return "Asset or wealth management firm"
    if _has_any(combined, (
        "venture capital", "private equity", "investor",
        "ventures", "capital", "vc", "partners", "startup",
    )):
        return "VC, PE or other investor"
    if _has_any(combined, ("community bank",)):
        return "Community bank"
    if _has_any(combined, ("neobank", "challenger bank", "digital bank")):
        return "Challenger or neobank"
    if _has_any(combined, ("retail bank",)):
        return "Retail bank"
    if _has_any(combined, (
        "bank", "banque", "banco", "banking",
        "financial services", "corporate banking",
        "commercial bank", "credito", "credit",
        "lending",
    )):
        return "Commercial or corporate bank"
    if _has_any(combined, (
        "startup fintech", "early stage fintech", "seed fintech",
    )):
        return "Startup fintech or solution provider"
    if _has_any(combined, (
        "fintech", "software", "platform", "payments",
        "technology", "tech", "systems", "analytics",
        "embedded banking", "saas", "ai", "blockchain",
        "crypto", "web3", "fusion",
    )):
        return "Established fintech or solution provider"
    if _has_any(combined, (
        "retailer", "merchant", "marketplace", "commerce",
        "isv", "retail", "ecommerce",
    )):
        return "Retailer, merchant, marketplace or integrated software vendor (ISV)"
    if _has_any(combined, (
        "media", "press", "news", "journal", "publication",
        "presse", "analyst",
    )):
        return "Media or sell side analyst"
    if _has_any(combined, (
        "government", "public sector", "ministry",
        "municipal", "federal", "gouvernement", "gobierno",
        "non profit", "nonprofit",
    )):
        return "Government"
    if _has_any(combined, (
        "consulting", "advisory", "legal", "accounting",
        "staffing", "professional services", "consultoria",
        "services firm", "vendor", "exhibitor",
    )):
        return "Professional services firm"
    if _has_any(combined, (
        "association", "nonprofit", "foundation", "charity",
        "philanthropy", "fondation", "industry body",
    )):
        return "Industry association or nonprofit"
    if _has_any(combined, (
        "university", "college", "school", "education",
        "research institute", "universite", "universidad",
        "faculty", "student", "professor",
    )):
        return "Higher education"
    if _has_any(combined, ("employee in transition",)):
        return "None (e.g. employee in transition)"

    return "Other"

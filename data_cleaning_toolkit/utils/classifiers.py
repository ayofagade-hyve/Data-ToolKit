"""Job title, function, and organisation type classification.

Features:
- Multi-language support (English, French, Portuguese, Spanish)
- Word-boundary regex matching
- Accent normalization via unicodedata
- LRU-cached pattern compilation
"""
import re
import unicodedata
from functools import lru_cache


def _normalize(value):
    text = str(value or "").lower()
    text = unicodedata.normalize("NFD", text)
    text = re.sub(r"[\u0300-\u036f]", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@lru_cache(maxsize=4096)
def _compile_pattern(phrase):
    return re.compile(r"\b" + re.escape(phrase) + r"\b")


def _matches(text, phrases):
    normalised = _normalize(text)
    for phrase in phrases:
        pattern = _compile_pattern(phrase.lower())
        if pattern.search(normalised):
            return True
    return False


VP_KEYWORDS = [
    "vice president", "vp ", "v.p.", "vp,", "svp", "evp", "avp",
    "vice presidente", "vice-presidente", "vice-president",
]

C_LEVEL_KEYWORDS = [
    "chief", "ceo", "cfo", "cto", "cio", "coo", "cmo", "cro", "cso",
    "c-level", "c-suite", "founder", "co-founder", "cofounder",
    "owner", "partner", "president", "managing director",
    "directeur general", "presidente", "fondateur", "cofondateur", "associe",
    "diretor geral", "fundador", "cofundador", "socio", "proprietario",
]

DIRECTOR_KEYWORDS = [
    "director", "head of", "head,", "global head",
    "senior director", "group director", "executive director",
    "directeur", "directrice", "responsable",
    "diretor", "diretora", "chefe de",
]

MANAGER_KEYWORDS = [
    "manager", "lead", "team lead", "supervisor",
    "coordinator", "chef de", "gerente", "gestionnaire",
    "chef d\'equipe", "coordenador", "coordenadora", "lider",
]

ASSOCIATE_KEYWORDS = [
    "associate", "assistant", "analyst", "specialist", "intern",
    "trainee", "junior", "jr", "entry level", "graduate",
    "executive", "officer", "representative", "agent",
    "adjoint", "adjointe", "stagiaire", "analyste",
    "assistente", "analista", "especialista", "estagiario",
    "estagiaria", "representante",
]


def classify_seniority(job_title, original_seniority=""):
    """Classify job seniority. VP checked BEFORE C-level."""
    if original_seniority and str(original_seniority).strip():
        return str(original_seniority).strip()
    if not job_title or not str(job_title).strip():
        return "Other"
    title = str(job_title)
    if _matches(title, VP_KEYWORDS):
        return "VP level"
    if _matches(title, C_LEVEL_KEYWORDS):
        return "C-level"
    if _matches(title, DIRECTOR_KEYWORDS):
        return "Director"
    if _matches(title, MANAGER_KEYWORDS):
        return "Manager"
    if _matches(title, ASSOCIATE_KEYWORDS):
        return "Associate"
    return "Other"


FUNCTION_MAP = {
    "Sales": ["sales", "account executive", "business development", "bdr", "sdr",
              "revenue", "commercial", "partnerships", "account manager",
              "ventes", "vendas", "ventas", "negocios"],
    "Marketing": ["marketing", "brand", "content", "communications", "pr ",
                   "public relations", "digital marketing", "growth", "demand gen",
                   "comunica", "mercadeo", "mercadotecnia"],
    "IT": ["it ", "information technology", "infrastructure", "devops",
            "systems admin", "network", "cybersecurity", "security",
            "helpdesk", "help desk", "support engineer",
            "informatique", "tecnologia da informacao"],
    "Engineering": ["engineer", "developer", "software", "programming", "backend",
                     "frontend", "full stack", "fullstack", "sre", "qa ",
                     "quality assurance", "test engineer", "data engineer",
                     "ingenieur", "developpeur", "engenheiro", "desenvolvedor",
                     "ingeniero", "desarrollador"],
    "Finance": ["finance", "accounting", "accountant", "controller", "treasury",
                 "audit", "tax ", "financial", "comptable",
                 "financeiro", "contabilidade", "finanzas", "contabilidad"],
    "Legal": ["legal", "lawyer", "attorney", "counsel", "compliance",
               "regulatory", "paralegal", "juridique", "avocat",
               "juridico", "advogado", "abogado"],
    "HR": ["human resources", "hr ", "talent", "recruiting", "recruitment",
            "people", "workforce", "compensation", "benefits",
            "ressources humaines", "recursos humanos", "rh "],
    "Operations": ["operations", "logistics", "supply chain", "procurement",
                    "facilities", "warehouse", "fleet", "ops ",
                    "logistique", "logistica", "operacoes", "operaciones"],
    "Product": ["product", "product manager", "product owner", "ux ",
                 "user experience", "ui ", "design", "product design",
                 "produit", "produto", "producto"],
}


def classify_job_function(job_title, department=""):
    """Classify job function from title and department."""
    combined = f"{job_title or ''} {department or ''}"
    if not combined.strip():
        return "Other"
    for function_name, keywords in FUNCTION_MAP.items():
        if _matches(combined, keywords):
            return function_name
    return "Other"


ORG_TYPE_MAP = {
    "Bank": ["bank", "banking", "banque", "banco", "savings", "credit union", "building society"],
    "Fintech": ["fintech", "financial technology", "neobank", "neo-bank",
                 "payments", "payment", "paytech", "regtech", "wealthtech",
                 "insurtech", "blockchain", "crypto", "defi"],
    "Insurance": ["insurance", "insurer", "underwriting", "reinsurance",
                   "assurance", "seguro", "seguros"],
    "VC/PE": ["venture capital", "private equity", "vc ", "pe ",
               "investment fund", "hedge fund", "asset management",
               "capital risque", "capital de risco"],
    "Retailer": ["retail", "retailer", "e-commerce", "ecommerce",
                  "store", "shop", "marketplace", "varejo"],
    "Government": ["government", "gov ", "public sector", "ministry",
                    "agency", "council", "municipality",
                    "gouvernement", "governo", "gobierno"],
    "Consultant": ["consulting", "consultant", "advisory", "advisors",
                    "professional services", "conseil", "consultoria"],
    "Technology": ["technology", "software", "saas", "cloud", "platform",
                    "tech", "digital", "ai ", "artificial intelligence",
                    "machine learning", "data analytics",
                    "technologie", "tecnologia"],
    "Media": ["media", "publishing", "broadcast", "news", "entertainment",
               "advertising", "creative", "editora", "publicidade", "medios"],
}


def classify_org_type(industries="", company="", job_title="",
                       website="", company_type="", company_tech=""):
    """Classify organisation type using multiple fields."""
    combined = " ".join([str(industries or ""), str(company or ""),
                          str(job_title or ""), str(website or ""),
                          str(company_type or ""), str(company_tech or "")])
    if not combined.strip():
        return "Other"
    for org_type, keywords in ORG_TYPE_MAP.items():
        if _matches(combined, keywords):
            return org_type
    return "Other"

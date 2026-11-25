from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class Issue(BaseModel):
    kind: str  # ambiguity|incomplete|untestable|missing_source|undefined_term|duplicate|conflict|out_of_scope|low_confidence|security_flag
    message: str
    severity: str = "medium"  # low|medium|high
    question: Optional[str] = None
    related: list[str] = []


class RegRef(BaseModel):
    kb_id: str
    title: str
    source: str
    jurisdiction: str
    effective_date: str
    version: str
    verified: bool
    score: float
    rationale: str = ""


class Requirement(BaseModel):
    id: str
    statement: str
    categories: list[str] = []
    source_stakeholder: str
    source_doc: str = ""
    source_quote: str = ""
    justification: str = ""
    priority: str = "Should"
    dependencies: list[str] = []
    assumptions: list[str] = []
    acceptance_criteria: list[str] = []
    regulations: list[RegRef] = []
    risk_level: str = "Low"
    risk_score: int = 1
    confidence: float = 0.7
    approval_status: str = "pending"  # pending|accepted|rejected
    approved_by: Optional[str] = None
    waiver_note: Optional[str] = None
    issues: list[Issue] = []
    needs_human: bool = False
    module: str = "GEN"


class Conflict(BaseModel):
    id: str
    kind: str  # duplicate|contradiction|numeric|tension
    req_ids: list[str]
    description: str
    severity: str = "medium"
    resolution_options: list[str] = []
    status: str = "open"  # open|resolved
    resolution_note: Optional[str] = None


class Gap(BaseModel):
    kb_id: str
    control: str
    description: str
    suggested_requirement: str
    severity: str = "high"


class RiskItem(BaseModel):
    id: str
    title: str
    category: str
    likelihood: int
    impact: int
    score: int
    rating: str
    mitigation: str
    verification: str
    req_ids: list[str] = []


class SdlcResult(BaseModel):
    factors: dict[str, float]
    ranking: list[dict]
    rules_fired: list[str]
    recommended: str
    explanation: str
    workflow: list[dict]
    signoffs: dict[str, str] = {}  # role -> user name


class SourceDoc(BaseModel):
    name: str
    stakeholder: str
    text: str


class ProjectParams(BaseModel):
    duration_months: float = 2
    team_size: int = 4
    stakeholder_availability: int = 3  # 1-5
    legacy_dependence: int = 3  # 1-5
    continuous_delivery_need: int = 2  # 1-5
    budget_pressure: int = 3  # 1-5
    pharmacy_type: str = "retail"


class RunRequest(BaseModel):
    project_name: str = "PharmaReq Demo"
    documents: list[SourceDoc]
    params: ProjectParams = Field(default_factory=ProjectParams)


class Run(BaseModel):
    run_id: str
    project_name: str
    created: str
    mode: str
    status: str = "draft"  # draft|baselined
    params: ProjectParams
    documents: list[SourceDoc]  # masked text only
    requirements: list[Requirement] = []
    conflicts: list[Conflict] = []
    gaps: list[Gap] = []
    risks: list[RiskItem] = []
    sdlc: Optional[SdlcResult] = None
    validation: dict = {}
    security_flags: list[str] = []
    pii_masked: dict[str, int] = {}
    metrics: dict = {}
    artifacts: list[str] = []

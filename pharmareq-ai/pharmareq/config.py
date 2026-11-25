"""Central configuration. Reads an optional .env file, then environment variables."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv():
    p = ROOT / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if v.strip():
                    os.environ.setdefault(k.strip(), v.strip())


_load_dotenv()

DATA_DIR = Path(os.getenv("PHARMAREQ_DATA", ROOT / "var"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "pharmareq.db"
OUTPUT_DIR = Path(os.getenv("PHARMAREQ_OUT", ROOT / "outputs"))
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
MODE = os.getenv("PHARMAREQ_MODE", "auto")  # auto | offline
RETRIEVAL_MIN_SCORE = float(os.getenv("RETRIEVAL_MIN_SCORE", "0.15"))
LOW_CONFIDENCE = float(os.getenv("LOW_CONFIDENCE", "0.55"))

USERS = json.loads((ROOT / "config" / "users.json").read_text())

# Who may do what (human-in-the-loop gates, plan section 16)
ROLE_PERMISSIONS = {
    "run_pipeline": {"analyst", "project_manager"},
    "approve_regulatory": {"compliance_officer", "pharmacist"},
    "approve_patient_safety": {"pharmacist"},
    "approve_security": {"security", "architect"},
    "approve_general": {"analyst", "pharmacist", "compliance_officer", "project_manager"},
    "resolve_conflict": {"pharmacist", "compliance_officer", "project_manager"},
    "baseline": {"project_manager"},
}
SDLC_SIGNOFF_ROLES = ["project_manager", "architect", "security", "compliance_officer"]

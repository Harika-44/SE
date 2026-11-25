import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="pharmareq_test_")
os.environ["PHARMAREQ_DATA"] = os.path.join(_tmp, "var")
os.environ["PHARMAREQ_OUT"] = os.path.join(_tmp, "out")
os.environ["PHARMAREQ_MODE"] = "offline"   # tests never call an LLM

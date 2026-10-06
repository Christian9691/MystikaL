import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import Optional

TIME_LIMIT = 10  # seconds before the spell is dispelled

_FRAME = re.compile(r'(File ")([^"]*)(", line )(\d+)')


@dataclass
class CastReport:
    stdout: str
    stderr: str
    problem: Optional[str]
    timed_out: bool
    exit_code: int


def _retarget(stderr: str, line_map: dict[int, int], real_path: str) -> str:
    """Rewrite only the 'File ..., line N' frames that belong to our script."""
    def swap(m: re.Match) -> str:
        if os.path.normcase(m.group(2)) != os.path.normcase(real_path):
            return m.group(0)
        n = int(m.group(4))
        return f"{m.group(1)}<mystika>{m.group(3)}{line_map.get(n, n)}"
    return _FRAME.sub(swap, stderr)


def cast(python_code: str, line_map: dict[int, int], time_limit: int = TIME_LIMIT) -> CastReport:
    """Run the code. Never raises; everything is reported in CastReport."""
    if not python_code.strip():
        return CastReport("", "", None, False, 0)

    try:
        with tempfile.TemporaryDirectory(prefix="mystika_", ignore_cleanup_errors=True) as workdir:
            script = os.path.join(workdir, "spell.py")
            with open(script, "w", encoding="utf-8") as fh:
                fh.write(python_code)

            env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
            try:
                done = subprocess.run(
                    [sys.executable, script],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=time_limit,
                    stdin=subprocess.DEVNULL,   # input() fails fast instead of hanging
                    env=env,
                    cwd=workdir,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            except subprocess.TimeoutExpired:
                return CastReport(
                    "", "", f"The spell ran longer than {time_limit}s and was dispelled.", True, -1
                )

            stderr = _retarget(done.stderr or "", line_map, script).replace(script, "<mystika>")
            problem = stderr.strip() if done.returncode != 0 and stderr.strip() else None
            return CastReport(
                (done.stdout or "").rstrip("\n"), stderr, problem, False, done.returncode
            )
    except Exception as exc:  # unexpected OS-level trouble
        return CastReport("", "", f"[Caster] Unexpected failure: {exc}", False, -1)
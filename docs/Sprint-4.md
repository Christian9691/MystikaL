# Sprint 4: Executor Implementation

**Status:** 0/5 tasks completed

## Tasks

- [ ] #24. Write Python code to tempfile with `tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w")`
- [ ] #25. Execute via `subprocess.run(["python3", tmp_path], capture_output=True, text=True, timeout=10)`
- [ ] #26. Handle Windows fallback to `["python", tmp_path]`
- [ ] #27. Implement 10-second timeout with `TimeoutExpired` handling
- [ ] #28. Implement stderr line number remapping to PussyCat source lines

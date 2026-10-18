# Implementation host

Windows, PowerShell, timezone Asia/Dhaka. Python 3.12.14 and Node 24.19.0 are available in the Codex runtime bundle, although not on normal PATH.

Current full executable paths:

```text
C:\Users\jesan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
C:\Users\jesan\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe
C:\Users\jesan\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd
C:\Users\jesan\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe
```

The isolated Python environment is `.venv`. Frontend dependencies are local to `frontend/node_modules`. Dependency downloads and the Vite build needed sandbox escalation; installation and compilation then succeeded. The Vite bundler reads parent directories during resolution, which was denied by the sandbox before escalation. This is not an application defect.

Useful direct frontend commands when pnpm is not on PATH, run from `frontend`:

```powershell
& 'C:/Users/jesan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' node_modules/typescript/bin/tsc -b
& 'C:/Users/jesan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' node_modules/vite/bin/vite.js build
& 'C:/Users/jesan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' node_modules/@playwright/test/cli.js test
```

Chrome is installed and used through Playwright's `chrome` channel. Docker and PostgreSQL executables were not found. No unrelated system installation or public deployment was performed.

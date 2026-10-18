# Run BhumiGuard on Windows — first-time guide

This guide uses **Windows 11, PowerShell, Python 3.12, Node 24 and the local SQLite database**. You do not need Docker, PostgreSQL, a hosting account or an AI key. Internet is needed for installation; the main demo works offline afterward.

If you are using the original development computer and the app already works, skip to **“Tomorrow: start it again”** and use its existing folder. The first-time steps below are for a new machine or a fresh source copy.

## 1. Put the project in a simple folder

Copy the source ZIP/folder using a USB drive. Extract the ZIP using **right-click → Extract All**. Do not run the project from inside the ZIP.

Open File Explorer, type `%USERPROFILE%` in its address bar and press Enter. Create a folder named `Projects`, put the extracted project inside it, and rename that folder to `BhumiGuard`.

You should now have:

```text
C:\Users\YOUR_WINDOWS_NAME\Projects\BhumiGuard\README.md
C:\Users\YOUR_WINDOWS_NAME\Projects\BhumiGuard\backend\
C:\Users\YOUR_WINDOWS_NAME\Projects\BhumiGuard\frontend\
```

The commands below automatically use your Windows username through `$env:USERPROFILE`; you do not type `YOUR_WINDOWS_NAME`.

Keep all source folders and configuration/lockfiles. For a **fresh setup**, leave out old `.venv`, `frontend/node_modules`, `runtime`, `.env`, and test/cache folders. Keep the original project intact. A copied Python environment may point to the other computer and will not reliably work.

A fresh setup creates the 22 fictional scenarios, without previous review decisions. If you want existing saved reviews, first preserve a separate copy of the old entire `runtime` folder. Database document paths are absolute; moving that database to a different folder/computer may require path migration. This guide does not silently overwrite old data.

## 2. Install Python 3.12

1. Open the official [Python Windows download page](https://www.python.org/downloads/windows/).
2. Install the **Python install manager** offered there. Use the normal manager installer, not an embeddable ZIP or source archive.
3. Close old Terminal windows. Open Start, type **PowerShell**, and open it normally. Administrator mode is not needed for project commands.
4. Run:

```powershell
py install 3.12
py -3.12 --version
```

Expect `Python 3.12.x`. If Python 3.12 was already installed with the older Python launcher, just checking `py -3.12 --version` may be enough. If `py install` is treated as a script filename, you have the older launcher: use `pymanager install 3.12` after installing the manager, then check again. The project has been tested with Python 3.12; using the newest unrelated major/minor version is unnecessary.

## 3. Install Node 24

1. Open [Node's official download page](https://nodejs.org/en/download).
2. Select **Node 24**, **Windows**, and the **Windows Installer (.msi)**. Choose x64 for a typical Intel/AMD laptop; choose ARM64 only if your laptop is Windows on ARM.
3. Run the installer and keep the normal options, including adding Node to PATH. Optional native build tools are not needed for the normal prebuilt dependency installation.
4. Close and reopen PowerShell so it sees the new installation.

Check Node and install pnpm:

```powershell
node --version
npm.cmd --version
npm.cmd install --global pnpm@11.25.0
pnpm.cmd --version
```

Expect Node `v24...` and pnpm `11.25.0`. We use `.cmd` to avoid PowerShell blocking npm/pnpm script wrappers. There is no need to change your system-wide script execution policy.

## 4. Enter the project folder

Paste each code block into PowerShell, press Enter and wait until it finishes. Stop if there is an error.

```powershell
cd "$env:USERPROFILE\Projects\BhumiGuard"
Get-Location
Get-ChildItem
```

The listing should show `README.md`, `backend`, and `frontend`. If you placed the project somewhere else, open that folder in File Explorer, copy its full path, and use `cd 'YOUR ACTUAL PATH'` instead. Keep quotes around paths containing spaces.

Choose the local database and local HTTP settings for this PowerShell session:

```powershell
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:DEMO_PASSWORD -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
$env:APP_ENV = 'local'
$env:COOKIE_SECURE = 'false'
$env:ALLOWED_ORIGINS = 'http://127.0.0.1:8000,http://localhost:8000'
```

These `Remove-Item Env:...` commands only clear environment variables in this Terminal session; they do not delete project files. You do not need a `.env` file for this setup.

## 5. Install the Python packages

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.lock
```

The `.venv` folder holds this project's Python packages. We call its Python directly, so you do not need to run `Activate.ps1`.

## 6. Create the local database and demo account

For a **fresh copy without an existing `runtime/demo.db`**, run:

```powershell
.\.venv\Scripts\python.exe -m alembic -c backend/alembic.ini upgrade head
.\.venv\Scripts\python.exe -m backend.app.seed --username reviewer
```

When asked for the new password, type a temporary password of at least 12 characters, such as `DemoSetup2026!`, then press Enter. Characters do not appear while typing; this is normal. You should see a message that 22 fictional scenarios were seeded.

Rename that account to your requested public demo login:

```powershell
.\.venv\Scripts\python.exe -m scripts.configure_demo_login --previous reviewer --username jesan
```

When it asks `Public demo password:`, type `12345`, then press Enter. This preserves the account's cases and updates the welcome page's login details.

Your login is now **jesan / 12345**. This is an intentionally public local-demo account. Do not rerun the fresh-account steps on every startup, and do not use database reset to fix a login error.

## 7. Build the frontend

```powershell
cd frontend
pnpm.cmd install --frozen-lockfile
pnpm.cmd build
cd ..
```

The first install can take a few minutes. A successful build creates `frontend/dist`. The last command returns to the project root. Bangla fonts are included locally.

## 8. Start the app and log in

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Wait for `Uvicorn running on http://127.0.0.1:8000`. Leave PowerShell open; it is the running server.

Open Edge, Chrome or Firefox. Type this into the browser's address bar:

```text
http://127.0.0.1:8000
```

Use **HTTP**, not HTTPS. Read the glass notice, click **আমি পড়েছি — এগিয়ে যাই / I've read this — continue**, and sign in:

```text
Username: jesan
Password: 12345
```

The welcome page includes DIU Jex Stone and both creators' GitHub links. **About this demo / ডেমো পরিচিতি** opens it again. GitHub links need internet; the local review workflow does not.

## 9. Check that it really works

1. Select English if that is easier for you.
2. Click **New review**.
3. Choose **Dhaka → Savar → Birulia** and **Valid transfer**.
4. Tick the fictional-data confirmation and create the review.
5. Inspect the document, confirm/save the critical fields and run analysis.
6. Enter reviewer notes and save a decision.
7. Refresh the page and reopen the case; the decision should remain saved.

Most imported upazilas do not yet have verified mouza data; use the supported demo location above. Try the provided sample PDFs from `sample-documents` if desired. Seeded fixtures and manual entry work without live AI.

## Tomorrow: start it again

For the new folder used in this guide:

```powershell
cd "$env:USERPROFILE\Projects\BhumiGuard"
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
$env:APP_ENV = 'local'
$env:COOKIE_SECURE = 'false'
$env:ALLOWED_ORIGINS = 'http://127.0.0.1:8000,http://localhost:8000'
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

For **Jesan's original development computer**, use this folder instead in the first command:

```powershell
cd 'C:\Users\jesan\OneDrive\Desktop\Bumi Guard'
```

Then run the remaining environment/server commands above. Its existing `.venv` already works; no Python/Node reinstall is needed merely to start that existing setup.

Open `http://127.0.0.1:8000`. No reinstall, seed or build is needed unless dependencies/source code changed. To stop, click PowerShell and press **Ctrl + C**. Your saved data remains. Closing only the browser does not stop the server.

## Back up your reviews

Stop the server first. Using File Explorer, copy the **entire `runtime` folder** into a dated backup location. It contains the SQLite database, documents and local demo credentials. Keep the source project too. Restore into the same absolute project folder; moving to another location or Ubuntu requires reviewing document paths. Never delete `runtime` as a troubleshooting shortcut.

## Common problems

| Problem | Fix |
|---|---|
| `py` or `node` is not recognized | Finish installation, then close and reopen PowerShell. Check the version commands. |
| `npm.ps1 cannot be loaded` | Use `npm.cmd` and `pnpm.cmd` as shown. No execution-policy change is needed. |
| `Activate.ps1` is blocked | Do not activate; use `.\.venv\Scripts\python.exe` directly. |
| `No module named backend` | You are probably inside `frontend`. Run `cd ..` and check `Get-ChildItem`. |
| `.venv` refers to another computer | Use a fresh source copy and create its own `.venv`. Keep existing data backed up. |
| `No matching distribution found` | Check internet and Python 3.12. Preserve the lockfile and share the full error. |
| `Cannot find path` | Use your actual extracted project folder. Check for an extra nested folder from the ZIP. |
| Port 8000 already in use | Stop the old project server with Ctrl+C in its PowerShell window. |
| Browser cannot connect | Keep the server running and use `http://127.0.0.1:8000`. |
| Login fails | On a fresh install, finish step 6. On an existing installation, read `runtime/local-account.txt`. Do not reset. |
| Website missing / API JSON shown | Check `frontend/dist/index.html`; build the frontend and restart the server. |
| Recent design change is not visible | Run `pnpm.cmd build` inside `frontend`, then refresh. |
| Copied database cannot open source documents | Its absolute paths still point to the old folder. Keep backups and request a path migration. |

## Optional tests and offline rehearsal

From the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m scripts.evaluate
```

Browser tests are optional. They require installed **Google Chrome** (the test configuration uses the `chrome` channel). Keep the app running in one PowerShell window; in a second window enter the project folder, then:

```powershell
cd frontend
pnpm.cmd test:e2e
```

These tests create extra fictional cases. The configured login is read from the local account file. No live AI call is needed.

Before the contest, turn off Wi-Fi, restart the local server and complete one seeded review. Keep the project and its `runtime` folder on the laptop. Internet-free operation means running the installed app, not installing missing packages without internet.

Official setup references checked 18 October 2026: [Python Windows setup](https://docs.python.org/3/using/windows.html), [Node download](https://nodejs.org/en/download), [pnpm installation](https://pnpm.io/installation). The existing Windows app is tested; installing these prerequisites on a second fresh Windows machine was not executed here.

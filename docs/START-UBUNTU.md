# Run BhumiGuard on Ubuntu — first-time guide

This guide starts from a fresh project copy on your Ubuntu laptop. You do not need coding experience, Docker, PostgreSQL, a hosting account, or an AI API key. The local database is a file called `runtime/demo.db` (SQLite).

**Internet is needed for the first installation. After setup, the main demo works offline.** Live AI extraction and opening GitHub links still need internet. Do this setup before travelling to the contest.

The commands below target **Ubuntu 24.04 LTS with Python 3.12**, and Node 24. Ubuntu installation has not been executed on the current Windows development machine; the app has been tested locally on Windows. If you use a different Ubuntu release, first check the versions as explained below. Do not replace Ubuntu's system Python.

## 1. Put the project on your laptop

Copy the source project using a USB drive or ZIP. If a project GitHub repository is available, you can download its ZIP; a creator's profile page is not itself the project repository. No project repository URL is assumed here.

In Ubuntu's **Files** app, open **Home**, create a folder named `Projects`, and place the project folder inside it. Rename the project folder to `BhumiGuard`. The final layout should be:

```text
Home/
  Projects/
    BhumiGuard/
      README.md
      backend/
      frontend/
      data/
      docs/
      scripts/
      sample-documents/
      tests/
```

Keep all source/configuration files, including `frontend/pnpm-lock.yaml`, `frontend/pnpm-workspace.yaml`, and `backend/requirements.lock`. Extract the ZIP first: do not try to run from inside an archive. If there is an extra folder inside the ZIP, use the folder that directly contains `README.md` and `backend`.

For this **fresh installation**, do not transfer `.venv`, `frontend/node_modules`, `runtime`, `.env`, or test/cache folders from Windows. They contain machine-specific dependencies or existing local data. Keep the original Windows project intact. A fresh setup recreates the 22 demo scenarios; it does not transfer previous review decisions.

**Want your old saved reviews too?** Keep a separate backup of the entire old `runtime` folder. Document paths currently stored in the database are absolute Windows paths. Copying that database onto Ubuntu alone will not make those documents work; a path migration is needed. This guide intentionally creates a fresh demo instead.

## 2. Open Terminal and learn the two rules

Press **Ctrl + Alt + T**. This opens Terminal, where you type commands.

- Copy one code block at a time. Paste with **Ctrl + Shift + V**, then press **Enter**. Wait for it to finish before continuing.
- If you see an error, stop at that step and use the troubleshooting table below. Do not keep pasting later commands.

Check your Ubuntu release:

```bash
cat /etc/os-release
```

Look for `VERSION_ID="24.04"`. These instructions use its normal Python 3.12 packages. Ubuntu 22.04's default Python is older than this project's target. If your version differs, share the output before following the Python installation steps; a separate Python 3.12 environment may be needed, without changing system Python.

## 3. Install Python and small setup tools

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl ca-certificates git
```

If Terminal asks for a password, type **your Ubuntu login password**, not `12345`. Nothing appears while you type; that is normal. Press Enter.

Check Python:

```bash
python3 --version
```

On Ubuntu 24.04, expect `Python 3.12.x`. The last number may differ.

## 4. Install Node 24 and pnpm

Node builds the website. pnpm installs its dependencies. You only need to build once unless the frontend code changes.

These commands download and run the official nvm project's installer, then install Node in your user account:

```bash
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh -o /tmp/bhumiguard-nvm-install.sh
bash /tmp/bhumiguard-nvm-install.sh
source ~/.bashrc
nvm install 24
nvm use 24
nvm alias default 24
npm install --global pnpm@11.25.0
```

Do not add `sudo` to the Node/npm commands. Check the results:

```bash
node --version
pnpm --version
```

Expect `v24...` and `11.25.0`. We pin pnpm to the project's setup version instead of installing whatever future version is newest.

## 5. Enter the project folder

```bash
cd "$HOME/Projects/BhumiGuard"
pwd
ls
```

`pwd` shows your current folder. `ls` should list `README.md`, `backend`, and `frontend`. If it does not, fix the folder location before continuing. All remaining commands start from this project folder unless a step says otherwise.

Use local mode and remove possible connection overrides from this Terminal session:

```bash
unset DATABASE_URL DEMO_PASSWORD OPENAI_API_KEY
export APP_ENV=local
export COOKIE_SECURE=false
export ALLOWED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

You do not need to create `.env` for this path. Direct Python commands use the shell environment; `.env` is automatically read by Docker Compose only.

## 6. Install the Python dependencies

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.lock
```

`.venv` is a private Python environment for this project. These commands do not change Ubuntu's system packages. We use its Python directly, so there is no separate activation step.

## 7. Create the database and demonstration cases

This step is for a **fresh copy without old `runtime/demo.db`**:

```bash
.venv/bin/python -m alembic -c backend/alembic.ini upgrade head
.venv/bin/python -m backend.app.seed --username reviewer
```

When asked for the new password, enter a temporary password of at least 12 characters, for example `DemoSetup2026!`. It will not appear while you type. The seed creates 22 fictional cases.

Now set the requested public demo login:

```bash
.venv/bin/python -m scripts.configure_demo_login --previous reviewer --username jesan
```

At `Public demo password:`, type `12345` and press Enter. The account is renamed while preserving its cases. The welcome notice now displays:

```text
Username: jesan
Password: 12345
```

Do not repeat this fresh-account procedure every time you start the app. Do not use a reset command: reset deletes saved reviews.

## 8. Build the website

```bash
cd frontend
pnpm install --frozen-lockfile
pnpm build
cd ..
```

Wait for a successful build. It creates `frontend/dist`. `cd ..` returns you to the main project folder. The build includes the Bangla font locally.

## 9. Start BhumiGuard

```bash
.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

When you see `Uvicorn running on http://127.0.0.1:8000`, leave Terminal open. The command keeps running because it is serving the app; it is not stuck.

Open Firefox or Chrome. Type this into the **address bar**:

```text
http://127.0.0.1:8000
```

Use `http`, not `https`. This address means “this laptop”; it is not a public website.

Read the glass welcome notice, click **আমি পড়েছি — এগিয়ে যাই / I've read this — continue**, and log in with `jesan` / `12345`. You can switch to English at the top. Use **About this demo / ডেমো পরিচিতি** to reopen the notice.

## 10. Try one complete case

1. Click **New review**.
2. Use **Dhaka → Savar → Birulia**. Other districts are available, but most upazilas do not yet have imported verified mouzas.
3. Choose **Valid transfer** and tick the fictional-data confirmation.
4. Create the review, inspect its fields, confirm them and save.
5. Run analysis, inspect the findings, enter reviewer notes and record a decision.
6. Refresh the browser and reopen the case. The saved decision should remain.

For offline use, choose seeded scenarios or manual entry. Do not use the live extraction button. Sample fictional PDFs are in `sample-documents`.

## Tomorrow: only start the server

You do **not** need to reinstall, seed or build again. Open Terminal and run:

```bash
cd "$HOME/Projects/BhumiGuard"
unset DATABASE_URL OPENAI_API_KEY
export APP_ENV=local
export COOKIE_SECURE=false
export ALLOWED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Then open `http://127.0.0.1:8000`. To stop, click the Terminal window and press **Ctrl + C**. Closing the browser does not stop the server. Stopping the server does not delete your data.

## Keep your work safe

Saved cases live in `runtime/demo.db`; generated/uploaded documents and demo login configuration also live in `runtime`. Before backing up, stop the server with Ctrl+C, then copy the **entire `runtime` folder** to a dated backup folder using Files. Keep the project source too. Restore to the same project location; moving across operating systems or to a different absolute path needs document-path migration. Do not delete `runtime` while cleaning dependencies.

## If something goes wrong

| What you see | What to do |
|---|---|
| `No such file or directory` after `cd` | Check the folder name/location in Files. Linux names are case-sensitive. Keep quotes around paths with spaces. |
| `nvm: command not found` | Run `source ~/.bashrc`, or close and reopen Terminal. |
| `pnpm: command not found` | Run `nvm use 24`, then `npm install --global pnpm@11.25.0`. |
| `ensurepip` or venv unavailable | Run `sudo apt install python3-venv`, then repeat environment creation. |
| `externally-managed-environment` | Use `.venv/bin/python -m pip ...`, not system `pip`. |
| A pinned dependency cannot download | Check internet and `python3 --version`. Keep the lockfile; share the exact error instead of changing versions at random. |
| Python executable mentions Windows or `Scripts` | A Windows `.venv` was copied. Use a fresh source copy and create the Ubuntu environment; preserve the old project. |
| `No module named backend` | Return to the project root: `cd "$HOME/Projects/BhumiGuard"`. |
| Browser cannot connect | Start the server, keep Terminal open, and use the exact HTTP address above. |
| Port 8000 already in use | Find the previous project Terminal and press Ctrl+C. Run one server at a time. |
| Login fails | Finish step 7 on a fresh installation. On an existing installation, check `runtime/local-account.txt`; do not reset the database. |
| API JSON instead of the website, or missing page | Check that `frontend/dist/index.html` exists. Complete step 8, then restart the server. |
| Old design after editing | Rebuild with `pnpm build` inside `frontend`, then refresh. |
| Missing old documents after copying a database | Windows absolute paths are not portable. Keep the backup and request a path migration. |

## Optional checks before the contest

With the app stopped, from the project root:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m scripts.evaluate
```

Browser automation is optional and needs Google Chrome plus additional Linux browser dependencies; it is not necessary to run the app. The project currently configures Playwright's `chrome` channel. Follow the ordinary manual workflow above first.

Finally, turn off Wi-Fi, restart the server using the “Tomorrow” commands, log in, open a seeded document and save a decision. That is your offline rehearsal. Re-enable Wi-Fi when finished if desired.

Setup references checked 18 October 2026: [Node download](https://nodejs.org/en/download), [official nvm installation](https://github.com/nvm-sh/nvm#installing-and-updating), [pnpm installation](https://pnpm.io/installation). No Ubuntu installation or browser run is claimed from the Windows host.

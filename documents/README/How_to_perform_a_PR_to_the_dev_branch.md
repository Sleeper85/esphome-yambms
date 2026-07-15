# YamBMS - How to perform a PR to the dev branch

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

## 1. Fork the repository

This step still happens on the GitHub website: go to https://github.com/Sleeper85/esphome-yambms and click **Fork** (top right).

## 2. Clone your fork with GitHub Desktop

- Open GitHub Desktop → **File → Clone Repository**
- In the **GitHub.com** tab, select `YOUR_USERNAME/esphome-yambms`
- Choose a local folder and click **Clone**
- GitHub Desktop will ask: *"How are you planning to use this fork?"* → select **To contribute to the parent project** (this makes syncing with the original repo easier later)

## 3. Switch to the `dev` branch

- Click the **Current Branch** button (top toolbar)
- Select `dev` from the list
- Click **Fetch origin** to make sure it's up to date

## 4. Create a new branch based on `dev`

- Click **Current Branch → New Branch**
- Name it something meaningful, e.g. `PR_fix_EOC_detection`
- ⚠️ In the dialog, GitHub Desktop asks which branch to base it on — select `dev`, not `main`
- Click **Create Branch**

## 5. Make your changes and commit

- Edit the files with your usual editor (VS Code, etc.)
- Back in GitHub Desktop, your modified files appear in the left panel
- Check the files you want to include
- Write a commit summary (e.g. *"Fix false EOC detection under low PV production"*) and click **Commit to PR_fix_EOC_detection**

## 6. Publish the branch**

- Click **Publish branch** (top toolbar). This pushes your branch to your fork on GitHub.

## 7. Open the Pull Request

- Click **Branch → Create Pull Request** (or the **Preview Pull Request** button). This opens GitHub in your browser.
- Verify the settings:
  - **base repository:** `Sleeper85/esphome-yambms` → **base:** `dev`
  - **head repository:** your fork → **compare:** `PR_fix_EOC_detection`
- ⚠️ Again, GitHub may default to `main` as the base — switch it to `dev`
- Add a clear title and description, then click **Create pull request**

## Keeping your branch up to date later (if needed)

- In GitHub Desktop: **Branch → Update from upstream/dev** (available if you selected "contribute to parent project" when cloning)
- Or: **Current Branch → choose your branch → Branch → Rebase current branch...** onto `upstream/dev`
- Then **Push origin** (Desktop will prompt for a force push if you rebased)

The main advantage for contributors: no command line needed at all, except the initial fork which is always done on the website.
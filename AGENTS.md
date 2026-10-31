# Repository navigation for AI

Read this map before choosing a workspace. Existing main branch; preserve concurrent changes.

| Path | Purpose | Start |
|---|---|---|
| app/ | Original Android WebView wrapper for ChatGPT | README.md |
| .github/ | Repository workflows, including Android builds | Inspect relevant workflow only |
| build.gradle, settings.gradle, gradle.properties | Root Android build configuration | Leave alone during CF research |
| cf2018/ | Original CF2018 research, original new code/tests, historical evidence | cf2018/AGENTS.md |
| cf2018v2/ | Version 2 of the CF2018 knowledge/workspace organization; same restoration mission and game version | [START](cf2018v2/START.md) |
| README.md | Original app description and workspace links | [Navigation](NAVIGATION.md) |

CF2018 work starts in cf2018v2. Existing implementation/evidence stays in cf2018; do not move or duplicate it blindly. Each folder's AGENTS applies within that folder. Updating the old implementation also requires its operating contract.
Public repository: no original game binaries/assets, raw dumps/captures, account/session contents, keys or credentials. No scheduled workers or live phone experiments automatically. Use only the owner's authorized despairarc000 GitHub connection. Source links do not establish local access.

# Replace the published dashboard

1. Extract the revised ZIP.
2. Back up the existing repository outside the public website as appropriate.
3. Replace the previous site's files with the extracted contents, preserving any unrelated repository settings such as a custom-domain CNAME when applicable. Do not delete the local `.git` directory when working in a Git checkout.
4. Explicitly delete obsolete `data/narratives/`, `privacy/`, the old sanitization script, earlier standalone HTML copies, and outdated docs/screenshots. Uploading replacement files alone does not remove these old assets.
5. Confirm `index.html`, `.nojekyll`, `assets/`, and `data/` are directly in the repository root.
6. Keep Settings → Pages configured to Deploy from a branch → main → /(root). Commit the file additions, modifications, and deletions together.
7. When the deployment completes, hard-refresh the page and check both dashboard modes.

Existing project URL:
https://kaifalu.github.io/HUD-CDBG-DR-Fund-Dashboard-Hierarchical/

Pages settings:
https://github.com/kaifalu/HUD-CDBG-DR-Fund-Dashboard-Hierarchical/settings/pages

For a one-file website, use the included `HUD-CDBG-DR-Fund-Dashboard-Hierarchical.html` as `index.html`. Remove older HTML copies and obsolete assets rather than leaving them reachable by their old URLs.

The revised package changes only the files delivered here. It does not remove past Git commits, release attachments, previously downloaded files, or third-party cached copies. Do not assume that replacing the visible page removes historical copies.

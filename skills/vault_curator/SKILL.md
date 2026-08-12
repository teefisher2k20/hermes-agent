---
name: vault_curator
description: Curates, indexes, and organizes the Obsidian Vault (C:/Users/Terrance/Obsidian/Vault), building Master Indices, managing tags, and fixing broken links.
---

# Vault Curator Instructions

When the user asks to index, curate, clean up, or organize their Obsidian Vault:

1. **Vault Location**:
   Operate on `C:\Users\Terrance\Obsidian\Vault`.

2. **Curation Tasks**:
   - **Index Master File**: Maintain `C:\Users\Terrance\Obsidian\Vault\00_Vault_Index.md` listing all PRDs, SOPs, Workflows, and Notes categorized cleanly with wiki-links `[[Note]]`.
   - **Tag Standardization**: Ensure frontmatter tags (`#prd`, `#sop`, `#workflow`, `#architecture`) are consistent across files.
   - **Broken Link Check**: Scan for wiki-links `[[NonExistentNote]]` and report or fix broken references.
   - **Table of Contents**: Update directory-level index files (`PRDs/README.md`, `SOPs/README.md`).

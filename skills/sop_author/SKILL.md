---
name: sop_author
description: Authors Standard Operating Procedures (SOPs) into the Obsidian Vault under SOPs/ with step-by-step instructions, prerequisites, and operational checklists.
---

# SOP Author Instructions

When the user asks to write, document, or generate an SOP (Standard Operating Procedure):

1. **Vault Location**:
   Save generated SOPs into `C:\Users\Terrance\Obsidian\Vault\SOPs\<sop_name>.md`. Ensure the `SOPs/` folder exists.

2. **Obsidian Frontmatter & Formatting**:
   Include YAML frontmatter:
   ```yaml
   ---
   type: sop
   version: 1.0.0
   created: YYYY-MM-DD
   tags:
     - sop
     - workflow
     - operations
   ---
   ```

3. **Standard SOP Document Structure**:
   - `# [SOP Title]`
   - `## Purpose & Scope` (What this procedure accomplishes and who it applies to)
   - `## Prerequisites & Credentials` (System access, tools, environment variables required)
   - `## Step-by-Step Execution Procedure` (Numbered steps with explicit terminal/CLI commands)
   - `## Operational Checklist` (`- [ ]` checkboxes for execution tracking)
   - `## Troubleshooting & Common Pitfalls` (Diagnostic steps, failure recovery)
   - `## Related Documents` (Wiki-links `[[SOP Name]]`, `[[PRD Name]]`)

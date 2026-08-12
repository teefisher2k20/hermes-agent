---
name: prd_generator
description: Generates standardized Product Requirement Documents (PRDs) into the Obsidian Vault under PRDs/ with structured sections, user stories, tech specs, and metrics.
---

# PRD Generator Instructions

When the user asks to write, draft, or generate a PRD (Product Requirement Document):

1. **Vault Location**:
   Save all generated PRDs into `C:\Users\Terrance\Obsidian\Vault\PRDs\<prd_name>.md`. Ensure the `PRDs/` folder exists.

2. **Obsidian Frontmatter & Formatting**:
   Include standard Obsidian YAML frontmatter:
   ```yaml
   ---
   type: prd
   status: draft
   created: YYYY-MM-DD
   tags:
     - prd
     - product
     - specification
   ---
   ```

3. **Standard PRD Document Structure**:
   - `# [PRD Title]`
   - `## 1. Executive Summary & Problem Statement` (Context, background, target audience)
   - `## 2. Goals & Success Metrics` (Measurable KPIs, success criteria)
   - `## 3. User Stories & Persona Requirements` (Gherkin or As a/I want/So that format)
   - `## 4. Functional Specifications & Requirements` (P0/P1/P2 feature breakdown)
   - `## 5. Technical & Architectural Design` (Data models, API contracts, sequence flows)
   - `## 6. Risks, Edge Cases & Mitigation` (Failure modes, security, performance limits)
   - `## 7. Open Questions & Next Steps`

4. **Vault Interlinking**:
   Use Obsidian wiki-links `[[Note Name]]` where relevant to link related PRDs, SOPs, or architecture notes.

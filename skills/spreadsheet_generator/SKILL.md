---
name: spreadsheet_generator
description: Generates multi-tab Excel (.xlsx) spreadsheets with styled headers, formulas, and overview/data worksheets using openpyxl.
---

# Spreadsheet Generator Instructions

When the user asks to create a spreadsheet, Excel file, financial report, or table analysis:

1. **Verify Dependency**:
   Ensure `openpyxl` is available. If missing, install via terminal:
   `pip install openpyxl`

2. **Structure Worksheets**:
   - Tab 1: **Overview / Summary** (Key metrics, total calculations using Excel formulas like `SUM`, `AVERAGE`).
   - Tab 2: **Data / Breakdown** (Structured data rows, formatted column headers).

3. **Format & Style**:
   - Header Row: Dark background fill with bold white text (`PatternFill`, `Font`).
   - Number Formatting: Currency, percentages, integers.
   - Auto-fit column widths so text is readable without truncation.

4. **Save & Open**:
   - Save to target location (`~/Desktop/<name>.xlsx` or local directory).
   - Open the spreadsheet with `os.startfile(filepath)` on Windows.
   - Confirm completion to the user.

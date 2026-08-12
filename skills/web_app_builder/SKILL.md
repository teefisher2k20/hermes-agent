---
name: web_app_builder
description: Generates full web applications (calculators, tools, dashboards) into a target developer folder and creates desktop/taskbar shortcuts.
---

# Web App Builder Instructions

When the user asks to build a web application, calculator, widget, or tool:

1. **Target Directory**:
   Save generated apps in the designated developer directory (default `~/HermesApps/<app_name>` or user-specified folder).

2. **Application Architecture**:
   - `index.html`: Modern semantic HTML structure.
   - `styles.css`: Modern styling (dark mode, glassmorphism, responsive grid, smooth CSS transitions, custom color palette).
   - `app.js`: Fully functional Vanilla JavaScript logic (no placeholder code).

3. **Shortcut Creation (Windows)**:
   To allow pinning to taskbar or launching as a desktop app:
   - Generate a small PowerShell script to create a `.url` or `.lnk` shortcut pointing to `index.html` (or via default browser).
   - Provide instructions for right-clicking the shortcut -> "Pin to taskbar".

4. **Launch Application**:
   Open the generated application in the default web browser immediately.

---
name: system_briefing
description: Generates a Jarvis-style morning system briefing including CPU, RAM, battery, disk space, local weather, and recent workspace files.
---

# System Briefing Instructions

When the user asks for a briefing, system status, "Good morning", or "Jarvis briefing":

1. **Gather System Metrics**:
   Run a quick Python command or snippet using `psutil`:
   - CPU Usage (`psutil.cpu_percent(interval=1)`)
   - RAM Usage (`psutil.virtual_memory()`)
   - Disk Space on primary drive (`psutil.disk_usage('/')` or `C:`)
   - Battery level and charging status (`psutil.sensors_battery()`)

2. **Gather Weather**:
   Use `web_search` or query Open-Meteo API for current weather report for the user's location.

3. **Gather Workspace Context**:
   Scan the workspace directory for files modified in the last 24 hours.

4. **Format Briefing**:
   Synthesize into a sleek, Jarvis-style response:
   - Greeting ("Good day/evening, sir...")
   - System Diagnostics (Battery %, CPU %, RAM %, Storage remaining)
   - Weather summary
   - Workspace summary ("I found recent work in...")
   - Offer further assistance.

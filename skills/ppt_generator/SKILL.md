---
name: ppt_generator
description: Automatically generates professional PowerPoint (.pptx) presentation decks from a topic or outline using python-pptx.
---

# PowerPoint Generator Instructions

When the user asks to generate a presentation, slide deck, or PowerPoint presentation:

1. **Verify Python Dependency**:
   Ensure `python-pptx` is available. If missing, install via terminal:
   `pip install python-pptx`

2. **Generate Presentation Script**:
   Write a temporary Python script (`scripts/gen_ppt.py` or inline) that builds the `.pptx` file:
   - Create a `Presentation()` object.
   - Slide 1: Title Slide with topic title and subtitle.
   - Slide 2..N: Content Slides (Key Points, Bullet Lists, Comparisons, Section Headers).
   - Final Slide: Summary & Conclusion slide.

3. **Styling & Aesthetics**:
   - Use clean typography and consistent color accents (dark title headers, structured text frames).
   - Set column widths and margins appropriately.

4. **Execute & Save**:
   - Save the presentation file to `~/Desktop/` or current workspace (e.g. `Presentation_<topic>.pptx`).
   - Open the file using `os.startfile(filepath)` on Windows or `open`/`xdg-open` on POSIX systems.
   - Inform the user that the presentation has been generated and opened.

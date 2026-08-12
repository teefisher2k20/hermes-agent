---
name: folder_organizer
description: Automatically categorizes messy folders (such as Downloads) into subdirectories by file type (Documents, Images, Archives, Installers, Code).
---

# Folder Organizer Instructions

When the user asks to clean up or organize a directory (e.g. Downloads folder):

1. **Target Directory Identification**:
   Default to `~/Downloads` unless specified otherwise by the user.

2. **Categorization Rules**:
   - `Documents/`: `.pdf`, `.docx`, `.doc`, `.txt`, `.xlsx`, `.pptx`, `.csv`
   - `Images/`: `.jpg`, `.jpeg`, `.png`, `.gif`, `.svg`, `.webp`
   - `Archives/`: `.zip`, `.tar.gz`, `.tar`, `.7z`, `.rar`
   - `Installers/`: `.exe`, `.msi`, `.dmg`, `.pkg`, `.iso`
   - `Code/`: `.py`, `.js`, `.ts`, `.json`, `.html`, `.css`, `.rs`, `.cpp`
   - `Media/`: `.mp4`, `.mp3`, `.wav`, `.mkv`, `.avi`

3. **Execution Safety**:
   - Create subdirectories if they do not exist.
   - Do not overwrite existing files with the same name (append timestamp or index if collision occurs).
   - Skip hidden system files (e.g. `.DS_Store`, `desktop.ini`).

4. **Summary**:
   Return a count summary of moved files per category.

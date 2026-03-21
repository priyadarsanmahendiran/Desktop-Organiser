# Desktop Organiser

An AI-powered, intelligent desktop and downloads folder organiser for macOS.

## Features

- **Automated Categorization**: Watches your `~/Desktop` and `~/Downloads` folders for new files and organizes them automatically.
- **AI File Classification**: Uses local LLMs (via Ollama and `llama3`) to intelligently categorize files based on their names (into Images, Documents, Software, Media, Chalmers, or Misc).
- **Duplicate Clean-up**: Automatically detects duplicate files (e.g., `report (1).pdf` vs `report.pdf`), prevents clutter by moving the duplicates into a `Bin` folder, and gracefully handles filename collisions.
- **macOS Notifications**: Seamlessly integrates into macOS to send native desktop notifications whenever the active background agent intercepts and bins a newly downloaded duplicate file.
- **Two-Phase Execution**:
  - **Phase 1 (Sweep)**: On startup, intelligently scans and categorizes all existing files.
  - **Phase 2 (Agent)**: Spawns a background watchdog directory observer that instantly reacts to new incoming files.

## Prerequisites

- macOS
- Python 3.x
- [Ollama](https://ollama.com/) with the `llama3` model pulled (`ollama pull llama3`)

## Installation & Setup

1. **Clone the repository** (or download the files).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the organiser**:
   ```bash
   python organise.py
   ```
   *Note: For best results, it is recommended to run this inside a virtual environment.*
4. **Run the organiser in background**:
   ```bash
   nohup python3 organise.py &
   ```
5. **Stop the organiser**:
   ```bash
   pkill -f organise.py
   ```

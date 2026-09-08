# Device Transfer & Setup Guide: Antigravity Skills Suite

This guide walks you through transferring and activating this complete Academic & Statistical Consultancy Skill Suite on another computer (Mac, Windows, or Linux).

---

## 1. Transferring the Project to the New Device

### Method A: Via Git (Recommended)
1. On your current computer, commit and push all files to your Git repository:
   ```bash
   git add .
   git commit -m "Add complete statistical-data-analyst skill, AGENTS.md, and setup guides"
   git push origin main
   ```
2. On your new computer, clone the repository:
   ```bash
   git clone <YOUR_REPOSITORY_URL> AntigravitySkills
   cd AntigravitySkills
   ```

### Method B: Via USB Flash Drive or ZIP Archive
1. Copy the entire `AntigravitySkills` folder to your USB drive or compress it as a ZIP file.
   > **Note**: Ensure that hidden directories (specifically `.agents/` and `.git/`) are included in the copy.
2. Unzip or copy the folder to your new computer (e.g., to your Desktop or Documents folder).

---

## 2. Setting Up the Environment on the New Device

### Step 1: Install Python (Version 3.10 or newer)
- **macOS**: Install via Homebrew: `brew install python` (or download from [python.org](https://www.python.org/)).
- **Windows**: Download Python from [python.org](https://www.python.org/). **Make sure to check "Add Python to PATH"** during installation.
- **Linux (Ubuntu/Debian)**: `sudo apt update && sudo apt install python3 python3-pip python3-venv`

### Step 2: Create a Virtual Environment & Install Dependencies
Open a terminal in the `AntigravitySkills` directory:

```bash
# 1. Create a virtual environment
python3 -m venv venv

# 2. Activate the virtual environment
# On macOS / Linux:
source venv/bin/activate
# On Windows (PowerShell):
# .\venv\Scripts\Activate.ps1
# On Windows (CMD):
# .\venv\Scripts\activate.bat

# 3. Upgrade pip & install all required packages
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Installing Persian Fonts (Essential for Microsoft Word)

The document generator formats Iranian university theses using standard Persian academic typography. For Microsoft Word to display the tables and text properly on the new device, install the **B Series Persian Fonts**:

1. Download or copy the standard font package:
   - **B Nazanin** (Normal & Bold)
   - **B Titr** (Bold)
   - **B Lotus** (Normal & Bold)
2. Install them on the new device:
   - **macOS**: Double-click each `.ttf` font file and click **Install Font** (in Font Book).
   - **Windows**: Right-click the `.ttf` font files and select **Install for all users**.
   - **Linux**: Copy `.ttf` files to `~/.local/share/fonts/` and run `fc-cache -fv`.

---

## 4. Activating in Google Antigravity

When you open this folder in **Google Antigravity**:
1. Open Antigravity and select **Open Workspace** $\rightarrow$ select the `AntigravitySkills` folder.
2. **Automatic Skill Discovery**:
   - Antigravity automatically detects the workspace customization folder `.agents/skills/`.
   - All 4 skills (`persian-academic-translation`, `academic-reference-extractor`, `persian-thesis-builder`, and `statistical-data-analyst`) will immediately appear in the agent's available skills list.
3. **Automatic Rule Injection**:
   - Antigravity automatically reads `AGENTS.md` at the root of the workspace. Any agent turn will adhere to the APA 7th Edition standards, zero-hallucination rules, and typography guidelines.

---

## 5. Verification Test (Confirming Everything Works)

To verify that the Python calculation engine and Word generator work smoothly on the new device, run this quick test in your terminal:

```bash
# 1. Test calculation engine on sample data
python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py \
  --data ".agents/skills/statistical-data-analyst/scripts/psychology_stats.py" --help

# 2. Test Word document generator
python3 .agents/skills/statistical-data-analyst/scripts/generate_apa_docx.py --help
```

If both commands display their help menus with no `ImportError`, your new device is **100% configured and ready** to process student datasets and write theses!

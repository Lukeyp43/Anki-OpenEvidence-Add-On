# How to Package and Distribute This Addon

This guide explains how to create a distributable `.ankiaddon` file that your friends can easily install.

## Quick Start (Mac/Linux)

1. Open Terminal
2. Navigate to the addon directory:
   ```bash
   cd "/Users/lukepettit/Library/Application Support/Anki2/addons21/openevidence_panel"
   ```
3. Run the packaging script:
   ```bash
   ./package_addon.sh
   ```
4. The file `openevidence_panel.ankiaddon` will be created in the parent directory
5. Share this file with your friends!

## Manual Method (All Platforms)

### Step 1: Clean the directory

First, delete the `__pycache__` directory if it exists:
```bash
rm -rf __pycache__
```

### Step 2: Create the package

**On Mac/Linux:**
```bash
cd "/Users/lukepettit/Library/Application Support/Anki2/addons21/openevidence_panel"
zip -r ../openevidence_panel.ankiaddon __init__.py manifest.json config.json README.md
```

**On Windows (Command Prompt):**
```cmd
cd "%APPDATA%\Anki2\addons21\openevidence_panel"
powershell Compress-Archive -Path __init__.py,manifest.json,config.json,README.md -DestinationPath ..\openevidence_panel.zip
ren ..\openevidence_panel.zip openevidence_panel.ankiaddon
```

## Distribution Options

### Option 1: Direct Sharing
- Email the `.ankiaddon` file to your friends
- Share via cloud storage (Google Drive, Dropbox, etc.)
- Share via messaging apps

### Option 2: AnkiWeb (Public Distribution)
1. Go to https://ankiweb.net/shared/addons/
2. Click "Upload" (requires AnkiWeb account)
3. Upload your `openevidence_panel.ankiaddon` file
4. Add a description and screenshots
5. Your addon will get a unique ID that anyone can use to install

### Option 3: GitHub/GitLab
1. Create a repository on GitHub/GitLab
2. Upload the addon files
3. Create a release with the `.ankiaddon` file attached
4. Share the repository link

## Installation Instructions for Your Friends

Send these instructions along with the `.ankiaddon` file:

1. **Download** the `openevidence_panel.ankiaddon` file
2. **Double-click** the file (Anki should open automatically)
   - OR open Anki → **Tools** → **Add-ons** → **Install from file...**
3. **Restart** Anki
4. Look for the book icon (📖) in the top toolbar next to Sync
5. Click the book icon to open OpenEvidence!

## Updating the Addon

When you make changes to the addon:
1. Update the `mod` timestamp in `manifest.json` (use current Unix timestamp)
2. Run the packaging script again
3. Distribute the new `.ankiaddon` file

To get current Unix timestamp:
```bash
date +%s
```

## Troubleshooting

**Problem: "Add-on corrupt" error**
- Make sure `__pycache__` directories are deleted
- Ensure the ZIP doesn't contain the parent folder

**Problem: Icon not showing**
- Tell users to restart Anki completely
- Check that they're using Anki 2.1.45 or later

**Problem: Panel not loading**
- Check internet connection (OpenEvidence requires internet)
- Try disabling other addons that might conflict

## File Structure

Your addon should contain these files:
```
openevidence_panel/
├── __init__.py          (main addon code)
├── manifest.json        (addon metadata)
├── config.json          (default configuration)
└── README.md           (user documentation)
```

The `.ankiaddon` file is simply a ZIP file containing these files (without the parent folder).


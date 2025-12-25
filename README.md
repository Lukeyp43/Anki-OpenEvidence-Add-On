# OpenEvidence Panel for Anki

A modern Anki addon that integrates OpenEvidence directly into your Anki interface as a side panel.

## Features

- 📚 **Clean Toolbar Icon**: Open book icon in the top toolbar next to Sync
- 🎨 **Integrated Side Panel**: OpenEvidence opens as a docked panel on the right side of Anki
- 🎯 **Modern UI**: Minimalistic design with smooth hover effects
- 🔄 **Flexible Layout**: Dock, undock, or resize the panel as needed
- ⚡ **Quick Access**: Toggle the panel on/off with a single click
- ⌨️ **Smart Templates**: 3 preset keyboard shortcuts to auto-fill OpenEvidence with card content
- ⚙️ **Customizable Settings**: Edit keyboard shortcuts and create custom templates via the settings panel
- ✨ **Cursor-Style Highlight Actions**: Select text on flashcards to show a floating action bar with quick actions

## Installation

### Method 1: Install from .ankiaddon file

1. Download the `openevidence_ai.ankiaddon` file
2. Double-click the file, or open Anki and go to **Tools → Add-ons → Install from file...**
3. Select the downloaded `.ankiaddon` file
4. Restart Anki

### Method 2: Manual Installation

1. Download and extract the addon files
2. Copy the `openevidence_ai` folder to your Anki addons directory:
   - **Windows**: `%APPDATA%\Anki2\addons21\`
   - **Mac**: `~/Library/Application Support/Anki2/addons21/`
   - **Linux**: `~/.local/share/Anki2/addons21/`
3. Restart Anki

## Usage

1. After installation, you'll see a book icon (📖) in the top toolbar next to Sync
2. Click the book icon to open/close the OpenEvidence panel
3. The panel will appear docked on the right side of Anki
4. You can:
   - Resize the panel by dragging the separator
   - Undock the panel by clicking the pop-out button
   - Close the panel by clicking the X button or the toolbar icon

### Smart Templates with Keyboard Shortcuts ⚡

The addon comes with **3 preset keyboard shortcuts** that let you instantly fill the OpenEvidence search box with card content in different formats. All shortcuts work while focused on the OpenEvidence search box.

**Preset 1: Standard Explain** - `Ctrl+Shift+S` (or `Cmd+Shift+S` on Mac)
- **Front side**: Sends your front with a polite prompt
  ```
  Can you explain this to me:

  [Your front]
  ```
- **Back side**: Sends both front and back
  ```
  Can you explain this to me:

  Question:
  [Your front]

  Answer:
  [Your back]
  ```

**Preset 2: Front/Back** - `Ctrl+Shift+Q` (or `Cmd+Shift+Q` on Mac)
- Sends only the front of your card on both sides
- Perfect for when you only want to search the front

**Preset 3: Back Only** - `Ctrl+Shift+A` (or `Cmd+Shift+A` on Mac)
- Front side: Sends nothing (empty)
- Back side: Sends only the back of your card
- Useful when you want to research just the back content

**Customization:**
Click the **Settings** button (gear icon) in the panel's title bar to:
- Edit existing keyboard shortcuts
- Modify templates for each preset
- Create your own custom templates with `{front}` and `{back}` placeholders

### Cursor-Style Highlight Actions ✨

When reviewing flashcards, you can now **highlight any text** on the card to show a floating action bar with quick actions. This feature works seamlessly while studying.

**How to use:**
1. **Select text** on any flashcard by clicking and dragging
2. A floating action bar appears above your selection with two options:
   - **Add to Chat**: Instantly populates the OpenEvidence search box with your selected text
   - **Ask Question**: Opens an input field where you can type a question about the selected text

**Add to Chat:**
- Click "Add to Chat" to send the selected text directly to OpenEvidence
- The panel opens automatically (if closed) and the text appears in the search box
- You can then edit the text or hit Enter to search

**Ask Question:**
- Click "Ask Question" to open an input field
- Type your question about the selected text
- Press Enter or click the arrow button to submit
- Your question and the selected text (as context) are sent to OpenEvidence and auto-submitted

**Example workflow:**
1. You're reviewing a card about "myocardial infarction"
2. Highlight the term "ST elevation"
3. Click "Ask Question"
4. Type "What causes this finding?"
5. Press Enter
6. OpenEvidence receives: "What causes this finding?\n\nContext:\nST elevation"

This feature is perfect for quickly researching unfamiliar terms or concepts without leaving your study flow!

## Requirements

- Anki 2.1.45 or later
- Internet connection (to access OpenEvidence.com)

## Credits

Created for medical students and professionals who want quick access to OpenEvidence while studying with Anki.

## License

Free to use and distribute.

## Support

For issues or questions, please contact the addon developer.

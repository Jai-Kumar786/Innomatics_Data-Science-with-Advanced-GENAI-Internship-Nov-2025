# 🔍 Regex Tester - Flask Web Application

A full-featured regex testing web application inspired by regex101.com, built with Flask and vanilla JavaScript. Test your regular expressions in real-time with detailed match information.

## Features

✅ **Core Functionality**
- Input regex patterns and test strings
- Real-time regex matching and validation
- Display all matches with detailed information
- Support for capture groups and named groups

✅ **Regex Flags**
- Case Insensitive (i)
- Multiline (m)
- Dotall (s)
- Verbose (x)

✅ **Match Information**
- Match position (start and end indices)
- Match length
- Capture groups display
- Named groups display
- Error handling for invalid regex patterns

✅ **User Interface**
- Modern, responsive design
- Two-column layout for pattern and test string
- Real-time error messages
- Loading indicators
- Clean results display

## Project Structure

```
regex-tester/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── templates/
    └── index.html        # Frontend HTML/CSS/JavaScript
```

## Installation & Setup

### Step 1: Clone or Create Project Directory

```bash
mkdir regex-tester
cd regex-tester
```

### Step 2: Create Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Create Templates Directory

```bash
mkdir templates
```

### Step 5: File Structure Setup

Place the files in the following structure:

```
regex-tester/
├── app.py
├── requirements.txt
├── README.md
└── templates/
    └── index.html
```

### Step 6: Run the Application

```bash
python app.py
```

You should see output like:
```
* Running on http://127.0.0.1:5000
* Press CTRL+C to quit
```

### Step 7: Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

## How to Use

### Basic Usage

1. **Enter a Regular Expression Pattern**
   - Example: `\w+@[\w.-]+\.\w+$` (for email matching)
   - Example: `\d{3}-\d{3}-\d{4}` (for phone numbers)

2. **Enter a Test String**
   - Paste the text you want to test the regex against
   - Can be single line or multiline text

3. **Configure Flags (Optional)**
   - **i** (Case Insensitive): Ignore case when matching
   - **m** (Multiline): Treat `^` and `$` as line boundaries
   - **s** (Dotall): Make `.` match newline characters
   - **x** (Verbose): Allow regex with comments and whitespace

4. **Click Submit**
   - Application will process the regex and find all matches
   - Results display with detailed match information

### Understanding Results

For each match, you'll see:
- **Match Text**: The actual matched string
- **Position**: Start and end character indices
- **Length**: Number of characters matched
- **Capture Groups**: Any groups captured by the regex
- **Named Groups**: If you used named groups in your pattern

## Examples

### Email Validation
- **Pattern:** `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`
- **Test String:** `Contact us at support@example.com or info@test.org`
- **Result:** 2 matches found

### Phone Number Extraction
- **Pattern:** `\d{3}-\d{3}-\d{4}`
- **Test String:** `Call 123-456-7890 or 987-654-3210`
- **Result:** 2 matches found

### URL Extraction
- **Pattern:** `https?://[^\s]+`
- **Test String:** `Visit https://example.com or https://test.org`
- **Result:** 2 matches found

### Word Extraction
- **Pattern:** `\w+`
- **Test String:** `Hello World!`
- **Result:** 2 matches: "Hello" and "World"

## API Endpoints

### POST /test-regex

**Request Body:**
```json
{
    "pattern": "\\d+",
    "test_string": "There are 123 apples and 456 oranges",
    "flags": "i"
}
```

**Response (Success):**
```json
{
    "success": true,
    "total_matches": 2,
    "matches": [
        {
            "full_match": "123",
            "start": 10,
            "end": 13,
            "groups": [],
            "named_groups": {}
        },
        {
            "full_match": "456",
            "start": 29,
            "end": 32,
            "groups": [],
            "named_groups": {}
        }
    ],
    "pattern": "\\d+",
    "flags": "i"
}
```

**Response (Error):**
```json
{
    "success": false,
    "error": "Invalid regex: missing )"
}
```

## Keyboard Shortcuts

- **Enter** in Pattern field: Submit regex test
- **Ctrl+Enter** in Test String field: Submit regex test
- **Clear button**: Reset all fields and results

## Python Regex Flags Supported

| Flag | Meaning | Use Case |
|------|---------|----------|
| `i` | IGNORECASE | Case-insensitive matching |
| `m` | MULTILINE | `^` and `$` match line boundaries |
| `s` | DOTALL | `.` matches including newlines |
| `x` | VERBOSE | Allows comments and whitespace in pattern |


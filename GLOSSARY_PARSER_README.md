# Glossary Parser for Quizlet Flashcards

This tool parses HTML pages containing glossary entries and formats them for direct import into Quizlet.

## Requirements

- **Node.js** (for `glossary-parser.js`) OR
- **Python 3** (for `glossary-parser.py`)

## Usage

### Method 1: Using Python (Recommended)

```bash
python3 glossary-parser.py "glossary items in page html.txt"
```

### Method 2: Using Node.js

```bash
node glossary-parser.js "glossary items in page html.txt"
```

## Input

Place your HTML file containing glossary entries in the same directory as the parser script. The default filename is `glossary items in page html.txt`, but you can specify a different file as a command-line argument.

## Output

The parser will create a file named `quizlet-flashcards.txt` with entries formatted as:

```
<Concept Name>, <Type>, <Pronunciation> ; <Definition>, <Example Sentence>, <Slovenian Translation>
```

### Example Output

```
Ameliorate, Verb, UK: /əˈmiːliəreɪt/ ; To make something bad or unsatisfactory better, The new measures are designed to ameliorate social problems, Novi ukrepi so namenjeni izboljšanju družbenih problemov
Curiosity, Noun, UK: /ˌkjʊəriˈɒsəti/, US: /ˌkjʊriˈɑːsəti/ ; An eager wish to know or learn about something, Her curiosity about the ancient ruins led her to study archaeology, Njena radovednost o starih ruševinah jo je pripeljala do študija arheologije
```

## Importing to Quizlet

1. Run the parser to generate `quizlet-flashcards.txt`
2. Go to Quizlet and create a new study set
3. Click "Import" or "Import from Word, Excel, Google Docs, etc."
4. Set the delimiter between term and definition to: **semicolon (;)**
5. Set the delimiter between rows to: **new line**
6. Copy the contents of `quizlet-flashcards.txt` and paste into Quizlet
7. Click "Import" to create your flashcards

## Features

- Extracts all required fields:
  - Concept name
  - Word type (noun, verb, adjective, idiom, etc.)
  - Phonetic transcription with UK/US labels
  - Definition
  - Example sentence
  - Slovenian translation of example
- Handles various HTML structures
- Removes duplicate entries
- Cleans and normalizes text
- Properly handles HTML entities

## Notes

- The parser automatically detects and labels UK and US pronunciations
- If pronunciation variants exist for both UK and US, both are included
- All entries must have all 6 fields to be included in the output
- Duplicate entries are automatically removed

## Troubleshooting

If no entries are found:
1. Check that the HTML file exists in the correct location
2. Verify the HTML structure matches expected patterns
3. The parser may need to be adjusted for your specific HTML format

Once the HTML file is available, the parser can be refined to match the exact structure of your glossary entries.

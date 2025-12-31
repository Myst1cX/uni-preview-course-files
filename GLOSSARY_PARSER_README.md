# Glossary Parser for Quizlet Flashcards

This tool parses HTML pages containing glossary entries and formats them for direct import into Quizlet.

## Requirements

- **Python 3** (recommended) - for `glossary-parser.py`

## Usage

```bash
python3 glossary-parser.py "glossary items in page html.txt"
```

Or if the file is in the current directory with the default name:

```bash
python3 glossary-parser.py
```

## Input

Place your HTML file containing glossary entries in the same directory as the parser script. The default filename is `glossary items in page html.txt`, but you can specify a different file as a command-line argument.

## Output

The parser will create a file named `quizlet-flashcards.txt` with entries formatted as:

```
<Concept Name>, <Type>, <Pronunciation> ; <Definition>, <Example Sentence>, <Slovenian Translation>
```

## Example Output Format

```
(at) full throttle, Idiom, /(æt) fʊl ˈθrɒtəl/ ; moving or progressing as fast as possible, She was roaring up the freeway at full throttle., S polnim plinom je drvela po avtocesti.
audit, Noun, UK: /ˈɔː.dɪt/, US: /ˈɑː.dɪt/ ; an official examination of the accounts of a business, An internal audit uncovered £11.5 million in payments to dead beneficiaries., Notranja revizija je razkrila 11,5 milijona funtov izplačil umrlim upravičencem.
average Joe, Noun, Idiom, /ˈævᵊrɪʤ ʤəʊ/ ; an ordinary, typical person, He says it takes him longer than the average Joe to get ready for work., Pravi, da se za delo pripravlja dlje kot kot povprečen človek.
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

- Extracts all required fields from HTML glossary entries:
  - Concept name
  - Word type (noun, verb, adjective, idiom, etc. - supports multiple types)
  - Phonetic transcription with UK/US labels where applicable
  - Definition (from `<strong>` tags or paragraph content)
  - Example sentence (from `<em>` tags)
  - Slovenian translation of example (from `<em>` tags)
- Handles various HTML structures and formatting inconsistencies
- Removes duplicate entries automatically
- Cleans and normalizes text (HTML entities, whitespace)
- Outputs clean, ready-to-import format

## Notes

- The parser automatically detects and labels UK and US pronunciations
- If pronunciation variants exist for both UK and US, both are included
- All entries must have all 6 fields to be included in the output
- Duplicate entries are automatically removed

## Troubleshooting

### If no entries or few entries are found:
1. Check that the HTML file exists in the correct location
2. Verify the HTML contains glossary entries in expected format
3. Check the console output for "Incomplete entry" messages - these show which fields are missing

### Common issues:
- **Missing examples/translations**: Some entries in the HTML might not have example sentences or translations formatted correctly (missing `<em>` tags)
- **Missing pronunciation**: Some entries might not have pronunciation in the expected `/.../ ` format
- **Definition not found**: Definition should be in `<strong>` tags or be a longer paragraph

The parser only includes entries that have ALL 6 required fields populated.

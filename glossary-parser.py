#!/usr/bin/env python3
"""
Glossary to Quizlet Flashcard Parser

Parses HTML containing glossary entries and formats them for Quizlet import.
Output format: <Name>, <Type>, <Pronunciation> ; <Definition>, <Example>, <Translation>
"""

import re
import sys
from pathlib import Path
from html.parser import HTMLParser
from html import unescape


class GlossaryEntry:
    """Represents a single glossary entry"""
    def __init__(self):
        self.name = ""
        self.type = ""
        self.pronunciation = ""
        self.definition = ""
        self.example = ""
        self.translation = ""
    
    def is_complete(self):
        """Check if entry has all required fields"""
        return all([self.name, self.type, self.pronunciation, 
                   self.definition, self.example, self.translation])
    
    def format_for_quizlet(self):
        """Format entry for Quizlet import"""
        front = f"{self.name}, {self.type}, {self.pronunciation}"
        back = f"{self.definition}, {self.example}, {self.translation}"
        return f"{front} ; {back}"


def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    # Unescape HTML entities
    text = unescape(text)
    # Replace multiple spaces/newlines with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_pronunciation(text):
    """Extract phonetic pronunciation from text"""
    # Look for IPA notation in slashes /.../ or brackets [...]
    pron_pattern = r'[/\[]([ˈˌæɪəʊʌɛɜːɔɑʃʒθðŋɹɾʔ\w\s.:]+)[/\]]'
    matches = re.findall(pron_pattern, text)
    
    if not matches:
        return ""
    
    pronunciation = ""
    
    # Check for UK/US labels
    uk_pattern = r'UK[:\s]*[/\[]([ˈˌæɪəʊʌɛɜːɔɑʃʒθðŋɹɾʔ\w\s.:]+)[/\]]'
    us_pattern = r'US[:\s]*[/\[]([ˈˌæɪəʊʌɛɜːɔɑʃʒθðŋɹɾʔ\w\s.:]+)[/\]]'
    
    uk_match = re.search(uk_pattern, text)
    us_match = re.search(us_pattern, text)
    
    if uk_match and us_match:
        pronunciation = f"UK: /{uk_match.group(1)}/, US: /{us_match.group(1)}/"
    elif uk_match:
        pronunciation = f"UK: /{uk_match.group(1)}/"
    elif us_match:
        pronunciation = f"US: /{us_match.group(1)}/"
    else:
        # No explicit label, use first match
        pronunciation = f"/{matches[0]}/"
        # Try to infer UK/US from context
        if 'UK' in text or 'British' in text:
            pronunciation = "UK: " + pronunciation
        elif 'US' in text or 'American' in text:
            pronunciation = "US: " + pronunciation
    
    return pronunciation


def extract_type(text):
    """Extract word type (noun, verb, etc.) from text"""
    type_pattern = r'\b(noun|verb|adjective|adverb|idiom|phrase|pronoun|preposition|conjunction|interjection)\b'
    match = re.search(type_pattern, text, re.IGNORECASE)
    
    if match:
        word_type = match.group(1)
        return word_type.capitalize()
    
    return ""


def parse_html_simple(html_content):
    """
    Simple parser that looks for common patterns in glossary HTML.
    This is a flexible approach that will be refined once we see the actual structure.
    """
    entries = []
    
    # Remove script and style tags
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Try different patterns for glossary entries
    
    # Pattern 1: Entries in divs/sections with class containing 'entry', 'term', 'glossary', 'item'
    pattern1 = r'<(?:div|article|section)[^>]*class="[^"]*(?:entry|term|glossary|item)[^"]*"[^>]*>(.*?)</(?:div|article|section)>'
    matches = re.findall(pattern1, html_content, re.DOTALL | re.IGNORECASE)
    
    # Pattern 2: Definition lists (dt/dd pairs)
    pattern2 = r'<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>'
    dt_dd_matches = re.findall(pattern2, html_content, re.DOTALL | re.IGNORECASE)
    
    # Pattern 3: List items with glossary-related classes
    pattern3 = r'<li[^>]*class="[^"]*(?:entry|term|glossary)[^"]*"[^>]*>(.*?)</li>'
    li_matches = re.findall(pattern3, html_content, re.DOTALL | re.IGNORECASE)
    
    # Combine all matches
    all_matches = matches + [f"{dt}{dd}" for dt, dd in dt_dd_matches] + li_matches
    
    for match in all_matches:
        entry = parse_entry_content(match)
        if entry and entry.is_complete():
            entries.append(entry)
    
    return entries


def parse_entry_content(content):
    """Parse content of a single entry"""
    entry = GlossaryEntry()
    
    # Strip HTML tags for analysis
    text = re.sub(r'<[^>]+>', ' ', content)
    text = clean_text(text)
    
    # Extract fields
    entry.pronunciation = extract_pronunciation(content)
    entry.type = extract_type(content)
    
    # For now, return None as we need to see actual structure
    # This will be completed once we have the actual HTML file
    return None


def parse_glossary_file(filename):
    """Main parsing function"""
    filepath = Path(filename)
    
    if not filepath.exists():
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    
    print(f"Reading file: {filename}")
    html_content = filepath.read_text(encoding='utf-8')
    
    print("Parsing glossary entries...")
    entries = parse_html_simple(html_content)
    
    print(f"Found {len(entries)} entries")
    
    return entries


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "glossary items in page html.txt"
    
    entries = parse_glossary_file(input_file)
    
    # Format for Quizlet
    quizlet_lines = [entry.format_for_quizlet() for entry in entries]
    
    # Remove duplicates while preserving order
    unique_lines = list(dict.fromkeys(quizlet_lines))
    
    print(f"Unique entries: {len(unique_lines)}")
    
    # Write to output file
    output_file = "quizlet-flashcards.txt"
    Path(output_file).write_text('\n'.join(unique_lines), encoding='utf-8')
    
    print(f"\nOutput written to: {output_file}")
    
    # Show first few entries
    print("\nFirst 5 entries:")
    for i, line in enumerate(unique_lines[:5], 1):
        print(f"{i}. {line}")


if __name__ == "__main__":
    main()

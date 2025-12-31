#!/usr/bin/env python3
"""
Glossary to Quizlet Flashcard Parser - Final Version

Parses HTML glossary entries and formats them for Quizlet import.
Output: <Name>, <Type>, <Pronunciation> ; <Definition>, <Example>, <Translation>
"""

import re
from pathlib import Path
from html import unescape


class GlossaryEntry:
    def __init__(self):
        self.name = ""
        self.type = ""
        self.pronunciation = ""
        self.definition = ""
        self.example = ""
        self.translation = ""
    
    def is_complete(self):
        return all([self.name, self.type, self.pronunciation, 
                   self.definition, self.example, self.translation])
    
    def format_for_quizlet(self):
        front = f"{self.name}, {self.type}, {self.pronunciation}"
        back = f"{self.definition}, {self.example}, {self.translation}"
        return f"{front} ; {back}"


def clean_text(text):
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    text = re.sub(r'^E\.g\.\s+', '', text, flags=re.IGNORECASE)
    return text


def strip_html(html):
    text = re.sub(r'<[^>]+>', '', html)
    return clean_text(text)


def extract_text_from_paragraph(p_content):
    """Extract clean text from a paragraph, stripping all HTML"""
    return strip_html(p_content)


def parse_glossary_entries(html_content):
    entries = []
    
    # Match glossary entries
    pattern = r'<div class="concept"><h4>(.*?)</h4>.*?<div class="no-overflow">(.*?)</div></td>'
    matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    print(f"Found {len(matches)} entries")
    
    for concept_name, content in matches:
        concept_name = strip_html(concept_name)
        entry = parse_entry(concept_name, content)
        
        if entry and entry.is_complete():
            entries.append(entry)
    
    return entries


def extract_type(text):
    """Extract word type"""
    pattern = r'\b(noun|verb|adjective|adverb|idiom|phrase|pronoun|preposition|conjunction|interjection)(?:\s*\([^)]*\))?(?:\s*,\s*(noun|verb|adjective|adverb|idiom|phrase|pronoun|preposition|conjunction|interjection))?'
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        types = [t for t in match.groups() if t]
        return ', '.join([t.capitalize() for t in types])
    return ""


def extract_pronunciation(paragraphs_raw):
    """Extract pronunciation - look in raw paragraph content"""
    for p in paragraphs_raw:
        # Clean the paragraph text
        text = extract_text_from_paragraph(p)
        
        # Check if this paragraph contains pronunciation
        # UK/US format
        uk_match = re.search(r'UK[:\s]*[/\[]([^/\]]+)[/\]]', text, re.IGNORECASE)
        us_match = re.search(r'US[:\s]*[/\[]([^/\]]+)[/\]]', text, re.IGNORECASE)
        
        if uk_match and us_match:
            return f"UK: /{uk_match.group(1).strip()}/, US: /{us_match.group(1).strip()}/"
        elif uk_match:
            return f"UK: /{uk_match.group(1).strip()}/"
        elif us_match:
            return f"US: /{us_match.group(1).strip()}/"
        
        # Simple format: just /pronunciation/
        # Must be a short line, mostly just the pronunciation
        if text.startswith('/') and text.endswith('/') and len(text) < 80:
            pron = text.strip('/').strip()
            return f"/{pron}/"
        
        # Format like: /ænd/ /swɪʧ/ or /(æt) fʊl ˈθrɒtəl/
        if '/' in text and len(text) < 80:
            # Extract all content between slashes
            pron_parts = re.findall(r'/([^/]+)/', text)
            if pron_parts:
                # Join multiple parts if they exist
                if len(pron_parts) > 1 and all(len(p.strip()) < 20 for p in pron_parts):
                    # Multiple short phonetic segments like /beɪt/ /ænd/ /swɪʧ/
                    pron = ' '.join(p.strip() for p in pron_parts)
                else:
                    # Single pronunciation
                    pron = pron_parts[0].strip()
                
                # Skip if it looks like a URL
                if 'http' not in pron and len(pron) > 2:
                    return f"/{pron}/"
    
    return ""


def extract_definition(paragraphs_raw):
    """Extract definition - usually in <strong> tags"""
    for p in paragraphs_raw:
        strong_match = re.search(r'<strong>(.*?)</strong>', p, re.DOTALL)
        if strong_match:
            definition = strip_html(strong_match.group(1))
            definition = definition.rstrip(':. ').strip()
            if len(definition) > 10:
                return definition
    
    # Fallback: find longest non-meta paragraph
    candidates = []
    for p in paragraphs_raw:
        text = extract_text_from_paragraph(p)
        # Skip short lines, pronunciation, type declarations, sources
        if len(text) > 20 and not text.startswith('From:') and 'dictionary.cambridge' not in text:
            if not extract_type(text) and not ('/' in text and len(text) < 80):
                candidates.append(text)
    
    if candidates:
        # Return longest one (likely the definition)
        return max(candidates, key=len)
    
    return ""


def extract_examples(paragraphs_raw):
    """Extract example sentences (English and Slovenian)"""
    examples = []
    
    for p in paragraphs_raw:
        # Examples are in <em> or <i> tags
        em_matches = re.findall(r'<(?:em|i)[^>]*>(.*?)</(?:em|i)>', p, re.DOTALL)
        for em in em_matches:
            text = strip_html(em)
            if text and len(text) > 5:
                examples.append(text)
    
    return examples


def parse_entry(concept_name, content):
    """Parse a single entry"""
    entry = GlossaryEntry()
    entry.name = concept_name
    
    # Extract paragraphs (keep raw HTML for some extractions)
    paragraphs_raw = re.findall(r'<p[^>]*>(.*?)</p>', content, re.DOTALL | re.IGNORECASE)
    
    if len(paragraphs_raw) < 2:
        return None
    
    # Extract type from first paragraph
    first_para_text = extract_text_from_paragraph(paragraphs_raw[0])
    entry.type = extract_type(first_para_text)
    
    # Extract pronunciation
    entry.pronunciation = extract_pronunciation(paragraphs_raw)
    
    # Extract definition
    entry.definition = extract_definition(paragraphs_raw)
    
    # Extract examples
    examples = extract_examples(paragraphs_raw)
    
    if len(examples) >= 2:
        entry.example = examples[0]
        entry.translation = examples[1]
    
    return entry


def main():
    import sys
    
    input_file = sys.argv[1] if len(sys.argv) > 1 else "glossary items in page html.txt"
    
    filepath = Path(input_file)
    if not filepath.exists():
        print(f"❌ Error: File '{input_file}' not found")
        sys.exit(1)
    
    print(f"📖 Reading: {input_file}")
    html = filepath.read_text(encoding='utf-8')
    
    print("🔍 Parsing entries...")
    entries = parse_glossary_entries(html)
    
    print(f"✅ Complete entries: {len(entries)}")
    
    # Format for Quizlet
    lines = [e.format_for_quizlet() for e in entries]
    unique_lines = list(dict.fromkeys(lines))
    
    # Save output
    output_file = "quizlet-flashcards.txt"
    Path(output_file).write_text('\n'.join(unique_lines), encoding='utf-8')
    
    print(f"\n💾 Saved {len(unique_lines)} flashcards to: {output_file}")
    
    # Show samples
    print("\n🎴 Sample flashcards:\n")
    for i, line in enumerate(unique_lines[:3], 1):
        if ' ; ' in line:
            front, back = line.split(' ; ', 1)
            print(f"{i}. Front: {front}")
            print(f"   Back:  {back[:80]}{'...' if len(back) > 80 else ''}\n")
    
    print("🎯 Import to Quizlet:")
    print("   1. Copy quizlet-flashcards.txt content")
    print("   2. In Quizlet: Import → Set delimiter to semicolon (;)")
    print("   3. Paste and import!")


if __name__ == "__main__":
    main()

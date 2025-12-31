#!/usr/bin/env node

/**
 * Glossary to Quizlet Flashcard Parser
 * 
 * Parses HTML containing glossary entries and formats them for Quizlet import.
 * Output format: <Name>, <Type>, <Pronunciation> ; <Definition>, <Example>, <Translation>
 */

const fs = require('fs');
const path = require('path');

// Read HTML file
function readHTMLFile(filename) {
    try {
        const filepath = path.join(__dirname, filename);
        return fs.readFileSync(filepath, 'utf-8');
    } catch (error) {
        console.error(`Error reading file: ${error.message}`);
        process.exit(1);
    }
}

// Helper function to clean text
function cleanText(text) {
    if (!text) return '';
    return text
        .replace(/\s+/g, ' ')  // Replace multiple spaces with single space
        .replace(/\n/g, ' ')    // Replace newlines with space
        .trim();
}

// Extract entries from HTML
function parseGlossaryEntries(html) {
    const entries = [];
    
    // Remove script and style tags
    html = html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '');
    html = html.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');
    
    // Pattern 1: Look for common glossary entry structures
    // This will need to be adjusted based on actual HTML structure
    
    // Try to find entries wrapped in common containers
    const patterns = [
        // Pattern for entries in div/article/section with class containing 'entry', 'term', 'glossary', 'item'
        /<(?:div|article|section)[^>]*class="[^"]*(?:entry|term|glossary|item)[^"]*"[^>]*>([\s\S]*?)<\/(?:div|article|section)>/gi,
        // Pattern for dt/dd pairs (definition lists)
        /<dt[^>]*>([\s\S]*?)<\/dt>\s*<dd[^>]*>([\s\S]*?)<\/dd>/gi,
        // Pattern for entries in list items
        /<li[^>]*class="[^"]*(?:entry|term|glossary)[^"]*"[^>]*>([\s\S]*?)<\/li>/gi,
    ];
    
    // Since we don't know the exact structure yet, let's create a flexible parser
    // that looks for key indicators in the text
    
    return entries;
}

// Extract specific fields from an entry
function extractFields(entryHTML) {
    const entry = {
        name: '',
        type: '',
        pronunciation: '',
        definition: '',
        example: '',
        translation: ''
    };
    
    // Remove HTML tags for text extraction
    const stripHTML = (html) => {
        return html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    };
    
    // Extract pronunciation (look for IPA notation in slashes or brackets)
    const pronMatch = entryHTML.match(/[\/\[]([\w\s:ˈˌæɪəʊʌɛɜːɔɑʃʒθðŋ.]+)[\/\]]/);
    if (pronMatch) {
        entry.pronunciation = pronMatch[0];
        
        // Check for UK/US labels
        if (entryHTML.includes('UK') || entryHTML.includes('British')) {
            entry.pronunciation = 'UK: ' + entry.pronunciation;
        }
        if (entryHTML.includes('US') || entryHTML.includes('American')) {
            if (entry.pronunciation.includes('UK:')) {
                // Handle both UK and US pronunciations
                const usPronMatch = entryHTML.match(/US[:\s]*[\/\[]([\w\s:ˈˌæɪəʊʌɛɜːɔɑʃʒθðŋ.]+)[\/\]]/);
                if (usPronMatch) {
                    entry.pronunciation += ', US: ' + usPronMatch[1];
                }
            } else {
                entry.pronunciation = 'US: ' + entry.pronunciation;
            }
        }
    }
    
    // Extract type (noun, verb, adjective, idiom, etc.)
    const typePattern = /\b(noun|verb|adjective|adverb|idiom|phrase|pronoun|preposition|conjunction|interjection)\b/i;
    const typeMatch = entryHTML.match(typePattern);
    if (typeMatch) {
        entry.type = typeMatch[1].charAt(0).toUpperCase() + typeMatch[1].slice(1).toLowerCase();
    }
    
    return entry;
}

// Format entry for Quizlet
function formatForQuizlet(entry) {
    const front = `${entry.name}, ${entry.type}, ${entry.pronunciation}`;
    const back = `${entry.definition}, ${entry.example}, ${entry.translation}`;
    return `${front} ; ${back}`;
}

// Main function
function main() {
    const inputFile = process.argv[2] || 'glossary items in page html.txt';
    
    console.log(`Reading file: ${inputFile}`);
    const html = readHTMLFile(inputFile);
    
    console.log('Parsing glossary entries...');
    const entries = parseGlossaryEntries(html);
    
    console.log(`Found ${entries.length} entries`);
    
    // Format for Quizlet
    const quizletLines = entries.map(entry => formatForQuizlet(entry));
    
    // Remove duplicates
    const uniqueLines = [...new Set(quizletLines)];
    
    console.log(`Unique entries: ${uniqueLines.length}`);
    
    // Write to output file
    const outputFile = 'quizlet-flashcards.txt';
    fs.writeFileSync(outputFile, uniqueLines.join('\n'));
    
    console.log(`\nOutput written to: ${outputFile}`);
    console.log('\nFirst 5 entries:');
    uniqueLines.slice(0, 5).forEach((line, i) => {
        console.log(`${i + 1}. ${line}`);
    });
}

// Run if called directly
if (require.main === module) {
    main();
}

module.exports = { parseGlossaryEntries, extractFields, formatForQuizlet, cleanText };

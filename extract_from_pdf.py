import fitz
import json
import re
import os
from collections import OrderedDict
from difflib import SequenceMatcher

INPUT_PDF = 'Lectures.pdf'
OUTPUT_JSON = 'Lectures.json'

def extract_clean_paragraphs(text):

    def filter_lines_with_three_letters(text_block):
        lines = text_block.splitlines()
        return "\n".join(line for line in lines if re.search(r'[A-Za-z]{3}', line))
    filtered_text = filter_lines_with_three_letters(text)

    lines = filtered_text.split('\n')
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        if re.match(r'^\s*\d+\s*$', stripped):
            continue
        if not stripped or len(stripped) < 3:
            continue
        cleaned_lines.append(stripped)

    paragraph_text = ' '.join(cleaned_lines)
    paragraph_text = re.sub(r'\s+', ' ', paragraph_text)
    return paragraph_text.strip()

def insert_period_after_title_match(title, content, max_scan=None, start_offset=0):
    title_letters = [c for c in title.lower() if c.isalpha()]
    match_length = 0
    content_letter_index = 0
    i = start_offset 

    while match_length < len(title_letters) and i < len(content):
        c = content[i]
        if c.isalpha():
            if c.lower() == title_letters[match_length]:
                match_length += 1
            else:
                match_length = 0
                if title_letters and c.lower() == title_letters[0]:
                    match_length = 1
            content_letter_index += 1
        elif not c.isspace():
            content_letter_index += 1

        if max_scan is not None and content_letter_index >= max_scan:
            break
        i += 1

    if match_length == len(title_letters):
        if i < len(content) and content[i] != '.':
            return content[:i] + '.' + content[i:]
    return content

def remove_capital(text, min_length=4):
    # Matches all uppercase blocks including internal spaces and any non-period symbols
    # [A-Z] - uppercase letters
    # [^\w\s.] - any character that's not a word character, whitespace, or period
    pattern = re.compile(r"\b(?:(?:[A-Z]|[^\w\s.])+\s?)+\b")

    result = []
    last_end = 0

    for match in pattern.finditer(text):
        start, end = match.start(), match.end()
        block = match.group().strip()
        words = block.split()

        # Ignore if it's a single character that's a letter (symbols count as part of blocks)
        if len(words) == 1 and len(words[0]) == 1 and words[0].isalpha():
            continue

        # Check for trailing single character (letters or symbols except period)
        has_trailing_single = (len(words) >= 2 and len(words[-1]) == 1 
                              and words[-1] != '.')

        core_words = words[:-1] if has_trailing_single else words
        core_block = ' '.join(core_words)

        # Skip blocks that don't meet min length (excluding spaces and non-letter chars)
        # We count only alphanumeric characters for length requirement
        if len(re.sub(r'[^A-Za-z0-9]', '', core_block)) <= min_length:
            continue

        # Build the replacement block
        replacement = core_block + '.'
        if has_trailing_single:
            replacement += ' ' + words[-1]

        # Check the char after the match
        char_after = text[end] if end < len(text) else ''
        if char_after == '.':
            replacement = replacement.rstrip('.')

        # Add space if needed
        if end >= len(text) or text[end] not in [' ', '.']:
            replacement += ' '

        # Append unchanged text + replacement
        result.append(text[last_end:start])
        result.append(replacement)
        last_end = end

    # Append remaining text
    result.append(text[last_end:])
    return ''.join(result)

def normalize_text(text):
    # Replace Unicode punctuation with ASCII equivalents
    replacements = {
        # '“': '"', '”': '"', '„': '"', '‟': '"', '″': '"', 
        '‘': "'", '’': "'", '‚': "'", '‛': "'",
        '—': '-', '–': '-', '−': '-',
        '…': '...',
        ' ': ' ', ' ': ' ',
        '′': "'",
        '‹': '<', '›': '>',
        # '«': '"', '»': '"'
    }
    for uni_char, ascii_char in replacements.items():
        text = text.replace(uni_char, ascii_char)

    # Remove duplicate periods
    text = re.sub(r'\.\s+\.', '.', text)

    # Match full all-caps block followed by a capitalized word
    text = remove_capital(text)

    return text


def is_similar_content(prev_content, current_content, similarity_threshold=1):

    if not prev_content or not current_content:
        return False
        
    # If one is significantly longer than the other, they're not similar
    len_ratio = min(len(prev_content), len(current_content)) / max(len(prev_content), len(current_content))
    if len_ratio < 0.8:  # More than 20% length difference
        return False
    
    # If they are exactly the same
    if prev_content.strip() == current_content.strip():
        return True

    if similarity_threshold >= 1:
        return False
    
    # Calculate similarity using sequence matching
    similarity = SequenceMatcher(None, prev_content, current_content).ratio()
    
    return similarity >= similarity_threshold

def extract_all_toc_entries_with_content(pdf_path):
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()

    first_title = toc[0][1].strip()
    ZERO_INDEXED = bool(re.match(r'^0+($|[^0-9])', first_title)) # One or more leading zeros, Followed by end of string or a non-digit character

    toc_entries = [
        {"level": level, "title": title, "start_page": start_page}
        for level, title, start_page in toc
        if title.strip() != "Blank Page"
    ]

    toc_level_1_2 = [e for e in toc_entries if e["level"] in (1, 2)]
    toc_level_1_2.sort(key=lambda x: x["start_page"])

    seen_pages = set()
    filtered_toc = []
    for entry in toc_level_1_2:
        if entry["start_page"] not in seen_pages:
            filtered_toc.append(entry)
            seen_pages.add(entry["start_page"])

    toc_flat = []
    for new_index, entry in enumerate(filtered_toc):
        toc_flat.append(OrderedDict([
            ("index", new_index + 1 * (not ZERO_INDEXED)),
            ("level", entry["level"]),
            ("start_page", entry["start_page"]),
            ("end_page", None),
            ("title", entry["title"])
        ]))

    for i in range(len(toc_flat)):
        current = toc_flat[i]
        next_start = toc_flat[i + 1]["start_page"] if i + 1 < len(toc_flat) else len(doc) + 1
        current["end_page"] = next_start - 1

        chapter_text = ""
        previous_page_content = None
        
        for page_num in range(current["start_page"], next_start):
            page = doc.load_page(page_num - 1)
            current_page_text = page.get_text()
            current_page_cleaned = extract_clean_paragraphs(current_page_text)
            
            # Skip if this page is very similar to the previous page
            if previous_page_content and is_similar_content(previous_page_content, current_page_cleaned):
                continue
                
            chapter_text += current_page_text
            previous_page_content = current_page_cleaned

        cleaned_content = extract_clean_paragraphs(chapter_text)
        fixed_content = insert_period_after_title_match(current["title"], cleaned_content)
        fixed_content = normalize_text(fixed_content)  # <-- Capital letters fix
        current["content"] = fixed_content

    for entry in toc_entries:
        if entry["level"] >= 2:
            page = entry["start_page"]
            try:
                level3_page_text = extract_clean_paragraphs(doc.load_page(page - 1).get_text())
            except Exception:
                continue

            for parent in toc_flat:
                if parent["start_page"] <= page <= parent["end_page"]:
                    updated_content = insert_period_after_title_match(entry["title"], parent["content"])
                    updated_content = normalize_text(updated_content)
                    parent["content"] = updated_content
                    break

    return toc_flat

def save_content_json():
    if not os.path.exists(INPUT_PDF):
        print(f"Error: {INPUT_PDF} not found in the current directory")
        return
        
    print(f"Processing: {INPUT_PDF} -> {OUTPUT_JSON}")

    try:
        toc_content = extract_all_toc_entries_with_content(INPUT_PDF)
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(
                [{k: v for k, v in entry.items() if k not in ("level", "start_page", "end_page")} for entry in toc_content],
                f, ensure_ascii=False, indent=2
            )
        print(f"Saved: {OUTPUT_JSON}")
    except Exception as e:
        print(f"Error processing {INPUT_PDF}: {str(e)}")

# === Main
if __name__ == "__main__":
    save_content_json()

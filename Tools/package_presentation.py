#!/usr/bin/env python3
import os
import csv
import shutil
import re

def fix_winner_loser_spacing(match):
    label = match.group(1)
    parts = [
        match.group(2),
        match.group(3),
        match.group(4),
        match.group(5)
    ]
    total = match.group(6)

    # Format suit counts with correct spacing: two before, one around =
    # fixed_parts = [f"  {p.split('=')[0].strip()} = {p.split('=')[1].strip()}" for p in parts]
    fixed_parts = [f"  {p.split('=')[0].strip()}={p.split('=')[1].strip()}" for p in parts]

    # Winners has space before Total, Losers has newline before Total
    if label == "Winners":
        tail = f"  Total = {total}"
    else:
        # tail = f"\\nTotal = {total}"
        tail = f"  Total = {total}"

    return f"{label}: {''.join(fixed_parts)}{tail}"
    
def strip_phrases(file_path, regex_control_tags, regex_prompts, literal_fragments, lesson_name=None):
    """
    Cleans PBN commentary for presentation/rotation use:
      Pass 1: Remove bridge-classroom control tags (case-sensitive regex).
      Pass 2: Remove UI prompt sentences (case-insensitive regex).
      Pass 3: Remove leftover literal fragments (case-insensitive).
      Cleanup: Whitespace normalization.
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return

    # Adjust font size for 100-level lessons
    if lesson_name and "100" in lesson_name:
        content = content.replace('%Font:Commentary "Georgia",12', '%Font:Commentary "Georgia",10')

    # Fix spacing in Winner and Loser counts:
    pattern = r'(Winners|Losers):\s*(\\S\s*=\s*\d+)\s*(\\H\s*=\s*\d+)\s*(\\D\s*=\s*\d+)\s*(\\C\s*=\s*\d+)\s*Total\s*=\s*(\d+)'
    content = re.sub(pattern, fix_winner_loser_spacing, content)

    # Pass 1: Remove bridge-classroom control tags (case-sensitive)
    for pat in regex_control_tags:
        content = re.sub(pat, "", content)

    # Pass 2: Remove UI prompt sentences (case-insensitive)
    for pat in regex_prompts:
        content = re.sub(pat, "", content, flags=re.IGNORECASE)

    # Pass 3: Remove leftover literal fragments (case-insensitive)
    for phrase in literal_fragments:
        content = re.sub(re.escape(phrase), "", content, flags=re.IGNORECASE)

    # Remove any whitespace immediately to the right of '{'
    content = re.sub(r'(\{)\s+', r'\1', content)

    # Condense multiple blank lines to a single blank line
    content = re.sub(r'\n\s*\n+', '\n\n', content)

    # For lines that contain only "{" (possibly with spaces), remove any blank lines following it
    # and join it with the next non-blank line.
    content = re.sub(r'(^\s*\{\s*$)\n(?:\s*\n)+(\s*\S)', r'\1 \2', content, flags=re.MULTILINE)

    try:
        with open(file_path, 'w') as f:
            f.write(content)
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")

def main():
    # Set up base directories based on the current working directory
    base_dir = os.getcwd()
    package_dir = os.path.join(base_dir, "Package")
    presentation_dir = os.path.join(base_dir, "Presentation")

    # --- Pass 1: Bridge-classroom control tags (case-sensitive) ---
    regex_control_tags = [
        r"\[BID[^\]]*\]",
        r"\[bid[^\]]*\]",
        r"\[NEXT\]",
        r"\[ROTATE\]",
        r"\[show\s+[A-Z]+\]",
        r"\[PLAY\s+[^\]]*\]",
        r"\[RESET\]",
        r"\[clear-commentary\]",
        r"\[showcards\]",
        r"\[choose-card[^\]]*\]",
    ]

    # --- Pass 2: UI prompt sentences (case-insensitive, after tags stripped) ---
    regex_prompts = [
        # "Decide what you would say/bid, then click on BID above." (all variants)
        r"Decide what you would \w+[^.]*(?:BID|<b>BID</b>)[^.]*\.",
        # Navigation / action prompts
        r"Make a Plan[^.]*\.",
        r"To make South the declarer[^.]*\.",
        r"Click ROTATE[^.]*\.",
        r"When you have made your choice[^.]*\.",
        r"Click\s+NEXT[^.]*\.",
        r"Click\s+for[^.]*\.",
        r"Click\s+to\s+see[^.]*\.",
        r"Click\s*for[^.]*\.",
        r"Clickfor[^.]*\.",
        r"Click\s*\.",
        # Scene-setting prompts
        r"The bidding has gone as shown\.",
        r"The bidding is shown\.",
        r"You are South and it is your bid\.",
        r"You are the dealer\.",
        r"You dealt so it is your bid\.",
        r"It is your bid\.",
        r"and it is your lead\.",
        r"and it is your play\.",
        # Question prompts
        r"What do you say(?: now)?\?",
        r"What do you bid(?: now| next)?\?",
        r"What do you respond\?",
        r"What do you lead\?",
    ]

    # --- Pass 3: Leftover fragments (case-insensitive) ---
    literal_fragments = [
        "to see all the hands. ",
        "to see the full deal. ",
        "to see all four hands. ",
        "to see the complete deal. ",
        "for the complete deal.",
        "for the full deal. ",
        "for all four hands. ",
        "for a view of all four hands. ",
        "to see if you made the slam. ",
        "to see all the hands.. ",
        "to see the hands.",
        "to see all hands. ",
        "to continue.",
        "to see how things should have played out. ",
        "again for an alternate layout. ",
        "Both.  ",
    ]

    # Load the mapping from titles.csv (fields: Lesson, Folder) located in the Package folder
    titles_path = os.path.join(package_dir, "titles.csv")
    lesson_to_folder = {}
    with open(titles_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lesson = row.get("Lesson", "").strip()
            folder = row.get("Folder")
            if folder is None or folder.strip() == "":
                print(f"Warning: Folder value for lesson '{lesson}' is missing. Assigning 'Uncategorized'.")
                folder = "Uncategorized"
            else:
                folder = folder.strip()
            lesson_to_folder[lesson] = folder

    # Create the Presentation folder if it doesn't already exist
    if not os.path.exists(presentation_dir):
        os.makedirs(presentation_dir)

    folders_created = 0
    files_copied = 0

    # Iterate through all files in the Package folder looking for .pbn files
    for entry in os.listdir(package_dir):
        if entry.lower().endswith(".pbn"):
            file_base = os.path.splitext(entry)[0]
            if file_base in lesson_to_folder:
                target_folder_name = lesson_to_folder[file_base]
                target_folder_path = os.path.join(presentation_dir, target_folder_name)
                if not os.path.exists(target_folder_path):
                    os.makedirs(target_folder_path)
                    folders_created += 1

                # Copy and rename the .pbn file with the "Baker Bridge " prefix
                src_pbn = os.path.join(package_dir, entry)
                new_pbn_name = "Baker Bridge " + entry
                dst_pbn = os.path.join(target_folder_path, new_pbn_name)
                shutil.copy2(src_pbn, dst_pbn)
                files_copied += 1

                # Process the copied .pbn file
                strip_phrases(dst_pbn, regex_control_tags, regex_prompts, literal_fragments, file_base)
                # Check for an associated PDF file with the same base name + "_Intro.pdf"
                pdf_filename = f"{file_base}_Intro.pdf"
                src_pdf = os.path.join(package_dir, pdf_filename)
                if os.path.exists(src_pdf):
                    new_pdf_name = "Baker Bridge " + pdf_filename
                    dst_pdf = os.path.join(target_folder_path, new_pdf_name)
                    shutil.copy2(src_pdf, dst_pdf)
                    files_copied += 1
            else:
                print(f"Title not found for file: {entry}")

    print(f"\nFolders created: {folders_created}")
    print(f"Files copied: {files_copied}")

if __name__ == "__main__":
    main()
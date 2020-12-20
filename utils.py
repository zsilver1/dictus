from typing import List, Dict, Set, Tuple
import os
import shutil
import re

FOOTNOTE_LINK = re.compile(r"\[\^([\w]+)\]")
FOOTNOTE_LABEL = re.compile(r"^\[\^([\w]+)]:\s?(.*)")


def cleanup_md_file(filename: str, backup: bool = True):
    if backup:
        shutil.copyfile(filename, f"{filename}.backup")

    headers: List[str] = []

    # map of header -> sub-contents
    header_contents: Dict[str, str] = {}

    first_header_line = -1

    # map of original footnote number to its label
    footnote_key_to_label: Dict[str, str] = {}

    # list of footnote labels in order
    fixed_footnotes: List[Tuple[str, str]] = []
    footnote_set: Set[str] = set()

    with open(filename) as f:
        contents = f.readlines()

    hit_footers = False
    current_header = None
    current_contents: List[str] = []
    for i, line in enumerate(contents):
        if line.strip().startswith("# "):
            if first_header_line < 0:
                first_header_line = i
            header = line[2:].strip()
            if current_header:
                header_contents[current_header] = "".join(current_contents)
                current_contents = []
            headers.append(header)
            current_header = header
        elif m := FOOTNOTE_LABEL.match(line):
            hit_footers = True
            footnote_key_to_label[m.group(1)] = m.group(2)
        elif current_header:
            if not hit_footers:
                current_contents.append(line)

    if current_header:
        header_contents[current_header] = "".join(current_contents)

    result: List[str] = []

    # we now know the correct order of the file
    # first output pre-header lines
    for i, line in enumerate(contents):
        if i >= first_header_line:
            break
        result.append(line)

    headers.sort()

    old_to_new_footnotes: Dict[str, str] = {}
    cur_footnote_index = 1

    def _repl(m):
        nonlocal cur_footnote_index
        if m.group(1) not in old_to_new_footnotes:
            if m.group(1).isnumeric():
                old_to_new_footnotes[m.group(1)] = str(cur_footnote_index)
                cur_footnote_index += 1
                return f"[^{cur_footnote_index - 1}]"
            else:
                return m.group()
        return f"[^{old_to_new_footnotes[m.group(1)]}]"

    for header in headers:
        text = header_contents[header]
        for key in FOOTNOTE_LINK.findall(text):
            if footnote_key_to_label[key] not in footnote_set:
                fixed_footnotes.append((key, footnote_key_to_label[key]))
                footnote_set.add(footnote_key_to_label[key])
            text = re.sub(FOOTNOTE_LINK, _repl, text)
        result.append(f"# {header}\n")
        result.append(text)

    # finish with footnotes
    index = 1
    for footnote in fixed_footnotes:
        key, label = footnote
        if key.isnumeric():
            result.append(f"[^{index}]: {label}{os.linesep}{os.linesep}")
            index += 1
        else:
            result.append(f"[^{key}]: {label}{os.linesep}{os.linesep}")

    result_str = "".join(result).rstrip()
    with open(filename, "w") as f:
        f.write(result_str)

#!/usr/bin/env python3
"""Convert documents from Obsidian markdown to Org Roam while maintaining links."""

import os
import subprocess
import re

OUT_DIR = "./out/"
# a list of tuples to find matches in the formatting string
# this is for beginning of line items
FORMAT_LIST = (
    ["####", "###", "##", "---"],
    ["***", "**", "*", ""],
)


def name_output(input_file: str) -> str:
    """Return output file name with .org instead of .md"""
    path = input_file.split("/")
    output_md = path[-1].split(".")
    return output_md[0] + ".org"


def replace_links(input_line: str) -> str:
    """Return output line with properly formatted links."""
    output_line = input_line
    # Standard obsidian links
    links = re.findall(r"\[\[(?:\S+\s*)+\]\]", output_line)
    for link in links:
        new_link = link.replace("[", "")
        new_link = new_link.replace("]", "")
        if "." in link:
            new_link = f"[[./{new_link}][{new_link}]]"
        else:
            new_link = f"[[./{new_link}.org][{new_link}]]"
        output_line = output_line.replace(link, new_link)
    # Links with special descriptions
    link_names = re.findall(r"\[\[(?:\w+\s*)+\|", output_line)
    link_locations = re.findall(r"\|(?:\w+\s*)+\]\]", output_line)
    try:
        assert len(link_names) == len(link_locations)
    except AssertionError:
        print("Error: link names and locations do not match up.")
    for i in range(len(link_names)):
        new_link_name = link_names[i].replace("[", "").replace("|", "")
        new_link_location = link_locations[i].replace("]", "").replace("|", "")
        if "." in new_link_location:
            new_link = f"[[./{new_link_location}][{new_link_name}]]"
        else:
            new_link = f"[[./{new_link_location}.org][{new_link_name}]]"
        output_line = output_line.replace(link, new_link)
    # Standard markdown links

    return output_line


def replace_code_block(input_line: str) -> str:
    """Return properly formatted code blocks."""
    code_block = re.search("```\w+", input_line)
    output_line = input_line
    if code_block is not None:
        output_line = input_line.replace("```", "#+begin_src ")
    else:
        code_block = re.search("```", input_line)
        if code_block is not None:
            output_line = input_line.replace("```", "#+end_src")

    return output_line


def format_line(input_line: str) -> str:
    """Return a properly formatted line"""
    output_line = input_line
    # start of line items
    for item in range(len(FORMAT_LIST[0])):
        if output_line.startswith(FORMAT_LIST[0][item]):
            output_line = input_line.replace(FORMAT_LIST[0][item], FORMAT_LIST[1][item])

    output_line = replace_links(output_line)
    output_line = replace_code_block(output_line)

    return output_line


def transfer(input_file: str) -> None:
    """Transfer from a markdown file to an Org file."""
    output_file = name_output(input_file)

    try:
        with open(input_file, "r") as markdown:
            in_lines = markdown.readlines()
    except FileNotFoundError:
        print("Error: file not found.")
        return
    try:
        os.mkdir(OUT_DIR)
    except FileExistsError:
        pass
    with open(OUT_DIR + output_file, "w") as out:
        out.write(":PROPERTIES:\n:ID:       ")
        try:
            uuid = (
                subprocess.run(
                    ["/usr/bin/uuidgen"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                .stdout.decode()
                .strip()
            )
        except subprocess.CalledProcessError:
            print("Error retrieving uuid.")
            return
        out.write(uuid)
        out.write("\n:END:\n")
        if in_lines[0].startswith("#"):
            in_lines[0] = in_lines[0].replace("#", "#+title:")
        for line in in_lines:
            if line.startswith("tags:"):
                line = line.replace("#", "")
                line = line.replace("tags:", "#+filetags:")
            out.write(format_line(line))
    with open(OUT_DIR + ".orgids", "a") as append:
        append.write(f'("Obsidian/{output_file}" "{uuid}")')


if __name__ == "__main__":
    transfer("./Phys 404.md")

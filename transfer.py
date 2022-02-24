#!/usr/bin/env python3
"""Convert documents from Obsidian markdown to Org Roam while maintaining links."""

import os

OUT_DIR = "./out/"


def name_output(input_file: str) -> str:
    """Return output file name with .org instead of .md"""
    path = input_file.split("/")
    output_md = path[-1].split(".")
    return output_md[0] + ".org"


def format_line(input_line: str) -> str:
    """Return a properly formatted line"""
    return input_line


def transfer(input_file: str) -> None:
    """Transfer from a markdown file to an Org file."""
    output_file = name_output(input_file)

    try:
        with open(input_file, "r") as md:
            in_lines = md.readlines()
    except FileNotFoundError:
        print("Error: file not found.")
        return
    try:
        os.mkdir(OUT_DIR)
    except FileExistsError:
        pass
    with open(OUT_DIR + output_file, "w") as out:
        for line in in_lines:
            out.write(format_line(line))


if __name__ == "__main__":
    transfer("./Phys 404.md")

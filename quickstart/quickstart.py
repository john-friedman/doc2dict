from doc2dict import *
from selectolax.parser import HTMLParser

tenk_mapping_dict = {
    "levels": {0: [
        {"name": "part", "regex": r'^part\s*([ivx]+)$'},
        {"name": "signatures", "regex": r'^signatures?\.*$'}
    ],
    1: [
        {"name": "item", "regex": r'^item\s*(\d+)\.?([a-z])?(?![a-z])'}
    ]},
    "instructions": {
        "processing": {},
        "postprocessing": {}
    },
    "dct": {
        "processing": {
            "table": {
                "detect_fake_tables": True,
                "strip_cell_text": True
            }
        },
        "postprocessing": {
            "table": {
                "bool" : [
                    "validate_structure",
                    "merge_formatting_chars",
                    "convert_images_to_text",
                    "remove_empty_rows",
                    "remove_empty_columns",
                    "remove_subset_rows_bottom_to_top",
                    "remove_subset_rows_top_to_bottom",
                    "remove_subset_columns_left_to_right",
                    "remove_subset_columns_right_to_left",
                    "simplify_cells",
                    "disallow_single_row_tables"
                ],
                "footnotes": {
                    "regex": "^(\\*|\\(\\d+\\)|\\d+|†+)"
                },
                "preamble" : {
                    "lines" : 3
                },
                "postamble" : {
                    "lines" : 3
                }

            }
        }
    }
}

# Load your html file
with open('example_output\html\msft_10k_2024.html','r') as f:
    content = f.read()


body = HTMLParser(content).body

# convert html to a series of instructions
instructions = convert_html_to_instructions(body)

with open('instructions.txt','w',encoding='utf-8') as f:
    for instruction in instructions:
        f.write(str(instruction))
        f.write('\n')

# visualize the conversion
visualize_instructions(instructions)

# convert instructions to dictionary
dct = html2dict(content,mapping_dict=tenk_mapping_dict)

# visualize dictionary
visualize_dict(dct)

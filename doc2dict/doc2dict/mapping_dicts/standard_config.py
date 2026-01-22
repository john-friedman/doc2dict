STANDARD_CONFIG = {
    "instructions": {
        "processing": {},
        "postprocessing": {}
    },
    "dct": {
        "preprocessing" : {
            "remove_strings" : [
                {"regex":r"^\d+$"}, 
                {"regex":r"^-\d+-$"}, 
                {"regex":r"(^\s*\d+\s*\||\|\s*\d+\s*$)"}, # e.g. BRYN MAWR BANK CORPORATION |   2020 PROXY STATEMENT |  45
                {"regex":r"^_+$"}, 
                {"regex":r"^●(\s*●)*"},
                {"regex": r"^table\s+of\s+contents$", "has_href":True}
            ],
            "remove_repetitive_text" : {
                "threshold" : 20
            }
        },
        "processing": {
            "table": {
                "detect_fake_tables": True,
                "strip_cell_text": True
            }
        },
        "postprocessing": {
            "table": {
                "bool": [
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
                    "disallow_single_row_tables",
                    "merge_duplicate_header_rows_down",
                    "inherit_section_title"
                ],
                "footnotes": {
                    "regex": r"^(\*|\(.{1,2}\)|\d+|†+)",
                    "check_next_n_lines": 3
                },
                "preamble": {
                    "lines": 7
                },
                "postamble": {
                    "lines": 7
                }
            }
        }
    }
}
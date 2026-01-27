# Installation

```bash
pip install doc2dict
```

## Parsing

### HTML
```python
from doc2dict import html2dict, visualize_dict

# Load your html file
with open('apple_10k_2024.html','r') as f:
    content = f.read()

# Parse wihout a mapping dict
dct = html2dict(content,mapping_dict=None)
# Parse using the standard mapping dict
dct = html2dict(content)

# Visualize Parsing
visualize_dict(dct)
```

### TXT
```python
from doc2dict import txt2dict, visualize_dict

# Load your html file
with open('apple_10k_2024.text','r') as f:
    content = f.read()

# Parse wihout a mapping dict
dct = txt2dict(content,mapping_dict=None)
# Parse using the standard mapping dict
dct = txt2dict(content)

# Visualize Parsing
visualize_dict(dct)
```

### PDF
```python
from doc2dict import pdf2dict, visualize_dict

# Load your html file
with open('apple_10k_2024.pdf','rb') as f:
    content = f.read()

# Parse with no mapping dict
dct = pdf2dict(content,mapping_dict=None)

# Visualize Parsing
visualize_dict(dct)
```

## Mapping Dicts

Mapping dictionaries are rules that you pass into the parser to tweak its functionality.

The below mapping dict tells the parser that "item" header should appear in the nesting of "part" headers. Also there are a bunch of other rules that should be kept by default.

```python
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
```

## Debugging

```python
from doc2dict import *
from selectolax.parser import HTMLParser

# Load your html file
with open('apple_10k_2024.htm','r') as f:
    content = f.read()


body = HTMLParser(content).body

# convert html to a series of instructions
instructions = convert_html_to_instructions(body)

# visualize the conversion
visualize_instructions(instructions)

# convert instructions to dictionary
dct = html2dict(content,mapping_dict=tenk_mapping_dict)

# visualize dictionary
visualize_dict(dct)
```

### Benchmarks 

Based on my personal (potato) laptop:
* About 500 pages per second single threaded.
* Parses the 57 page Apple 10-K in 160 milliseconds.

### Target Speed
I think I can get to ~40,000 pages per second in the near future for html, with proper threading. Would need:
- rust rewrite
- reducing waste in function calls (I've bloated the package by adding features, it used to iterate in one read over the DOM)


## Converting to other formats

Experimental.

### convert_dict_to_data_tuples

Converts the dictionary representation into a flat format. Some information is lost. I am using this to store tbs of SEC filings data in parquet format. Roughly 120x smaller than original html.

```
convert_dict_to_data_tuples(dct['document'])
# returns ('section_id', 'content_type', 'content_value', 'level', 'class')
```

### convert_data_tuples_to_dict

Converts the flat representation into dictionary format. Can apply a mapping dict. This allows you tweak data after it has been processed. This is useful, but tired. So will wait to explain further.

```
convert_data_tuples_to_dict(tuples_list, mapping_dict=None)
```

### get_title_from_dict

Returns a section in dict.
```
get_title_from_dict(dct, title=None, title_regex=None, title_class=None)
```

### get_title_from_tuples

Returns a section in tuples.
```
get_title_from_tuples(tuples_list, title=None, title_regex=None, title_class=None)
```

Example
```
item1a_tuples = get_title_from_tuples(
    doc.data_tuples,
    title_regex=r'item 1a',
    title_class='item'
)
```

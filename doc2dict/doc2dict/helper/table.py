import re

EMPTY_CHARS = ' \t\n\r\xa0\u200b'
EMPTY_TABLE_CHARS = ['', '–', '-']
LEFT_TABLE_CHARS = ['$','(']
RIGHT_TABLE_CHARS = [')','%']

def strip_empty_chars_from_cells(table):
    """Strip EMPTY_CHARS from beginning and end of all cell text"""
    if not table:
        return table
    
    stripped_table = []
    for row in table:
        stripped_row = []
        for cell in row:
            if isinstance(cell, dict):
                # Copy the cell dict
                stripped_cell = cell.copy()
                # Strip text if present
                if 'text' in stripped_cell:
                    stripped_cell['text'] = stripped_cell['text'].strip(EMPTY_CHARS)
                stripped_row.append(stripped_cell)
            else:
                # Cell is a string
                stripped_row.append(cell.strip(EMPTY_CHARS) if isinstance(cell, str) else cell)
        stripped_table.append(stripped_row)
    
    return stripped_table


def merge_duplicate_header_rows_down(table):
    """Merge top two rows if top row has consecutive duplicate cells."""
    if not table or len(table) < 2:
        return table
    
    top_row = table[0]
    
    # Check if top row has any consecutive duplicates
    has_consecutive_duplicates = False
    for i in range(len(top_row) - 1):
        # Extract text for comparison
        cell1_text = top_row[i].get('text', '') if isinstance(top_row[i], dict) else top_row[i]
        cell2_text = top_row[i + 1].get('text', '') if isinstance(top_row[i + 1], dict) else top_row[i + 1]
        
        if cell1_text == cell2_text:
            has_consecutive_duplicates = True
            break
    
    if not has_consecutive_duplicates:
        return table
    
    # Merge top two rows
    second_row = table[1]
    merged_row = []
    
    for i in range(len(top_row)):
        # Extract text from both rows
        top_text = top_row[i].get('text', '') if isinstance(top_row[i], dict) else top_row[i]
        
        if i < len(second_row):
            second_text = second_row[i].get('text', '') if isinstance(second_row[i], dict) else second_row[i]
            merged_text = top_text + '\n' + second_text
        else:
            merged_text = top_text
        
        # Keep as dict if original was dict, otherwise string
        if isinstance(top_row[i], dict):
            merged_cell = top_row[i].copy()
            merged_cell['text'] = merged_text
            merged_row.append(merged_cell)
        else:
            merged_row.append(merged_text)
    
    # Return new table with merged row and remaining rows
    return [merged_row] + table[2:]

def is_subset(items1, items2, empty_chars):
    """returns true if items1 is a subset of items2"""
    for item1, item2 in zip(items1, items2):
        # If item1 has an image, it's not a subset
        if 'image' in item1:
            return False
        # Check text content
        if item1.get('text', '') not in empty_chars and item1.get('text', '') != item2.get('text', ''):
            return False
    return True



def remove_subset_rows(table, empty_chars, direction="bottom_to_top"):
    """
    Remove subset rows from the table.
    direction: "bottom_to_top" or "top_to_bottom"
    """
    if not table:
        return table
    
    keep_rows = [True] * len(table)
    
    if direction == "bottom_to_top":
        # Compare each row with the row above it
        for i in range(len(table)-1, 0, -1):
            if is_subset(table[i], table[i-1], empty_chars):
                keep_rows[i] = False
    else:  # top_to_bottom
        # Compare each row with the row below it
        for i in range(len(table)-1):
            if is_subset(table[i], table[i+1], empty_chars):
                keep_rows[i] = False
    
    return [table[i] for i in range(len(table)) if keep_rows[i]]

def remove_subset_columns(table, empty_chars, direction="left_to_right"):
    """
    Remove subset columns from the table.
    direction: "left_to_right" or "right_to_left"
    """
    if not table or not table[0]:
        return table
    
    num_cols = len(table[0])
    keep_cols = [True] * num_cols
    
    if direction == "left_to_right":
        # Compare each column with the column to its right
        for j in range(num_cols-1):
            col1 = [row[j] for row in table]
            col2 = [row[j+1] for row in table]
            if is_subset(col1, col2, empty_chars):
                keep_cols[j] = False
    else:  # right_to_left
        # Compare each column with the column to its left
        for j in range(num_cols-1, 0, -1):
            col1 = [row[j] for row in table]
            col2 = [row[j-1] for row in table]
            if is_subset(col1, col2, empty_chars):
                keep_cols[j] = False
    
    return [[row[j] for j in range(num_cols) if keep_cols[j]] for row in table]

def is_left_char_cell(cell):
    """Check if cell contains only LEFT_TABLE_CHARS + EMPTY_CHARS"""
    if 'image' in cell:
        return False
    text = cell.get('text', '')
    if not text:
        return False
    # Check if all characters in text are either left chars or empty chars
    return all(char in LEFT_TABLE_CHARS + EMPTY_TABLE_CHARS for char in text)

def is_right_char_cell(cell):
    """Check if cell contains only RIGHT_TABLE_CHARS + EMPTY_CHARS"""
    if 'image' in cell:
        return False
    text = cell.get('text', '')
    if not text:
        return False
    # Check if all characters in text are either right chars or empty chars
    return all(char in RIGHT_TABLE_CHARS + EMPTY_TABLE_CHARS for char in text)

def is_content_cell(cell):
    """Check if cell has meaningful content (not just formatting chars)"""
    if 'image' in cell:
        return True
    text = cell.get('text', '')
    if not text:
        return False
    # Content cell if it has chars that aren't formatting or empty
    all_formatting_chars = LEFT_TABLE_CHARS + RIGHT_TABLE_CHARS + EMPTY_TABLE_CHARS
    return any(char not in all_formatting_chars for char in text)

def find_next_content_cell(row, start_col):
    """Find next cell with content to the right"""
    for col in range(start_col + 1, len(row)):
        if is_content_cell(row[col]):
            return col
    return None

def find_prev_content_cell(row, start_col):
    """Find previous cell with content to the left"""
    for col in range(start_col - 1, -1, -1):
        if is_content_cell(row[col]):
            return col
    return None

def merge_cell_content(source_cell, target_cell, direction):
    """Merge source cell text into target cell"""
    source_text = source_cell.get('text', '')
    target_text = target_cell.get('text', '')
    
    # Create a copy of target cell to preserve its attributes
    merged_cell = target_cell.copy()
    
    if direction == 'left':
        # Source goes to the left of target
        merged_cell['text'] = source_text + target_text
    else:  # direction == 'right'
        # Source goes to the right of target
        merged_cell['text'] = target_text + source_text
    
    return merged_cell

def merge_table_formatting(table):
    """Merge formatting characters with adjacent content"""
    if not table or not table[0]:
        return table
    
    # Create a working copy
    result_table = [row[:] for row in table]
    
    # Left merging pass - merge LEFT_TABLE_CHARS with content to their right
    for row_idx, row in enumerate(result_table):
        for col_idx, cell in enumerate(row):
            if is_left_char_cell(cell):
                # Find next content cell to the right
                target_col = find_next_content_cell(row, col_idx)
                if target_col is not None:
                    # Merge this cell's content with the target cell
                    merged_cell = merge_cell_content(cell, row[target_col], 'left')
                    result_table[row_idx][target_col] = merged_cell
                    # Mark source cell as empty
                    result_table[row_idx][col_idx] = {'text': ''}
    
    # Right merging pass - merge RIGHT_TABLE_CHARS with content to their left
    for row_idx, row in enumerate(result_table):
        for col_idx, cell in enumerate(row):
            if is_right_char_cell(cell):
                # Find previous content cell to the left
                target_col = find_prev_content_cell(row, col_idx)
                if target_col is not None:
                    # Merge this cell's content with the target cell
                    merged_cell = merge_cell_content(cell, row[target_col], 'right')
                    result_table[row_idx][target_col] = merged_cell
                    # Mark source cell as empty
                    result_table[row_idx][col_idx] = {'text': ''}
    
    return result_table

def validate_table_structure(table):
    """Check if all rows have same number of columns"""
    if len(table) == 0:
        return table, "dirty"
    
    same_length = all([len(row) == len(table[0]) for row in table])
    if not same_length:
        return table, "dirty"
    
    return table, "valid"

def convert_images_to_text_in_table(table):
    """Convert image cells to text cells with [IMAGE: {src}] format"""
    for row_idx, row in enumerate(table):
        for col_idx, cell in enumerate(row):
            if 'image' in cell:
                src = cell['image'].get('src', '')
                alt = cell['image'].get('alt', '')
                # Create new text cell preserving other attributes
                new_cell = {k: v for k, v in cell.items() if k != 'image'}
                new_cell['text'] = f'[ALT: {alt}. SRC: {src}]'
                table[row_idx][col_idx] = new_cell
    return table

def remove_empty_rows_from_table(table):
    """Remove rows where all cells contain only EMPTY_TABLE_CHARS"""
    empty_chars = EMPTY_TABLE_CHARS
    table = [row for row in table if any(
        ('image' in cell or cell.get('text', '') not in empty_chars)
        for cell in row
    )]
    return table

def remove_empty_columns_from_table(table):
    """Remove columns where all cells contain only EMPTY_TABLE_CHARS"""
    if table and table[0]:
        empty_chars = EMPTY_TABLE_CHARS
        keep_cols = [j for j in range(len(table[0])) if any(
            ('image' in table[i][j] or table[i][j].get('text', '') not in empty_chars)
            for i in range(len(table))
        )]
        table = [[row[j] for j in keep_cols] for row in table]
    return table

def simplify_table_cells(table):
    """Convert cell dictionaries to strings (extract text only)"""
    simplified_table = []
    
    for row in table:
        simplified_row = []
        for cell in row:
            if 'image' in cell:
                # Keep image cells as dicts
                simplified_row.append(cell)
            elif 'text' in cell:
                # Extract just the text string
                simplified_row.append(cell['text'])
            else:
                # Empty cell
                simplified_row.append('')
        simplified_table.append(simplified_row)
    
    return simplified_table

def apply_table_postprocessing(table, rules):
    """Apply table postprocessing rules in order"""
    if not rules:
        return table, "cleaned"

    # Strip empty chars from all cells FIRST
    table = strip_empty_chars_from_cells(table)

    enabled = rules.get("bool", [])
    cleaning_status = "cleaned"

    # Validate structure
    if "validate_structure" in enabled:
        table, status = validate_table_structure(table)
        if status == "dirty":
            cleaning_status = "dirty"

    # Merge formatting characters
    if "merge_formatting_chars" in enabled:
        table = merge_table_formatting(table)

    # Convert images to text
    if "convert_images_to_text" in enabled:
        table = convert_images_to_text_in_table(table)

    # Remove empty rows
    if "remove_empty_rows" in enabled:
        table = remove_empty_rows_from_table(table)

    # Remove empty columns
    if "remove_empty_columns" in enabled:
        table = remove_empty_columns_from_table(table)

    # Remove subset rows
    if "remove_subset_rows_bottom_to_top" in enabled:
        table = remove_subset_rows(table, EMPTY_TABLE_CHARS, "bottom_to_top")

    if "remove_subset_rows_top_to_bottom" in enabled:
        table = remove_subset_rows(table, EMPTY_TABLE_CHARS, "top_to_bottom")

    # Remove subset columns
    if "remove_subset_columns_left_to_right" in enabled:
        table = remove_subset_columns(table, EMPTY_TABLE_CHARS, "left_to_right")

    if "remove_subset_columns_right_to_left" in enabled:
        table = remove_subset_columns(table, EMPTY_TABLE_CHARS, "right_to_left")

    # Simplify cells
    if "simplify_cells" in enabled:
        table = simplify_table_cells(table)

    if "merge_duplicate_header_rows_down" in enabled:
        table = merge_duplicate_header_rows_down(table)

    return table, cleaning_status
def walk_and_process_tables(obj, rules):
    """Recursively walk through document and apply table postprocessing"""
    if isinstance(obj, dict):
        if 'table' in obj:
            # Found a table - apply postprocessing
            table = obj['table']['data']
            processed_table, status = apply_table_postprocessing(table, rules)
            obj['table']['data'] = processed_table 
            obj['table']['cleaned'] = (status == "cleaned") 
        else:
            # Recurse into nested structures
            for value in obj.values():
                walk_and_process_tables(value, rules)
    elif isinstance(obj, list):
        for item in obj:
            walk_and_process_tables(item, rules)


def collect_table_footnotes(parent_contents, table_key, regex_pattern, check_next_n_lines=1):
    
    # Get all keys sorted numerically
    try:
        sorted_keys = sorted(parent_contents.keys(), key=lambda x: int(x) if str(x).lstrip('-').isdigit() else float('inf'))
    except:
        sorted_keys = sorted(parent_contents.keys())
    
    # Find the index of our table
    try:
        table_index = sorted_keys.index(table_key)
    except ValueError:
        return  # Table key not found
    
    # Collect footnotes from subsequent items
    footnotes = []
    keys_to_remove = []
    
    i = table_index + 1
    while i < len(sorted_keys):
        key = sorted_keys[i]
        item = parent_contents[key]
        
        # Only check text and textsmall items
        if not isinstance(item, dict):
            # Hit a non-dict item, stop collecting
            break
            
        matched = False
        text_content = None
        content_type = None
        
        # Check if it's a text or textsmall item
        if 'text' in item:
            text_content = item['text']
            content_type = 'text'
        elif 'textsmall' in item:
            text_content = item['textsmall']
            content_type = 'textsmall'
        
        if text_content is not None:
            match = re.match(regex_pattern, text_content.strip())
            if match:
                # Found a footnote marker
                footnote_id = match.group(1)
                text_without_id = text_content.strip()[len(match.group(0)):]
                
                # Initialize footnote entry
                current_footnote = {
                    content_type: text_without_id.strip(),
                    'footnote_id': footnote_id
                }
                keys_to_remove.append(key)
                
                # Look ahead for continuation text
                lookahead_count = 0
                j = i + 1
                
                while j < len(sorted_keys) and lookahead_count < check_next_n_lines:
                    next_key = sorted_keys[j]
                    next_item = parent_contents[next_key]
                    
                    if not isinstance(next_item, dict):
                        break
                    
                    next_text = None
                    next_type = None
                    
                    if 'text' in next_item:
                        next_text = next_item['text']
                        next_type = 'text'
                    elif 'textsmall' in next_item:
                        next_text = next_item['textsmall']
                        next_type = 'textsmall'
                    
                    if next_text is not None:
                        # Check if this is a new footnote
                        next_match = re.match(regex_pattern, next_text.strip())
                        if next_match:
                            # This is a new footnote, stop concatenating
                            break
                        else:
                            # This is continuation text, concatenate it
                            current_footnote[content_type] += ' ' + next_text.strip()
                            keys_to_remove.append(next_key)
                            lookahead_count += 1
                            j += 1
                    else:
                        # Not a text item, stop looking ahead
                        break
                
                footnotes.append(current_footnote)
                matched = True
                # Skip past the items we just processed
                i = j
                continue
        
        # If this item didn't match, stop collecting
        if not matched:
            break
        
        i += 1
    
    # Add footnotes to the table if any were collected
    if footnotes:
        parent_contents[table_key]['table']['footnotes'] = footnotes
        
        # Remove the footnote items from parent_contents
        for key in keys_to_remove:
            del parent_contents[key]

        return keys_to_remove
    
def apply_table_annotations(obj, rules, parent=None, parent_key=None):
    if isinstance(obj, dict):
        # Check if this dict contains a table
        if 'table' in obj and parent is not None and parent_key is not None:
            # This is a content item with a table - collect annotations in order
            
            # 1. Collect preamble (if configured)
            if "preamble" in rules:
                collect_table_preamble(parent, parent_key, rules["preamble"])
            
            # 2. Collect footnotes (if configured)
            footnote_keys = []
            if "footnotes" in rules:
                footnote_regex = rules["footnotes"]["regex"]
                check_next_n = rules["footnotes"].get("check_next_n_lines", 2)  # Default to 2
                footnote_keys = collect_table_footnotes(parent, parent_key, footnote_regex, check_next_n)
            
            # 3. Collect postamble (if configured)
            if "postamble" in rules:
                collect_table_postamble(parent, parent_key, rules["postamble"], footnote_keys)
        else:
            # Recurse into nested structures
            for key, value in list(obj.items()):  # Use list() to avoid modification during iteration
                if key == 'contents' and isinstance(value, dict):
                    # This is a contents dictionary - recurse with it as parent
                    for content_key, content_value in list(value.items()):
                        apply_table_annotations(content_value, rules, value, content_key)
                else:
                    apply_table_annotations(value, rules, obj, key)
    elif isinstance(obj, list):
        for item in obj:
            apply_table_annotations(item, rules, None, None)

def collect_table_preamble(parent_contents, table_key, preamble_config):
    """
    Collect content that comes before a table and move it into the table's preamble array.
    
    Args:
        parent_contents: The contents dictionary containing the table
        table_key: The key/index of the table in parent_contents
        preamble_config: Config dict with collection rules (e.g., {"lines": 3})
    
    Returns:
        None (modifies parent_contents in place)
    """
    # Get number of lines to collect
    num_lines = preamble_config.get("lines", 0)
    if num_lines <= 0:
        return
    
    # Get all keys sorted numerically
    try:
        sorted_keys = sorted(parent_contents.keys(), key=lambda x: int(x) if str(x).lstrip('-').isdigit() else float('inf'))
    except:
        sorted_keys = sorted(parent_contents.keys())
    
    # Find the index of our table
    try:
        table_index = sorted_keys.index(table_key)
    except ValueError:
        return  # Table key not found
    
    # Collect preamble from previous items (backwards)
    preamble = []
    keys_to_remove = []
    
    for i in range(table_index - 1, -1, -1):  # Walk backwards
        if len(preamble) >= num_lines:
            break
            
        key = sorted_keys[i]
        item = parent_contents[key]
        
        # Only collect text and textsmall items
        if isinstance(item, dict):
            if 'text' in item:
                preamble.insert(0, {'text': item['text']})  # Insert at front to maintain order
                keys_to_remove.append(key)
            elif 'textsmall' in item:
                preamble.insert(0, {'textsmall': item['textsmall']})
                keys_to_remove.append(key)
            else:
                # Hit non-text content (table, image, section), stop
                break
        else:
            # Hit non-dict item, stop
            break
    
    # Add preamble to the table if any were collected
    if preamble:
        parent_contents[table_key]['table']['preamble'] = preamble
        
        # Remove the preamble items from parent_contents
        for key in keys_to_remove:
            del parent_contents[key]


def collect_table_postamble(parent_contents, table_key, postamble_config, footnote_keys):
    """
    Collect content that comes after a table's footnotes and move it into the table's postamble array.
    
    Args:
        parent_contents: The contents dictionary containing the table
        table_key: The key/index of the table in parent_contents
        postamble_config: Config dict with collection rules (e.g., {"lines": 2})
        footnote_keys: List of keys used by footnotes (to skip over them)
    
    Returns:
        None (modifies parent_contents in place)
    """
    # Get number of lines to collect
    num_lines = postamble_config.get("lines", 0)
    if num_lines <= 0:
        return
    
    # Get all keys sorted numerically
    try:
        sorted_keys = sorted(parent_contents.keys(), key=lambda x: int(x) if str(x).lstrip('-').isdigit() else float('inf'))
    except:
        sorted_keys = sorted(parent_contents.keys())
    
    # Find the index of our table
    try:
        table_index = sorted_keys.index(table_key)
    except ValueError:
        return  # Table key not found
    
    # Find where to start collecting (after footnotes if they exist)
    start_index = table_index + 1
    if footnote_keys:
        # Find the highest footnote key index
        footnote_indices = [sorted_keys.index(fk) for fk in footnote_keys if fk in sorted_keys]
        if footnote_indices:
            start_index = max(footnote_indices) + 1
    
    # Collect postamble from subsequent items
    postamble = []
    keys_to_remove = []
    
    for i in range(start_index, len(sorted_keys)):
        if len(postamble) >= num_lines:
            break
            
        key = sorted_keys[i]
        item = parent_contents[key]
        
        # Only collect text and textsmall items
        if isinstance(item, dict):
            if 'text' in item:
                postamble.append({'text': item['text']})
                keys_to_remove.append(key)
            elif 'textsmall' in item:
                postamble.append({'textsmall': item['textsmall']})
                keys_to_remove.append(key)
            else:
                # Hit non-text content (table, image, section), stop
                break
        else:
            # Hit non-dict item, stop
            break
    
    # Add postamble to the table if any were collected
    if postamble:
        parent_contents[table_key]['table']['postamble'] = postamble
        
        # Remove the postamble items from parent_contents
        for key in keys_to_remove:
            del parent_contents[key]

def remove_single_row_tables(obj, parent=None, parent_key=None):
    """
    Recursively walk through document and convert single-row tables to text.
    
    Args:
        obj: Current object being processed
        parent: Parent object (for tracking)
        parent_key: Key in parent object (for tracking)
    """
    if isinstance(obj, dict):
        # Check if this dict contains a single-row table
        if 'table' in obj and parent is not None and parent_key is not None:
            table_data = obj['table']['data']
            
            # Check if single row
            if len(table_data) == 1:
                # Convert the single row to text instructions
                row = table_data[0]
                
                # Combine all cells into one text string (space-separated)
                text_parts = []
                for cell in row:
                    if isinstance(cell, dict) and 'text' in cell:
                        text_parts.append(cell['text'])
                    elif isinstance(cell, str):
                        text_parts.append(cell)
                
                combined_text = ' '.join(text_parts)
                
                # Replace the table with a text entry in parent
                del parent[parent_key]
                parent[parent_key] = {'text': combined_text}
        else:
            # Recurse into nested structures
            for key, value in list(obj.items()):
                if key == 'contents' and isinstance(value, dict):
                    # This is a contents dictionary - recurse with it as parent
                    for content_key, content_value in list(value.items()):
                        remove_single_row_tables(content_value, value, content_key)
                else:
                    remove_single_row_tables(value, obj, key)
    elif isinstance(obj, list):
        for item in obj:
            remove_single_row_tables(item, None, None)
EMPTY_CHARS = ' \t\n\r\xa0'
EMPTY_TABLE_CHARS = ['', '–', '-']
LEFT_TABLE_CHARS = ['$','(']
RIGHT_TABLE_CHARS = [')','%']

# ============================================================================
# TABLE PROCESSING FUNCTIONS (moved from HTML parser)
# ============================================================================

def is_subset(items1, items2, empty_chars):
    """returns true if items1 is a subset of items2"""
    return all(item1.get('text', '') in empty_chars or item1.get('text', '') == item2.get('text', '') for item1, item2 in zip(items1, items2))

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
                # Create new text cell preserving other attributes
                new_cell = {k: v for k, v in cell.items() if k != 'image'}
                new_cell['text'] = f'[IMAGE: {src}]'
                table[row_idx][col_idx] = new_cell
    return table

def remove_empty_rows_from_table(table):
    """Remove rows where all cells contain only EMPTY_TABLE_CHARS"""
    empty_chars = EMPTY_TABLE_CHARS
    table = [row for row in table if any(
        (cell.get('text', '') not in empty_chars)
        for cell in row
    )]
    return table

def remove_empty_columns_from_table(table):
    """Remove columns where all cells contain only EMPTY_TABLE_CHARS"""
    if table and table[0]:
        empty_chars = EMPTY_TABLE_CHARS
        keep_cols = [j for j in range(len(table[0])) if any(
            (table[i][j].get('text', '') not in empty_chars)
            for i in range(len(table))
        )]
        table = [[row[j] for j in keep_cols] for row in table]
    return table

def apply_table_postprocessing(table, rules):
    """Apply table postprocessing rules in order"""
    if not rules:
        return table, "cleaned"
    
    cleaning_status = "cleaned"
    
    # Validate structure
    if rules.get("validate_structure", False):
        table, status = validate_table_structure(table)
        if status == "dirty":
            cleaning_status = "dirty"
    
    # Merge formatting characters
    if rules.get("merge_formatting_chars", False):
        table = merge_table_formatting(table)
    
    # Convert images to text
    if rules.get("convert_images_to_text", False):
        table = convert_images_to_text_in_table(table)
    
    # Remove empty rows
    if rules.get("remove_empty_rows", False):
        table = remove_empty_rows_from_table(table)
    
    # Remove empty columns
    if rules.get("remove_empty_columns", False):
        table = remove_empty_columns_from_table(table)
    
    # Remove subset rows
    if rules.get("remove_subset_rows_bottom_to_top", False):
        table = remove_subset_rows(table, EMPTY_TABLE_CHARS, "bottom_to_top")
    
    if rules.get("remove_subset_rows_top_to_bottom", False):
        table = remove_subset_rows(table, EMPTY_TABLE_CHARS, "top_to_bottom")
    
    # Remove subset columns
    if rules.get("remove_subset_columns_left_to_right", False):
        table = remove_subset_columns(table, EMPTY_TABLE_CHARS, "left_to_right")
    
    if rules.get("remove_subset_columns_right_to_left", False):
        table = remove_subset_columns(table, EMPTY_TABLE_CHARS, "right_to_left")
    
    return table, cleaning_status

def walk_and_process_tables(obj, rules):
    """Recursively walk through document and apply table postprocessing"""
    if isinstance(obj, dict):
        if 'table' in obj:
            # Found a table - apply postprocessing
            table = obj['table']
            processed_table, status = apply_table_postprocessing(table, rules)
            obj['table'] = processed_table
            # Optionally add status
            if rules.get("apply_cleaning_status", False):
                obj['cleaned'] = (status == "cleaned")
        else:
            # Recurse into nested structures
            for value in obj.values():
                walk_and_process_tables(value, rules)
    elif isinstance(obj, list):
        for item in obj:
            walk_and_process_tables(item, rules)
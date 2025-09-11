import re

# params 
tag_groups = {
"bold": ["b", "strong"],
"italic": ["i", "em"],
"underline": ["u", "ins"],
}

EMPTY_CHARS = ' \t\n\r\xa0'
EMPTY_TABLE_CHARS = ['', '–', '-']
LEFT_TABLE_CHARS = ['$','(']
RIGHT_TABLE_CHARS = [')','%']

def remove_leading_empty_instructions(instructions):
   """Remove leading empty/whitespace-only instructions from the list"""
   if not instructions:
       return instructions
   
   # Find the first non-empty instruction
   first_meaningful_index = 0
   for i, instruction in enumerate(instructions):
       # Skip non-text instructions (tables, images are meaningful content)
       if 'image' in instruction or 'table' in instruction:
           first_meaningful_index = i
           break
       
       # Check if text instruction has meaningful content
       if 'text' in instruction:
           text = instruction['text'].strip(EMPTY_CHARS)
           if text:  # Non-empty after stripping
               first_meaningful_index = i
               break
   else:
       # If we get here, all instructions were empty text or whitespace-only
       return []
   
   # Return sliced list starting from first meaningful instruction
   return instructions[first_meaningful_index:]

def is_empty_instructions(instructions):
    """Check if an instruction block contains only whitespace/empty content"""
    if not instructions:
        return True
    
    for instruction in instructions:
        # Skip non-text instructions (tables, images are meaningful content)
        if 'image' in instruction or 'table' in instruction:
            return False
        
        # Check if text instruction has meaningful content
        if 'text' in instruction:
            text = instruction['text'].strip(EMPTY_CHARS)
            if text:  # Non-empty after stripping
                return False
    
    # All instructions were either empty text or whitespace-only
    return True

# utils
def walk(node):
    yield ("start",node)
    for child in node.iter(include_text=True):
        yield from walk(child)

    yield ("end",node)

def check_text_style(text):
    if not text or not text.strip():
        return {}
    
    styles = {}
    
    if text.isupper():
        styles['all_caps'] = True
    else:
        # Stop words that can be lowercase in proper case
        stop_words = r'\b(and|or|of|the|in|on|at|to|for|with|by|a|an)\b'
        
        # Replace stop words with placeholder, check if remaining words are proper case
        text_no_stops = re.sub(stop_words, 'STOP', text, flags=re.IGNORECASE)
        
        # Check if all non-stop words start with capital and have at least one capital
        if re.match(r'^[A-Z][a-zA-Z]*(\s+(STOP|[A-Z][a-zA-Z]*))*$', text_no_stops) and re.search(r'[A-Z]', text):
            styles['proper_case'] = True
    
    return styles


def style_to_dict(style_string):
    result = {}
    if not style_string:
        return result
    # send to lower case
    style_string = style_string.lower()
    style_list = [attr.strip(EMPTY_CHARS) for attr in style_string.split(';') if attr.strip(EMPTY_CHARS)]

    for item in style_list:
        if ':' in item:
            key, value = item.split(':', 1)
            result[key.strip(EMPTY_CHARS)] = value.strip(EMPTY_CHARS)
    return result


def parse_font_shorthand(font_value):
    """
    Parse CSS font shorthand property into individual components.
    
    Font shorthand syntax: [font-style] [font-variant] [font-weight] font-size [/line-height] font-family
    Required: font-size and font-family
    Optional (in order): font-style, font-variant, font-weight, line-height
    
    Examples:
    - "bold 10pt Times New Roman" -> {'font-weight': 'bold', 'font-size': '10pt', 'font-family': 'Times New Roman'}
    - "italic bold 12px Arial" -> {'font-style': 'italic', 'font-weight': 'bold', 'font-size': '12px', 'font-family': 'Arial'}
    """
    if not font_value:
        return {}
    
    # Clean and split the font value
    parts = font_value.strip().split()
    if len(parts) < 2:  # Must have at least font-size and font-family
        return {}
    
    result = {}
    i = 0
    
    # Parse optional properties in order: font-style, font-variant, font-weight
    
    # Check for font-style (italic, oblique, normal)
    if i < len(parts) and parts[i].lower() in ['italic', 'oblique', 'normal']:
        if parts[i].lower() == 'italic':
            result['font-style'] = 'italic'
        i += 1
    
    # Check for font-variant (small-caps, normal) - we'll skip this for now
    if i < len(parts) and parts[i].lower() in ['small-caps', 'normal']:
        # Skip font-variant for now since we don't handle it
        i += 1
    
    # Check for font-weight (bold, normal, 100-900, lighter, bolder)
    if i < len(parts):
        weight = parts[i].lower()
        if weight in ['bold', '700']:
            result['font-weight'] = 'bold'
            i += 1
        elif weight in ['normal', '400']:
            result['font-weight'] = 'normal'
            i += 1
        elif weight in ['100', '200', '300', '500', '600', '800', '900', 'lighter', 'bolder']:
            result['font-weight'] = weight
            i += 1
    
    # Next must be font-size (required)
    if i < len(parts):
        size_part = parts[i]
        # Handle font-size/line-height format (e.g., "12px/1.5")
        if '/' in size_part:
            size, line_height = size_part.split('/', 1)
            result['font-size'] = size
            result['line-height'] = line_height
        else:
            result['font-size'] = size_part
        i += 1
    
    # Remaining parts are font-family (required)
    if i < len(parts):
        # Join remaining parts for font family (handles "Times New Roman" etc.)
        font_family = ' '.join(parts[i:])
        # Remove quotes if present
        font_family = font_family.strip('\'"')
        result['font-family'] = font_family
    
    return result

def get_style(node):
    increments = []
    stacks = []
    style = node.attributes.get('style', '')
    style_dict = style_to_dict(style)

    # Parse font shorthand if present
    if 'font' in style_dict:
        font_properties = parse_font_shorthand(style_dict['font'])
        # Merge parsed properties into style_dict
        style_dict.update(font_properties)

    if 'font-weight' in style_dict:
        if style_dict['font-weight'] == 'bold':
            increments.append('bold')
        elif style_dict['font-weight'] == '700':
            increments.append('bold')

    if 'font-style' in style_dict:
        if style_dict['font-style'] == 'italic':
            increments.append('italic')
    
    if 'text-decoration' in style_dict:
        if style_dict['text-decoration'] == 'underline':
            increments.append('underline')    

    if 'text-align' in style_dict:
        if style_dict['text-align'] == 'center':
            increments.append('text-center')

        
    left_indent = 0

    if 'font-size' in style_dict:
        font_size = style_dict['font-size']
        font_size = normalize_to_px(font_size)
        stacks.append({'font-size': font_size})
    
    if 'text-indent' in style_dict:
        indent = style_dict['text-indent']
        indent = normalize_to_px(indent)
        left_indent += indent

    if 'padding' in style_dict:
        padding_value = style_dict['padding']
        # Handle four-value format: top right bottom left
        if padding_value.count(' ') == 3:
            _, _, _, left = padding_value.split(' ')
            left = normalize_to_px(left)
            left_indent += left
        # Handle three-value format: top right/left bottom
        elif padding_value.count(' ') == 2:
            _, right_left, _ = padding_value.split(' ')
            right_left = normalize_to_px(right_left)
            left_indent += right_left
        # Handle two-value format: top/bottom right/left
        elif padding_value.count(' ') == 1:
            _, right_left = padding_value.split(' ')
            right_left = normalize_to_px(right_left)
            left_indent += right_left
        # Handle single-value format: all sides
        else:
            padding_value = normalize_to_px(padding_value)
            left_indent += padding_value

    # Also handle direct padding-left if specified
    if 'padding-left' in style_dict:
        padding_left = style_dict['padding-left']
        padding_left = normalize_to_px(padding_left)
        left_indent += padding_left

    # Handle margin with the same logic as padding
    if 'margin' in style_dict:
        margin_value = style_dict['margin']
        # Handle four-value format: top right bottom left
        if margin_value.count(' ') == 3:
            _, _, _, left = margin_value.split(' ')
            left = normalize_to_px(left)
            left_indent += left
        # Handle three-value format: top right/left bottom
        elif margin_value.count(' ') == 2:
            _, right_left, _ = margin_value.split(' ')
            right_left = normalize_to_px(right_left)
            left_indent += right_left
        # Handle two-value format: top/bottom right/left
        elif margin_value.count(' ') == 1:
            _, right_left = margin_value.split(' ')
            right_left = normalize_to_px(right_left)
            left_indent += right_left
        # Handle single-value format: all sides
        else:
            margin_value = normalize_to_px(margin_value)
            left_indent += margin_value

    # Handle direct margin-left if specified
    if 'margin-left' in style_dict:
        margin_left = style_dict['margin-left']
        margin_left = normalize_to_px(margin_left)
        left_indent += margin_left

    if 'display' in style_dict:
        if style_dict['display'] == 'none':
            increments.append('display-none')

    if left_indent != 0:
        stacks.append({'left-indent': str(left_indent)})    
    return increments, stacks

def parse_css_value(value_str):
    """Extract numeric value and unit from CSS value string"""
    if not value_str or not isinstance(value_str, str):
        return 0, 'px'
    
    value_str = value_str.strip(EMPTY_CHARS)
    
    # Handle non-numeric values
    if value_str in ['auto', 'inherit', 'initial']:
        return 0, value_str
    
    # Find where the number ends
    numeric_part = ''
    for i, char in enumerate(value_str):
        if char.isdigit() or char == '.':
            numeric_part += char
        elif char == '-' and i == 0:  # Handle negative values
            numeric_part += char
        else:
            unit = value_str[i:].strip(EMPTY_CHARS)
            break
    else:
        unit = 'px'  # Default if no unit specified
    
    # Convert numeric part to float
    try:
        value = float(numeric_part) if numeric_part else 0
    except ValueError:
        value = 0
    
    return value, unit


def normalize_to_px(value_str, font_context=None):
    """Convert any CSS measurement to pixels based on context"""
    if not value_str:
        return 0
    
    # Parse the value
    value, unit = parse_css_value(value_str)
    
    # Early return for non-numeric values
    if unit in ['auto', 'inherit', 'initial']:
        return 0
    
    # Get font context in pixels
    current_font_size = 16  # Default
    if font_context:
        font_value, font_unit = parse_css_value(font_context)
        if font_unit == 'px':
            current_font_size = font_value
        elif font_unit == 'pt':
            current_font_size = font_value * 1.333
        else:
            # For simplicity, treat all other units as approximately 16px
            current_font_size = font_value * 16 if font_value else 16
    
    # Convert to pixels
    if unit == 'px':
        return value
    elif unit == 'pt':
        return value * 1.333
    elif unit == 'em':
        return value * current_font_size
    elif unit == 'rem':
        return value * 16  # Root em always based on root font size
    elif unit == '%':
        return value * current_font_size / 100  # % of font size
    elif unit == 'ex':
        return value * current_font_size / 2  # Roughly half the font size
    elif unit == 'ch':
        return value * current_font_size * 0.5  # Approximate character width
    elif unit in ['vh', 'vw', 'vmin', 'vmax']:
        return value  # Cannot accurately convert viewport units without screen size
    elif unit == 'cm':
        return value * 37.8  # Approximate for screen (96dpi)
    elif unit == 'mm':
        return value * 3.78  # 1/10th of cm
    elif unit == 'in':
        return value * 96  # Standard 96dpi
    elif unit == 'pc':
        return value * 16  # 1pc = 12pt
    else:
        return value  # Unknown unit, return as is

def safe_increment(dct,key):
    if key not in dct:
        dct[key] = 0

    dct[key] += 1

def safe_decrement(dct,key):
    if key not in dct:
        dct[key] = 0

    dct[key] -= 1
    if dct[key] < 0:
        dct[key] = 0

def safe_stack(dct,key,val):
    if key not in dct:
        dct[key] = []

    dct[key].append(val)

def safe_unstack(dct,key):
    if key not in dct:
        dct[key] = []

    if len(dct[key]) > 0:
        dct[key].pop()
    else:
        dct[key] = []

def parse_start_style(current_attributes,node):
    increments, stacks = get_style(node)
    if 'display-none' in increments:
        return 'skip'

    for key in increments:
        safe_increment(current_attributes,key)

    for stack in stacks:
        for key in stack:
            safe_stack(current_attributes,key,stack[key])

    return ''
def parse_end_style(current_attributes,node):
    increments,stacks = get_style(node)
    if 'display-none' in increments:
        return 'skip'
    
    for key in increments:
        safe_decrement(current_attributes,key)

    for stack in stacks:
        for key in stack:
            safe_unstack(current_attributes,key)

    return ''

def parse_start_tag(current_attributes,node):
    tag = node.tag

    if tag == 'table':
        return 'table'
    elif tag == '-text':
        return 'text'
    elif tag == 'a':
        href = node.attributes.get('href', '')
        safe_stack(current_attributes, 'href', href)
        return ''
    elif tag == 'img':
        return 'image'

    for tag in tag_groups:
        if node.tag in tag_groups[tag]:
            safe_increment(current_attributes,tag)
            return ''
        
def parse_end_tag(current_attributes,node):
    tag = node.tag

    if tag == 'table':
        return 'table'
    elif tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li','br']:
        return 'newline'
    elif tag == 'a':
        safe_unstack(current_attributes, 'href')
        return ''

    for tag in tag_groups:
        if node.tag in tag_groups[tag]:
            safe_decrement(current_attributes,tag)
            return ''

# USED AI BC LAZY #
def merge_instructions(instructions):
    if not instructions or len(instructions) <= 1:
        return instructions
    
    result = [instructions[0]]
    
    for i in range(1, len(instructions)):
        current = instructions[i]
        prev = result[-1]
        
        # Skip merging if either instruction is an image
        if 'image' in current or 'image' in prev:
            result.append(current)
            continue
        
        # Case 1: Empty string after strip
        if current.get('text', '').strip(EMPTY_CHARS) == '':
            prev['text'] += current.get('text', '')
            continue
        
        # Case 2: Attributes match with previous
        attrs_to_check = ['bold', 'text-center', 'italic', 'underline', 'font-size']
        attrs_match = all(current.get(attr) == prev.get(attr) for attr in attrs_to_check)
        
        if attrs_match:
            prev['text'] += current.get('text', '')
            continue
        
        # Case 3: Check if attributes match with any earlier instruction
        # This handles the case where instructions a and c match but b doesn't
        merged = False
        for j in range(len(result) - 1, -1, -1):  # Check all previous instructions
            earlier = result[j]
            if 'image' not in earlier and all(current.get(attr) == earlier.get(attr) for attr in attrs_to_check):
                # Combine all instructions from j to the current one
                combined_text = earlier['text']
                for k in range(j + 1, len(result)):
                    if 'text' in result[k]:
                        combined_text += result[k].get('text', '')
                combined_text += current.get('text', '')
                
                earlier['text'] = combined_text
                # Remove the instructions that were merged
                result = result[:j+1]
                merged = True
                break
        
        if not merged:
            result.append(current)
    
    return result
# USED AI BC LAZY #

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


def merge_cell_instructions(instructions):
    """
    Merge all text from cell instructions into a single instruction.
    Discard images, concatenate all text, collect ALL attributes from ALL instructions.
    For boolean attributes (bold, italic, etc.), if ANY instruction has it, the result has it.
    For list attributes (font-size, href, etc.), use the last non-empty value.
    """
    if not instructions:
        return {'text': ''}
    
    # Collect all text and all attributes
    combined_text = ''
    all_attributes = {}
    
    for instruction in instructions:
        # Skip images completely
        if 'image' in instruction:
            continue
            
        # Add any text content
        if 'text' in instruction:
            combined_text += instruction['text']
        
        # Collect all attributes except 'text'
        for key, value in instruction.items():
            if key == 'text':
                continue
                
            if key not in all_attributes:
                all_attributes[key] = []
            all_attributes[key].append(value)
    
    # Create final cell instruction
    result = {'text': combined_text}
    
    # Process collected attributes
    for key, values in all_attributes.items():
        # Remove None/empty values
        non_empty_values = [v for v in values if v is not None and v != '']
        
        if not non_empty_values:
            continue
            
        # For boolean attributes (True/False), if ANY instruction has True, result is True
        if all(isinstance(v, bool) for v in non_empty_values):
            result[key] = any(non_empty_values)
        
        # For numeric attributes, use the last value
        elif all(isinstance(v, (int, float)) for v in non_empty_values):
            result[key] = non_empty_values[-1]
        
        # For string attributes, use the last non-empty value
        else:
            result[key] = non_empty_values[-1]
    
    return result

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

def clean_table(table):
    if len(table) == 0:
        return table, "dirty"
    
    # First check if table has same number of columns
    same_length = all([len(row) == len(table[0]) for row in table])
    if not same_length:
        return table, "dirty"
    
    # NEW: Table detection - single row tables are likely formatting, not data
    if len(table) == 1:
        return table, "not_table"
    
    # Merge formatting characters with adjacent content
    table = merge_table_formatting(table)
    
    # Convert image cells to text cells with [IMAGE: {src}] format
    for row_idx, row in enumerate(table):
        for col_idx, cell in enumerate(row):
            if 'image' in cell:
                src = cell['image'].get('src', '')
                # Create new text cell preserving other attributes
                new_cell = {k: v for k, v in cell.items() if k != 'image'}
                new_cell['text'] = f'[IMAGE: {src}]'
                table[row_idx][col_idx] = new_cell
    
    empty_chars = EMPTY_TABLE_CHARS
    
    # Remove empty rows - now only need to check text since all images are converted
    table = [row for row in table if any(
        (cell.get('text', '') not in empty_chars)
        for cell in row
    )]
    
    # Remove empty columns - now only need to check text since all images are converted
    if table and table[0]:
        keep_cols = [j for j in range(len(table[0])) if any(
            (table[i][j].get('text', '') not in empty_chars)
            for i in range(len(table))
        )]
        table = [[row[j] for j in keep_cols] for row in table]

    # Remove subset rows and columns
    table = remove_subset_rows(table, empty_chars, "bottom_to_top")
    table = remove_subset_rows(table, empty_chars, "top_to_bottom")
    table = remove_subset_columns(table, empty_chars, "left_to_right")
    table = remove_subset_columns(table, empty_chars, "right_to_left")
    
    return table, "cleaned"

# TODO, not sure how it handles ragged tables... e.g. td are not same length in rows
def convert_html_to_instructions(root):
    skip_node = False
    in_table = False
    in_cell = False

    instructions_list = []
    instructions = []
    current_attributes = {}

    # Dictionary-based approach for table cells
    table_cells = {}
    max_row = -1
    max_col = -1
    occupied_positions = set()
    current_cell_instructions = []

    # table
    row_id = 0
    col_id = 0
    rowspan = 1
    colspan = 1

    for signal, node in walk(root):
        if signal == "start":
            # skip invisible elements
            if skip_node:
                continue
            elif in_table and node.tag in ['td', 'th']:
                in_cell = True
                colspan = int(node.attributes.get('colspan', 1))
                rowspan = int(node.attributes.get('rowspan', 1))
                current_cell_instructions = []
            elif in_table and node.tag == 'tr':
                pass
            
            style_command = parse_start_style(current_attributes, node)
            if style_command == 'skip':
                skip_node = True
                continue

            tag_command = parse_start_tag(current_attributes, node)
            if tag_command == 'table':
                in_table = True
                # Reset table variables
                table_cells = {}
                max_row = -1
                max_col = -1
                occupied_positions = set()
                row_id = 0
                col_id = 0
                if len(instructions) > 0:
                    if not is_empty_instructions(instructions):  
                        instructions_list.append(instructions)
                    instructions = []
                continue
            elif tag_command == 'text':
                text = node.text_content

                # check not leading whitespace 
                if len(instructions) == 0:
                    text = text
                    if len(text) == 0:
                        continue
            
                instruction = {'text': text}

                text_styles = check_text_style(text)
                instruction.update(text_styles)

                for key in current_attributes:
                    val = current_attributes[key]
                    if isinstance(val, list):
                        if len(val) > 0:
                            instruction[key] = val[-1]
                    elif isinstance(val, int):
                        if val > 0:
                            instruction[key] = True

                # Redirect instruction output based on context
                if in_cell:
                    current_cell_instructions.append(instruction)
                else:
                    instructions.append(instruction)
            elif tag_command == 'image':
                src = node.attributes.get('src', '')
                alt = node.attributes.get('alt', '')
                
                instruction = {'image': {'src': src, 'alt': alt}}
                
                for key in current_attributes:
                    val = current_attributes[key]
                    if isinstance(val, list):
                        if len(val) > 0:
                            instruction[key] = val[-1]
                    elif isinstance(val, int):
                        if val > 0:
                            instruction[key] = True

                # Redirect instruction output based on context
                if in_cell:
                    current_cell_instructions.append(instruction)
                else:
                    instructions.append(instruction)

        elif signal == "end":
            style_command = parse_end_style(current_attributes, node)
            if style_command == 'skip':
                skip_node = False
                continue

            tag_command = parse_end_tag(current_attributes, node)
            if tag_command == 'table':

                # Create a properly sized matrix from the collected data
                if max_row >= 0 and max_col >= 0:  # Only if we have cells
                    matrix = [[{'text': ''} for _ in range(max_col + 1)] for _ in range(max_row + 1)]

                    
                    # Fill in the cells
                    for (r, c), cell_data in table_cells.items():
                            if 'text' in cell_data:
                                # Create a copy and strip the text
                                cleaned_cell = cell_data.copy()
                                cleaned_cell['text'] = cell_data['text'].strip(EMPTY_CHARS)
                                matrix[r][c] = cleaned_cell
                            else:
                                matrix[r][c] = cell_data


                    # clean the matrix
                    matrix,cleaning_status = clean_table(matrix)
                    if cleaning_status == "not_table":
                        # Combine all cells into one instruction block (same line)
                        all_cells = []
                        for cell in matrix[0]:
                            if 'text' in cell and cell['text'].strip(EMPTY_CHARS):
                                all_cells.append(cell)
                        if all_cells:
                            instructions_list.append(all_cells)  # One block = One line
                    elif len(matrix) == 1:
                        # Fallback for other single-row cases that somehow didn't get caught
                        cell_texts = []
                        for cell in matrix[0]:
                            if 'image' in cell:
                                cell_texts.append(f"[Image: {cell['image'].get('alt', 'No alt text')}]")
                            else:
                                cell_texts.append(cell.get('text', ''))
                        matrix_text = ' '.join(cell_texts)
                        instructions_list.append([{'text': matrix_text, 'fake_table': True}])
                    else:
                        # Multi-row table (cleaned or dirty)
                        instructions_list.append([{'table': matrix, 'cleaned': cleaning_status == "cleaned"}])

                
                # Reset table state
                table_cells = {}
                occupied_positions = set()
                current_cell_instructions = []
                in_table = False
                continue
            elif in_table:
                if node.tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'br']:
                    # Add newline to current cell if we're in a cell
                    if in_cell:
                        if current_cell_instructions:
                            last_instruction = current_cell_instructions[-1]
                            if 'text' in last_instruction:
                                last_instruction['text'] += '\n'
                elif node.tag == 'tr':
                    row_id += 1
                    col_id = 0
                elif node.tag in ['td', 'th']:
                    # Process accumulated cell instructions
                    if current_cell_instructions:
                        cell_data = merge_cell_instructions(current_cell_instructions)

                    else:
                        cell_data = {'text': ''}
                    
                    # Find next available position if current is occupied
                    while (row_id, col_id) in occupied_positions:
                        col_id += 1
                    
                    # Store the cell_data at EVERY position this cell occupies
                    for y in range(rowspan):
                        for x in range(colspan):
                            # Store cell data at this position
                            table_cells[(row_id + y, col_id + x)] = cell_data
                            # Mark position as occupied
                            occupied_positions.add((row_id + y, col_id + x))
                    
                    # Update maximum dimensions
                    max_row = max(max_row, row_id + rowspan - 1)
                    max_col = max(max_col, col_id + colspan - 1)
                    
                    # Move to next position
                    col_id += colspan
                    current_cell_instructions = []
                    in_cell = False

            elif tag_command == 'newline':
                if len(instructions) > 0:
                    instructions = remove_leading_empty_instructions(instructions)
                    instructions = merge_instructions(instructions)
                    if len(instructions) == 1:
                        # strip text if it's a text instruction
                        if 'text' in instructions[0]:
                            instructions[0]['text'] = instructions[0]['text'].strip(EMPTY_CHARS)
                    if not is_empty_instructions(instructions): 
                        instructions_list.append(instructions)
                    instructions = []
                continue

    # add any remaining instructions
    if instructions:
        if len(instructions) > 0:
            instructions = remove_leading_empty_instructions(instructions)
            if len(instructions) == 1:
                # strip text if it's a text instruction
                if 'text' in instructions[0]:
                    instructions[0]['text'] = instructions[0]['text'].strip(EMPTY_CHARS)
            if not is_empty_instructions(instructions): 
                instructions_list.append(instructions)
    return instructions_list
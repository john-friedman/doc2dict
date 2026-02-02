import re

def _clean_cell_content(cell_content):

    text = str(cell_content)
    
    # Replace non-breaking space
    text = text.replace('\u00a0', '')
    
    # Replace tabs with spaces
    text = text.replace('\t', ' ')
    
    # Replace multiple newlines with single spaces
    text = text.replace('\n\n', ' ')
    text = text.replace('\n', ' ')
    
    # Replace multiple spaces with single spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def _format_table(table_data):
    if not table_data:
        return []
    
    # Clean all cell content first
    cleaned_data = []
    for row in table_data:
        cleaned_row = [_clean_cell_content(cell) for cell in row]
        cleaned_data.append(cleaned_row)
    
    # Calculate column widths using cleaned data
    col_widths = []
    for row in cleaned_data:
        for i, cell in enumerate(row):
            cell_len = len(cell)
            if i >= len(col_widths):
                col_widths.append(cell_len)
            else:
                col_widths[i] = max(col_widths[i], cell_len)
    
    formatted_rows = []
    formatted_rows.append('')  # Empty line before table
    
    for i, row in enumerate(cleaned_data):
        padded_cells = [cell.ljust(col_widths[j]) for j, cell in enumerate(row)]
        formatted_rows.append('| ' + ' | '.join(padded_cells) + ' |')
        
        # Add separator after first row (header)
        if i == 0:
            separator = '|' + '|'.join('-' * (w + 2) for w in col_widths) + '|'
            formatted_rows.append(separator)
    
    formatted_rows.append('')  # Empty line after table
    return formatted_rows


def _format_title(text, level):
    # Ensure level is at least 1 for proper markdown heading
    markdown_level = max(1, min(level + 1, 6))
    return "#" * markdown_level + " " + text


def convert_dict_to_data_tuples(dct):
    result = []
    
    def process_content(content, current_id=None, level=0):
        if not isinstance(content, dict):
            return
        
        # Get the class and standardized_title if they exist
        content_class = content.get('class', None)
        standardized_title = content.get('standardized_title', None)
            
        # Process title, text, textsmall directly
        for key in ['title', 'text', 'textsmall']:
            if key in content:
                result.append((current_id, key, content[key], level, content_class, standardized_title))
        
        # Process table - flatten all components into separate tuples
        if 'table' in content:
            table_dict = content['table']

            if 'title' in table_dict and table_dict['title'] is not None:
                result.append((current_id, 'table_title', table_dict['title'], level, content_class, standardized_title))
            
            if 'preamble' in table_dict and table_dict['preamble'] is not None:
                result.append((current_id, 'table_preamble', table_dict['preamble'], level, content_class, standardized_title))
            
            # Main table data - always include if present
            if 'data' in table_dict:
                result.append((current_id, 'table_data', table_dict['data'], level, content_class, standardized_title))
            
            # Footnotes - only add if list is not empty
            if 'footnotes' in table_dict and table_dict['footnotes']:
                result.append((current_id, 'table_footnotes', table_dict['footnotes'], level, content_class, standardized_title))
            
            # Postamble - only add if not None
            if 'postamble' in table_dict and table_dict['postamble'] is not None:
                result.append((current_id, 'table_postamble', table_dict['postamble'], level, content_class, standardized_title))
        
        # Process contents recursively in numeric order
        contents = content.get('contents', {})
        if contents:
            for key in contents.keys():
                process_content(contents[key], key, level + 1)
    
    # Start processing from document
    if 'document' in dct:
        document = dct['document']
        for key in document.keys(): 
            process_content(document[key], key, 0)
    else:
        # If no document key, process the entire dictionary
        process_content(dct, level=0)
    
    return result

# Backward compatibility alias
unnest_dict = convert_dict_to_data_tuples


def convert_data_tuples_to_dict(tuples_list, mapping_dict=None):
    """
    Convert a flat list of tuples back into a nested dictionary structure.
    
    Args:
        tuples_list: List of tuples in format (section_id, content_type, content_value, level, class, standardized_title)
        mapping_dict: Optional mapping dictionary with 'levels' key containing regex patterns
    
    Returns:
        Nested dictionary with 'document' structure
    """
    if not tuples_list:
        return {'document': {}}
    
    # Build a tree structure to track sections and their hierarchy
    sections = {}
    
    for tuple_data in tuples_list:
        section_id = tuple_data[0]
        content_type = tuple_data[1]
        content_value = tuple_data[2]
        level = tuple_data[3]
        content_class = tuple_data[4] if len(tuple_data) > 4 else None
        standardized_title = tuple_data[5] if len(tuple_data) > 5 else None
        
        # Initialize section if it doesn't exist
        if section_id not in sections:
            sections[section_id] = {
                'level': level,
                'content': {},
                'class': content_class,
                'standardized_title': standardized_title,
                'children': []
            }
        
        section = sections[section_id]
        
        # Process content types
        if content_type == 'title':
            section['content']['title'] = content_value
        elif content_type == 'text':
            section['content']['text'] = content_value
        elif content_type == 'textsmall':
            section['content']['textsmall'] = content_value
        elif content_type.startswith('table'):
            # Initialize table dict if not present
            if 'table' not in section['content']:
                section['content']['table'] = {}
            
            if content_type == 'table_title':
                section['content']['table']['title'] = content_value
            elif content_type == 'table_preamble':
                section['content']['table']['preamble'] = content_value
            elif content_type == 'table_data':
                section['content']['table']['data'] = content_value
            elif content_type == 'table_footnotes':
                section['content']['table']['footnotes'] = content_value
            elif content_type == 'table_postamble':
                section['content']['table']['postamble'] = content_value
    
    # Build hierarchy based on levels
    # Group sections by level to establish parent-child relationships
    levels_map = {}
    for section_id, section_data in sections.items():
        level = section_data['level']
        if level not in levels_map:
            levels_map[level] = []
        levels_map[level].append(section_id)
    
    # Build the nested structure
    result = {'document': {}}
    
    # Process level 0 (top-level sections)
    if 0 in levels_map:
        for section_id in levels_map[0]:
            section_dict = _build_section_dict(sections[section_id])
            
            # Find and add children recursively
            children = _find_children(section_id, sections, tuples_list)
            if children:
                section_dict['contents'] = children
            
            result['document'][section_id] = section_dict
    
    return result


def _build_section_dict(section_data):
    """
    Helper to build a section dictionary in the correct order:
    title -> standardized_title (if exists) -> class -> other content -> contents
    """
    section_dict = {}
    
    # Add fields in specific order
    if 'title' in section_data['content']:
        section_dict['title'] = section_data['content']['title']
    
    if section_data['standardized_title'] is not None:
        section_dict['standardized_title'] = section_data['standardized_title']
    
    if section_data['class'] is not None:
        section_dict['class'] = section_data['class']
    
    # Add remaining content fields (text, textsmall, table, image)
    for key in ['text', 'textsmall', 'table', 'image']:
        if key in section_data['content']:
            section_dict[key] = section_data['content'][key]
    
    return section_dict


def _find_children(parent_id, sections, tuples_list):
    """
    Helper function to find all children of a given section.
    Children are sections that appear after the parent in the tuples list
    and have a higher level, until we hit another section at the same or lower level.
    """
    parent_level = sections[parent_id]['level']
    children = {}
    
    # Find the position of the last tuple for this parent
    parent_end_idx = -1
    for idx, tuple_data in enumerate(tuples_list):
        sec_id = tuple_data[0]
        if sec_id == parent_id:
            parent_end_idx = idx
    
    # Look for potential children after this parent
    next_section_id = None
    for idx in range(parent_end_idx + 1, len(tuples_list)):
        tuple_data = tuples_list[idx]
        sec_id = tuple_data[0]
        level = tuple_data[3]
        
        # If we hit a section at same or lower level, stop
        if level <= parent_level:
            break
        
        # If this is a direct child (one level deeper)
        if level == parent_level + 1 and sec_id != next_section_id:
            next_section_id = sec_id
            child_dict = _build_section_dict(sections[sec_id])
            
            # Recursively find grandchildren
            grandchildren = _find_children(sec_id, sections, tuples_list)
            if grandchildren:
                child_dict['contents'] = grandchildren
            
            children[sec_id] = child_dict
    
    return children
def escape_markdown(text):
    """Escape markdown special characters in text."""
    if not isinstance(text, str):
        return text
    
    chars_to_escape = ['\\', '`', '*', '_', '[', ']', '(', ')', '#', '+', '-', '.', '!', '|']
    
    for char in chars_to_escape:
        text = text.replace(char, '\\' + char)
    
    return text

def flatten_dict(dct=None, format='markdown', tuples_list=None):
    if tuples_list is None:
        tuples_list = unnest_dict(dct)
    results = []

    # todo performance + apply escaping to table data
    if format == 'markdown':
        for tuple in tuples_list:
            tuple_type = tuple[1]
            content = tuple[2]
            level = tuple[3]
            
            if tuple_type == 'table_data':
                results.extend(_format_table(content))
            elif tuple_type == 'table_preamble':
                if content is not None:
                    results.append('')
                    results.append(f'*{escape_markdown(content)}*')
                    results.append('')
            elif tuple_type == 'table_footnotes':
                for footnote in content:
                    footnote_id = escape_markdown(footnote[0])
                    footnote_text = escape_markdown(footnote[1])
                    results.append(f"- **{footnote_id}**: {footnote_text}")
            elif tuple_type == 'table_postamble':
                if content is not None:
                    results.append('')
                    results.append(f'*{escape_markdown(content)}*')
                    results.append('')
            elif tuple_type == 'text':
                results.append(escape_markdown(content))
            elif tuple_type == 'textsmall':
                results.append(f'<sub>{escape_markdown(content)}</sub>')
            elif tuple_type == 'title':
                results.append(_format_title(content, level))
        
        return '\n'.join(results)
    
    elif format == 'text':
        for tuple in tuples_list:
            tuple_type = tuple[1]
            content = tuple[2]
            level = tuple[3]

            if tuple_type == 'table_data':
                results.extend(_format_table(content))
            elif tuple_type == 'table_preamble':
                if content is not None:
                    results.append('')
                    results.append(content)
                    results.append('')
            elif tuple_type == 'table_footnotes':
                for footnote in content:
                    results.append(f"{footnote[0]}: {footnote[1]}")
            elif tuple_type == 'table_postamble':
                if content is not None:
                    results.append('')
                    results.append(content)
                    results.append('')
            elif tuple_type == 'text':
                results.append(content)
            elif tuple_type == 'textsmall':
                results.append(content)
            elif tuple_type == 'title':
                results.append('')
                results.append(content)
                results.append('')

        return '\n'.join(results)
    else:
        raise ValueError(f'Format not found: {format}')
    
def convert_dict_to_columnar(dct):
    tuples_list = convert_dict_to_data_tuples(dct)
    return [
        {
            'id': t[0],
            'type': t[1],
            'content': t[2],
            'level': t[3],
            'class': t[4],
            'standardized_title': t[5]
        }
        for t in tuples_list
    ]
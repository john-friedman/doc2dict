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

def unnest_dict(dct):
    result = []
    
    def process_content(content, current_id=None, level=0):
        if not isinstance(content, dict):
            return
            
        # Process title, text, textsmall, and table directly
        for key in ['title', 'text', 'textsmall', 'table']:
            if key in content:
                # skip introduction filler
                if current_id == -1:
                    pass
                else:
                    result.append((current_id, key, content[key], level))
        
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

def flatten_dict(dct, format='markdown'):
    tuples_list = unnest_dict(dct)
    results = []
    if format == 'markdown':
        for tuple in tuples_list:
            tuple_type = tuple[1]
            content = tuple[2]
            level = tuple[3]
            if tuple_type == 'table':
                results.extend(_format_table(content))
            elif tuple_type == 'text':
                results.append(content)
            elif tuple_type == 'textsmall':
                results.append(f'<sub>{content}</sub>')
            elif tuple_type == 'title':
                results.append(_format_title(content,level))
        
        return '\n'.join(results)
    elif format == 'text':
        for tuple in tuples_list:
            tuple_type = tuple[1]
            content = tuple[2]
            level = tuple[3]

            # reuse markdown format
            if tuple_type == 'table':
                results.extend(_format_table(content))
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
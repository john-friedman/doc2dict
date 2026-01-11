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
            
        # Process title, text, textsmall directly
        for key in ['title', 'text', 'textsmall']:
            if key in content:
                # skip introduction filler
                if current_id == -1:
                    pass
                else:
                    result.append((current_id, key, content[key], level))
        
        # Process table - flatten all components into separate tuples
        if 'table' in content:
            if current_id != -1:
                table_dict = content['table']
                
                # Handle both old format (raw list) and new format (dict with 'data')
                if isinstance(table_dict, dict):
                    # New format - create separate tuples for each component
                    
                    # Preamble comes first if it exists
                    if 'preamble' in table_dict:
                        result.append((current_id, 'table_preamble', table_dict['preamble'], level))
                    
                    # Main table data
                    if 'data' in table_dict:
                        result.append((current_id, 'table_data', table_dict['data'], level))
                    
                    # Footnotes (could be a list, so add each one)
                    if 'footnotes' in table_dict:
                        footnotes = table_dict['footnotes']
                        if isinstance(footnotes, list):
                            for footnote in footnotes:
                                result.append((current_id, 'table_footnote', footnote, level))
                        else:
                            # Single footnote as string
                            result.append((current_id, 'table_footnote', footnotes, level))
                    
                    # Postamble comes last if it exists
                    if 'postamble' in table_dict:
                        result.append((current_id, 'table_postamble', table_dict['postamble'], level))
                else:
                    # Old format - just the raw list, now using 'table_data' for consistency
                    result.append((current_id, 'table_data', table_dict, level))
        
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


def flatten_dict(dct=None, format='markdown', tuples_list=None):
    if tuples_list is None:
        tuples_list = unnest_dict(dct)
    results = []
    if format == 'markdown':
        for tuple in tuples_list:
            tuple_type = tuple[1]
            content = tuple[2]
            level = tuple[3]
            if tuple_type == 'table_data':
                results.extend(_format_table(content))
            elif tuple_type == 'table_preamble':
                results.append(f'*{content}*')  # Italicized preamble
                results.append('')
            elif tuple_type == 'table_footnote':
                results.append(f'<sub>{content}</sub>')
            elif tuple_type == 'table_postamble':
                results.append('')
                results.append(f'*{content}*')  # Italicized postamble
            elif tuple_type == 'text':
                results.append(content)
            elif tuple_type == 'textsmall':
                results.append(f'<sub>{content}</sub>')
            elif tuple_type == 'title':
                results.append(_format_title(content, level))
        
        return '\n'.join(results)
    elif format == 'text':
        for tuple in tuples_list:
            tuple_type = tuple[1]
            content = tuple[2]
            level = tuple[3]

            # reuse markdown format for tables
            if tuple_type == 'table_data':
                results.extend(_format_table(content))
            elif tuple_type == 'table_preamble':
                results.append(content)
                results.append('')
            elif tuple_type == 'table_footnote':
                results.append(content)
            elif tuple_type == 'table_postamble':
                results.append('')
                results.append(content)
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
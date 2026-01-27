import webbrowser
import os

def visualize_dict(data_dict, filename='document_visualization.html', open_browser=True):
    """
    Convert nested dictionary to HTML visualization and open in browser
    
    Parameters:
        data_dict (dict): The nested dictionary to visualize
        filename (str): The name of the HTML file to create
        open_browser (bool): Whether to automatically open in browser
    
    Returns:
        str: The path to the created HTML file
    """
    html = []
    
    # Add HTML document opening tags and CSS
    html.append("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document Visualization</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                line-height: 1.6; 
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .metadata-box { 
                background-color: #f8f9fa; 
                border: 1px solid #ddd; 
                padding: 15px; 
                margin-bottom: 20px; 
                border-radius: 5px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .metadata-title { 
                font-weight: bold; 
                margin-bottom: 10px; 
                font-size: 1.2em;
                color: #555;
            }
            
            .table-wrapper {
                margin: 15px 0;
            }
            
            .table-title-bar {
                background-color: #4a90e2;
                color: white;
                padding: 12px 15px;
                font-weight: bold;
                font-size: 1.05em;
                border-radius: 5px 5px 0 0;
                border: 2px solid #4a90e2;
                border-bottom: none;
            }
            
            .table-title-label {
                font-size: 0.85em;
                font-style: italic;
                opacity: 0.9;
                margin-left: 8px;
                font-weight: normal;
            }
            
            table { 
                border-collapse: collapse; 
                width: 100%; 
                margin: 0; 
                background-color: white;
            }
            
            .table-wrapper table {
                border-radius: 0 0 5px 5px;
            }
            
            table, th, td { 
                border: 2px solid #ddd; 
            }
            th, td { 
                padding: 10px; 
                text-align: left; 
            }
            th {
                background-color: #f2f2f2;
                font-weight: bold;
            }
            .textsmall { 
                font-size: 0.85em; 
                color: #666; 
            }
            .section { 
                margin-left: 20px; 
                margin-bottom: 15px; 
                padding-left: 10px;
                border-left: 1px solid #eee;
            }
            h1, h2, h3, h4, h5, h6 {
                margin-top: 1em;
                margin-bottom: 0.5em;
                color: #333;
            }
            p {
                margin: 0.5em 0;
            }
            .document-image {
                max-width: 100%;
                height: auto;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                margin: 10px 0;
            }
            .table-image {
                max-width: 200px;
                height: auto;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
            .image-wrapper {
                text-align: center;
                margin: 15px 0;
            }
            .table-footnotes {
                margin-top: 0;
                margin-bottom: 0;
                padding-left: 10px;
                border-left: 3px solid #ddd;
                border-right: 2px solid #ddd;
                border-bottom: 2px solid #ddd;
                background-color: #fafafa;
                padding: 10px;
                font-size: 0.9em;
                border-radius: 0 0 5px 5px;
            }
            .footnote {
                margin: 5px 0;
                color: #555;
            }
                
            .table-preamble {
                margin-bottom: 0;
                padding: 10px 15px;
                background-color: #f0f8ff;
                border-left: 2px solid #ddd;
                border-right: 2px solid #ddd;
                border-top: 2px solid #ddd;
                font-size: 0.95em;
                font-style: italic;
            }

            .table-preamble-with-title {
                border-top: none;
            }

            .table-postamble {
                margin-top: 0;
                padding: 10px 15px;
                background-color: #fff8f0;
                border-left: 2px solid #ddd;
                border-right: 2px solid #ddd;
                border-bottom: 2px solid #ddd;
                font-size: 0.95em;
                border-radius: 0 0 5px 5px;
            }

            .preamble-item, .postamble-item {
                margin: 5px 0;
                color: #444;
            }
        </style>
    </head>
    <body>
    """)
    
    # Add metadata box
    if "metadata" in data_dict:
        html.append('<div class="metadata-box">')
        html.append('<div class="metadata-title">Parser Metadata</div>')
        metadata = data_dict["metadata"]
        for key, value in metadata.items():
            html.append(f'<div><strong>{key}:</strong> {value}</div>')
        html.append('</div>')
    
    # Process the document structure
    if "document" in data_dict:
        html.append('<div class="document">')
        process_document(data_dict["document"], html, 1)
        html.append('</div>')
    
    # Add HTML closing tags
    html.append("""
    </body>
    </html>
    """)
    
    html_content = ''.join(html)
    
    # Write HTML content to a file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Get the absolute path of the file
    file_path = os.path.abspath(filename)
    
    # Open the HTML file in the default web browser if requested
    if open_browser:
        webbrowser.open('file://' + file_path)
    
    return file_path

def process_document(doc_dict, html, level):
    """Process document elements recursively"""
    # Sort keys to ensure numerical order for items like "1", "2", etc.
    try:
        sorted_keys = sorted(doc_dict.keys(), key=lambda x: (not x.lstrip('-').isdigit(), int(x) if x.lstrip('-').isdigit() else x))
    except:
        # Fallback if sorting fails
        sorted_keys = list(doc_dict.keys())
    
    for key in sorted_keys:
        value = doc_dict[key]
        
        if isinstance(value, dict):
            section_title = value.get("title", "")
            
            # Output the section title
            if section_title:
                heading_level = min(level, 6)  # Limit to h6
                html.append(f'<h{heading_level}>{section_title}</h{heading_level}>')
            
            # Process the section content
            html.append('<div class="section">')
            
            # Handle direct content fields
            for attr_key, attr_value in value.items():
                if attr_key not in ["title", "class", "contents", "standardized_title"]:
                    process_content(attr_key, attr_value, html)
            
            # Process contents dictionary if it exists
            if "contents" in value and value["contents"]:
                process_document(value["contents"], html, level + 1)
                
            html.append('</div>')
        else:
            # Direct content
            process_content(key, value, html)

def process_content(content_type, content, html):
    """Process specific content types"""
    if content_type == "text":
        # Preserve bullet points and other formatting
        html.append(f'<p>{content}</p>')
    elif content_type == "textsmall":
        html.append(f'<p class="textsmall">{content}</p>')
    elif content_type == "image":
        process_image(content, html)
    elif content_type == "table":
        process_table(content, html)
    else:
        pass

def process_image(image_data, html):
    """Convert image data to HTML img tag"""
    src = image_data.get('src', '')
    alt = image_data.get('alt', 'Image')
    
    html.append('<div class="image-wrapper">')
    html.append(f'<img src="{src}" alt="{alt}" class="document-image">')
    html.append('</div>')

def process_table_cell(cell):
    """Process a single table cell that may contain text or image data"""
    if isinstance(cell, dict):
        if 'image' in cell:
            # Cell contains an image
            image_data = cell['image']
            src = image_data.get('src', '')
            alt = image_data.get('alt', 'Image')
            return f'<img src="{src}" alt="{alt}" class="table-image">'
        elif 'text' in cell:
            # Cell contains structured text data
            return cell['text']
        else:
            # Cell is a dict but doesn't match expected structure
            return str(cell)
    else:
        # Cell is a string or other simple type
        return str(cell)


def process_table(content, html):
    """Convert table data to HTML table"""
    
    # Wrap entire table structure
    html.append('<div class="table-wrapper">')
    
    # Display table title if present (FIRST, before everything)
    has_title = 'title' in content and content['title']
    if has_title:
        html.append('<div class="table-title-bar">')
        html.append(content['title'])
        html.append('<span class="table-title-label">(inherited)</span>')
        html.append('</div>')
    
    # Process preamble if present (AFTER title)
    if 'preamble' in content and content['preamble'] is not None:
        preamble_class = 'table-preamble'
        if has_title:
            preamble_class += ' table-preamble-with-title'
        html.append(f'<div class="{preamble_class}">')
        html.append(f'<p class="preamble-item">{content["preamble"]}</p>')
        html.append('</div>')
        
    # Render the table
    table_data = content['data']
    
    html.append('<table>')
    
    # Check if first row should be treated as header
    has_header = False
    if len(table_data) > 1:
        # Heuristic: if first row contains mostly text content, treat as header
        first_row = table_data[0]
        text_cells = 0
        for cell in first_row:
            if isinstance(cell, str) and cell.strip():
                text_cells += 1
            elif isinstance(cell, dict) and cell.get('text', '').strip():
                text_cells += 1
        
        if text_cells >= len(first_row) / 2:  # At least half the cells have text
            has_header = True
    
    for i, row in enumerate(table_data):
        html.append('<tr>')
        for cell in row:
            # Use th for header cells, otherwise td
            tag = 'th' if has_header and i == 0 else 'td'
            cell_content = process_table_cell(cell)
            html.append(f'<{tag}>{cell_content}</{tag}>')
        html.append('</tr>')
    
    html.append('</table>')
    
    # Process footnotes if present (AFTER table)
    if 'footnotes' in content and content['footnotes']:
            html.append('<div class="table-footnotes">')
            for footnote in content['footnotes']:
                # footnote is [id, text] format
                html.append(f'<p class="footnote"><b>{footnote[0]}</b> {footnote[1]}</p>')
            html.append('</div>')
    
    # Process postamble if present (AFTER footnotes)
    if 'postamble' in content and content['postamble'] is not None:
        html.append('<div class="table-postamble">')
        html.append(f'<p class="postamble-item">{content["postamble"]}</p>')
        html.append('</div>')
    
    # Close table wrapper
    html.append('</div>')
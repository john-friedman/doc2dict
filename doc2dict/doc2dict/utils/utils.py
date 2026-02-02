import re

def get_title(dct, title=None, title_regex=None, title_class=None):
    results = []
    
    # Ensure valid parameter combination
    if title is not None and title_regex is not None:
        raise ValueError("Cannot specify both 'title' and 'title_regex'")
    
    if title is None and title_regex is None and title_class is None:
        raise ValueError("At least one of 'title', 'title_regex', or 'title_class' must be specified")
    
    title_class = title_class.lower() if title_class else None
    
    if title_regex:
        title_pattern = re.compile(title_regex, re.IGNORECASE)
    elif title:
        title_lower = title.lower()
    
    def search(node, parent_id=None):
        if isinstance(node, dict):
            node_title = node.get('title', '')
            node_class = node.get('class', '').lower()
            node_standardized_title = node.get('standardized_title', '')
            
            # Check title match based on which parameter was provided
            if title_regex:
                title_match = (title_pattern.match(node_title) or 
                              title_pattern.match(node_standardized_title))
            elif title:
                title_match = (node_title.lower() == title_lower or 
                              node_standardized_title.lower() == title_lower)
            else:
                # No title filter specified, match all titles
                title_match = True
            
            # Apply class filter
            class_match = (title_class is None or node_class == title_class)
            
            if title_match and class_match:
                results.append((parent_id, node))
                
            contents = node.get('contents', {})
            for key, value in contents.items():
                search(value, key)
    
    if 'document' in dct:
        for doc_id, doc_node in dct['document'].items():
            search(doc_node, doc_id)
                
    return results

get_title_from_dict = get_title

def get_title_from_tuples(tuples_list, title=None, title_regex=None, title_class=None):
    """
    Search through data tuples to find sections matching title/class criteria.
    
    Args:
        tuples_list: List of tuples from convert_dict_to_data_tuples
        title: Exact title string to match (case-insensitive)
        title_regex: Regex pattern to match against titles
        title_class: Class to filter by ('item', 'part', etc.)
    
    Returns:
        List of tuples belonging to matching sections (including all descendants)
    """
    # Ensure valid parameter combination
    if title is not None and title_regex is not None:
        raise ValueError("Cannot specify both 'title' and 'title_regex'")
    
    if title is None and title_regex is None and title_class is None:
        raise ValueError("At least one of 'title', 'title_regex', or 'title_class' must be specified")
    
    # Normalize inputs
    title_class = title_class.lower() if title_class else None
    
    if title_regex:
        title_pattern = re.compile(title_regex, re.IGNORECASE)
    elif title:
        title_lower = title.lower()
    
    # Find matching section indices and their levels
    matching_sections = []  # List of (index, level)
    
    for idx, tup in enumerate(tuples_list):
        section_id, tuple_type, content, level = tup[0], tup[1], tup[2], tup[3]
        class_val = tup[4] if len(tup) > 4 else None
        
        # Only look at title tuples for matching
        if tuple_type != 'title':
            continue
        
        # Check title match
        if title_regex:
            title_match = title_pattern.search(content)
        elif title:
            title_match = (content.lower() == title_lower)
        else:
            # No title filter, match all
            title_match = True
        
        # Check class match
        if class_val:
            class_match = (title_class is None or class_val.lower() == title_class)
        else:
            class_match = (title_class is None)
        
        if title_match and class_match:
            matching_sections.append((idx, level))
    
    # Collect all tuples for matching sections including descendants
    results = []
    
    for match_idx, match_level in matching_sections:
        # Add the matched section itself
        results.append(tuples_list[match_idx])
        
        # Collect all descendants (tuples that come after and have higher level)
        for idx in range(match_idx + 1, len(tuples_list)):
            current_tuple = tuples_list[idx]
            current_level = current_tuple[3]
            
            # If we hit a tuple at same or lower level, we've left this section
            if current_level <= match_level:
                break
            
            # This tuple is a descendant, add it
            results.append(current_tuple)
    
    return results
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
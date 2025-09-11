import re

def get_title(dct, title=None, title_regex=None, title_class=None):
    results = []
    
    # Ensure exactly one of title or title_regex is specified
    if (title is None and title_regex is None) or (title is not None and title_regex is not None):
        raise ValueError("Exactly one of 'title' or 'title_regex' must be specified")
    
    title_class = title_class.lower() if title_class else None
    
    if title_regex:
        title_pattern = re.compile(title_regex, re.IGNORECASE)
    else:
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
            else:
                title_match = (node_title.lower() == title_lower or 
                              node_standardized_title.lower() == title_lower)
            
            if title_match and (title_class is None or node_class == title_class):
                results.append((parent_id, node))
                
            contents = node.get('contents', {})
            for key, value in contents.items():
                search(value, key)
    
    if 'document' in dct:
        for doc_id, doc_node in dct['document'].items():
            search(doc_node, doc_id)
                
    return results

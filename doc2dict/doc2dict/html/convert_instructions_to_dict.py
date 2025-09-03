import re
from importlib.metadata import version

__version__ = version("doc2dict")

LIKELY_HEADER_ATTRIBUTES = ['bold', 'italic', 'underline', 'text-center', 'all_caps', 'fake_table','proper_case']

def remove_empty_contents(obj):
    """Recursively remove empty contents dictionaries"""
    if isinstance(obj, dict):
        if 'contents' in obj and not obj['contents']:
            del obj['contents']
        else:
            for value in obj.values():
                remove_empty_contents(value)

def create_level(level_num=-1, class_name='text', title='', attributes=None):
    """Factory function to create level dictionaries with all required fields"""
    return {
        'level': level_num, 
        'class': class_name, 
        'standardized_title': title, 
        'attributes': attributes or {}
    }


def split_header_instructions(instructions_list):
    """
    Splits instruction groups where the first instruction would be classified as a header.
    
    Args:
        instructions_list: List of instruction groups (each group is a list of instructions)
        
    Returns:
        New list of instruction groups with headers separated from their content
    """

    
    # First, detect big_script like in determine_levels
    text_instructions = [instr[0] for instr in instructions_list if 'text' in instr[0]]
    font_size_counts = {size: sum(1 for item in text_instructions if item.get('font-size') == size) 
                       for size in set(item.get('font-size') for item in text_instructions if item.get('font-size') is not None)}
    
    big_script = [False] * len(instructions_list)
    if font_size_counts:
        most_common_font_size, font_count = max(font_size_counts.items(), key=lambda x: x[1])
        if font_count > (0.5 * len(instructions_list)):
            # Check for big script (>20% larger than most common)
            for idx, instructions in enumerate(instructions_list):
                first = instructions[0]
                if 'text' in first and first.get('font-size') is not None:
                    if first.get('font-size') > (1.2 * most_common_font_size):
                        big_script[idx] = True
    
    # Now split instruction groups
    new_instructions_list = []
    
    for idx, instructions in enumerate(instructions_list):
        # Skip if only one instruction - nothing to split
        if len(instructions) <= 1:
            new_instructions_list.append(instructions)
            continue
        
        first_instruction = instructions[0]
        
        # Check if first instruction would be classified as a header
        is_header = False
        if 'text' in first_instruction:
            # Check for header attributes or big_script
            has_header_attrs = any(first_instruction.get(attr, False) for attr in LIKELY_HEADER_ATTRIBUTES)
            if has_header_attrs or big_script[idx]:
                is_header = True
        
        if is_header:
            # Split: first instruction becomes its own group, rest become another group
            new_instructions_list.append([first_instruction])
            if len(instructions) > 1:  # Add remaining instructions as separate group
                new_instructions_list.append(instructions[1:])
        else:
            # Keep as is - no splitting needed
            new_instructions_list.append(instructions)
    
    return new_instructions_list


# AI GENERATED CODE BC I WANT TO PUSH TO PROD #
def determine_predicted_header_levels(levels):
    """
    Assigns hierarchy levels to predicted headers based on their attributes,
    maintaining consistency within each section defined by known headers.
    
    Args:
        levels: List of dictionaries containing level, class, and attributes
        
    Returns:
        List of tuples in the format (level, class)
    """
    # Find the base level for predicted headers
    predicted_headers = [l for l in levels if l['class'] == 'predicted header']
    if not predicted_headers:
        return [(level['level'], level['class'], level.get('standardized_title','')) for level in levels]
    
    base_level = min(h['level'] for h in predicted_headers)
    
    # Create a copy of levels that we'll modify
    updated_levels = levels.copy()
    
    # Track the last known header level
    current_section_level = -1
    
    # Dictionary to map attribute combinations to levels within the current section
    # Format: {attribute_key: assigned_level}
    attr_level_map = {}
    
    # Helper function to create a key from attributes dictionary
    def attr_to_key(attrs):
        if not attrs:
            return "no_attributes"
        # Sort keys to ensure consistent mapping regardless of order
        return "_".join(sorted([k for k, v in attrs.items() if v]))
    
    # Process each item
    for i, item in enumerate(updated_levels):
        # When we hit a known header, reset our attribute mapping
        if item['class'] != 'predicted header' and item['class'] not in ['text', 'textsmall']:
            if item['level'] <= current_section_level:
                # We've entered a new section at same or higher level, reset mappings
                attr_level_map = {}
            current_section_level = item['level']
            continue
        
        # Skip non-header items
        if item['class'] != 'predicted header':
            continue
        
        # Create a key for this item's attributes
        attr_key = attr_to_key(item.get('attributes', {}))
        
        # If we haven't seen this attribute combination in this section,
        # assign it the next available level
        if attr_key not in attr_level_map:
            attr_level_map[attr_key] = base_level + len(attr_level_map)
        
        # Assign the level based on the mapping
        item['level'] = attr_level_map[attr_key]
    
    # Return in the required format
    return [(level['level'], level['class'], level.get('standardized_title','')) for level in updated_levels]
# AI GENERATED CODE BC I WANT TO PUSH TO PROD #

def extract_cell_content(cell):
    """Helper function to extract content from table cells that may contain text or images"""
    if 'image' in cell:
        return cell  # Return the full cell structure for images
    else:
        return cell.get("text", "")  # Return text content or empty string

def determine_levels(instructions_list, mapping_dict=None):
    if mapping_dict is None:
        predicted_header_level = 0
    #TODO bandaid fix
    elif 'rules' in mapping_dict:
        predicted_header_level = 0
    else:
        predicted_header_level = max(mapping_dict.values()) + 1

    # filter out tables, include both text and image instructions
    headers = []
    for instructions in instructions_list:
        first_instruction = instructions[0]
        if 'text' in first_instruction or 'image' in first_instruction:
            headers.append(first_instruction)
        else:
            headers.append({})

    
    # count font-size (only for text instructions)
    small_script = [False] * len(headers)
    big_script = [False] * len(headers)
    text_instructions = [instr[0] for instr in instructions_list if 'text' in instr[0]]
    font_size_counts = {size: sum(1 for item in text_instructions if item.get('font-size') == size) for size in set(item.get('font-size') for item in text_instructions if item.get('font-size') is not None)}
    
    # use only font size goes here
    if mapping_dict is not None:
        if 'rules' in mapping_dict:
            if 'use_font_size_only_for_level' in mapping_dict['rules']:
                # Filter headers first for this special case
                headers = [item if 'text' in item and any([item.get(attr, False) for attr in LIKELY_HEADER_ATTRIBUTES]) else {} for item in headers]
                
                most_common_font_size, font_count = max(font_size_counts.items(), key=lambda x: x[1])
                
                # Get all unique font sizes and sort them in descending order (largest font = level 0, next = level 1, etc.)
                unique_font_sizes = sorted(font_size_counts.keys(), reverse=True)
                
                # Create a mapping from font size to level (largest font = level 0, next = level 1, etc.)
                font_size_to_level = {size: idx for idx, size in enumerate(unique_font_sizes)}
                
                levels = []
                for idx, header in enumerate(headers):
                    if 'text' in header and header.get('font-size') is not None:
                        font_size = header.get('font-size')
                        
                        if font_size < most_common_font_size:
                            # Assign small script for fonts smaller than most common
                            level = (-2,'textsmall','')
                        else:
                            # Assign level based on font size hierarchy
                            hierarchy_level = font_size_to_level[font_size]
                            level = (hierarchy_level, 'predicted header','')
                    else:
                        # No font size information or not text, treat as regular text
                        level = (-1, 'text','')
                    
                    levels.append(level)
                
                return levels
    
    # Detect font sizes first (before filtering headers)
    if font_size_counts != {}:
        most_common_font_size, font_count = max(font_size_counts.items(), key=lambda x: x[1])
        if font_count > (.5 * len(instructions_list)):
            # assume anything with less than this font size is small script
            small_script = [True if 'text' in item and item.get('font-size') is not None and item.get('font-size') < most_common_font_size else False for item in headers]
            
            # assume anything with more than 20% of the most common font size is big script
            big_script = [True if 'text' in item and item.get('font-size') is not None and item.get('font-size') > (1.2 * most_common_font_size) else False for item in headers]

    # NOW filter headers after font size detection (includes big_script in the filtering)
    headers = [item if 'text' in item and (any([item.get(attr, False) for attr in LIKELY_HEADER_ATTRIBUTES]) or big_script[idx]) else {} for idx, item in enumerate(headers)]
    
    levels = []
    for idx,header in enumerate(headers):
        level = None
        attributes = {attr: header.get(attr, False) for attr in LIKELY_HEADER_ATTRIBUTES if attr in header}
        
        if small_script[idx]:
            level = create_level(-2, 'textsmall')
        elif 'text' in header:
            if mapping_dict is not None:
                text = header['text'].lower()
                regex_tuples = [(item[0][1], item[0][0], item[1]) for item in mapping_dict.items()]
                
                for regex, header_class, hierarchy_level in regex_tuples:
                    match = re.match(regex, text.strip())
                    if match:
                        # create a dictionary of attributes from LIKELY_HEADER_ATTRIBUTES
                        match_groups = match.groups()
                        if len(match_groups) > 0:
                            string = ''.join([str(x) for x in match_groups if x is not None])
                            standardized_title = f'{header_class}{string}'
                        else:
                            standardized_title = f'{header_class}'
                        level = create_level(hierarchy_level, header_class, standardized_title, attributes)
                        break
            
            if level is None:
                # Check for header attributes OR big_script
                if any([header.get(attr,False) for attr in LIKELY_HEADER_ATTRIBUTES]) or big_script[idx]:
                    level = create_level(predicted_header_level, 'predicted header', '', attributes)

        if level is None:
            level = create_level(-1, 'text')
        
        levels.append(level)

    # NOW USE SEQUENCE AND ATTRIBUTES IN THE LEVELS TO DETERMINE HIERARCHY FOR PREDICTED HEADERS
    levels = determine_predicted_header_levels(levels)
    return levels

def convert_instructions_to_dict(instructions_list, mapping_dict=None):
    # CHANGE: Split mixed header-content groups first
    instructions_list = split_header_instructions(instructions_list)
    
    # Get pre-calculated levels for each instruction
    levels = determine_levels(instructions_list, mapping_dict)
    
    # Initialize document structure
    document = {'contents': {}}
    
    # Create an introduction section
    introduction = {'title': 'introduction', 'class': 'introduction', 'contents': {}}
    
    # Add the introduction to the document
    document['contents'][-1] = introduction
    
    # Keep track of current position in hierarchy
    current_section = introduction
    current_path = [document, introduction]  # Path from root to current section
    current_levels = [-1, 0]  # Corresponding hierarchy levels
    
    # Process each instruction using pre-calculated levels
    for idx, instructions in enumerate(instructions_list):
        instruction = instructions[0]
        level, level_class, standardized_title = levels[idx]

        if level >= 0:
            # This is a section header
            
            # Pop hierarchy until finding appropriate parent
            while len(current_levels) > 1 and current_levels[-1] >= level:
                current_path.pop()
                current_levels.pop()
            
            # Extract title from the instruction (only text instructions can be headers)
            if 'text' in instruction:
                title = ''.join([instr['text'] for instr in instructions if 'text' in instr])
            else:
                title = '[Non-text header]'  # Fallback, though this shouldn't happen
            
            # Create new section, in correct order
            new_section = {'title': title}
            if standardized_title:  # Add right after title
                new_section['standardized_title'] = standardized_title
            new_section['class'] = level_class
            new_section['contents'] = {}
            
            # Add section to parent's contents with index as key
            parent = current_path[-1]
            parent['contents'][idx] = new_section
            
            # Update tracking
            current_path.append(new_section)
            current_levels.append(level)
            current_section = new_section
            
            # CHANGE: Removed mixed content handling here since groups are now pure

        # CHANGE: Simplified - only process regular content (no mixed groups anymore)
        if level in [-1, -2]:
            for instruction in instructions:
                if 'text' in instruction:
                    if not current_section['contents'].get(idx):
                        current_section['contents'][idx] = {level_class: ''}
                    if level_class in current_section['contents'][idx]:
                        current_section['contents'][idx][level_class] += instruction['text']
                    else:
                        current_section['contents'][idx][level_class] = instruction['text']
                elif 'image' in instruction:
                    current_section['contents'][idx] = {'image': instruction['image']}
                elif 'table' in instruction:
                    current_section['contents'][idx] = {'table': [[extract_cell_content(cell) for cell in row] for row in instruction['table']]}
    
    # Create final result with metadata
    result = {
        'metadata': {
            'parser': 'doc2dict',
            'github': 'https://github.com/john-friedman/doc2dict',
            "version": __version__,
        },
        'document': document['contents']
    }
    
    remove_empty_contents(result)
    return result
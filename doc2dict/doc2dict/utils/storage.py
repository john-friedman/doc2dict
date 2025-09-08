ATTRIBUTES = {
   # Tags
   "table": (2, "tag"),
    "image": (3, "tag"),
   
   # Value based
   "text": (0, "value"),
   "font-size": (10, "value"),
   "left-indent": (11, "value"),
   "href": (12, "value"),
   
   # Boolean
   "bold": (100, "boolean"),
   "italic": (101, "boolean"),
   "underline": (102, "boolean"),
   "text-center": (103, "boolean"),
   "display-none": (104, "boolean"),
   "all_caps": (105, "boolean"),
   "proper_case": (106, "boolean"),
   
   # Special/Meta
   "cleaned": (200, "boolean") ,
    "fake_table": (201, "boolean"),

    # IMAGE
    "src" : (300,"value"),
    "alt" : (301,"value"),
}


SEPARATORS = {
    "unit": '\x1f',      # Unit Separator (31) RESERVED for instruction
    'group': '\x1d',     # Group Separator (29) RESERVED for instruction
    "record": '\x1e',    # Record Separator (30) RESERVED for instruction
    'file': '\x1c',      # File Separator (28) RESERVED for new instructions. Can't reuse.
    'down': '\x0e',      # Shift Out (14) - "shift out" to deeper level
    'up': '\x0f',         # Shift In (15) - "shift in" to shallower level
    'list_start': '\x01',  # SOH - Start of Heading  
    'list_end': '\x04'     # EOT - End of Transmission
}

TRANSLATOR = str.maketrans('', '', ''.join(SEPARATORS.values()))

def serialize_instruction(instruction):
    """Recursion"""
    block = ''
    attrs = instruction.keys()
    for attr_name in attrs:
        if attr_name in ATTRIBUTES:
            attr_id, attr_type = ATTRIBUTES[attr_name]
            attr_value = instruction[attr_name]
            if attr_type == 'value':
                # Sanitize values
                attr_value = str(attr_value).translate(TRANSLATOR)
                block += f"{attr_id}{SEPARATORS['unit']}{attr_value}{SEPARATORS['group']}"
            elif attr_type == "boolean":
                block += f"{attr_id}{SEPARATORS['group']}"
            elif attr_type == 'tag':
                if attr_id == ATTRIBUTES['image'][0]:
                    block += str(ATTRIBUTES['image'][0]) + SEPARATORS['down'] + serialize_instruction(attr_value) + SEPARATORS['up']
                elif attr_id == ATTRIBUTES['table'][0]:
                    row_strs = [SEPARATORS['list_start'] + ''.join([serialize_instruction(cell) for cell in row]) + SEPARATORS['list_end'] for row in attr_value]
                    serialized_table_str = SEPARATORS['list_start'] + ''.join(row_strs) + SEPARATORS['list_end']
                    block += str(ATTRIBUTES['table'][0]) + SEPARATORS['down'] + serialized_table_str + SEPARATORS['up']
                else:
                    raise ValueError("WRONG")
            else:
                raise ValueError("Attribute type not allowed: {attr_type}")
        else:
            raise ValueError(f'Attribute not found: {attr_name}')
    return block

def serialize_instructions(instructions):
    line = ''
    for instruction in instructions:
        block = serialize_instruction(instruction)
        line += block + SEPARATORS["record"]
    
    return line

def serialize_instructions_list(instructions_list):
    serialized_instructions_list = []
    for instructions in instructions_list:
        serialized_instructions_list.append(serialize_instructions(instructions))
    
    return SEPARATORS["file"].join(serialized_instructions_list) 


# GENERATED WITH AI #
# seems to work except for tables #

# Create reverse lookup: attr_id -> (attr_name, attr_type)
ATTR_LOOKUP = {str(v[0]): (k, v[1]) for k, v in ATTRIBUTES.items()}


def deserialize_instruction(data):
    """Deserialize a single instruction from a string"""
    instruction = {}
    pos = 0
    
    while pos < len(data):
        # Find next attribute ID
        attr_start = pos
        attr_end = pos
        
        # Find end of attribute ID (unit or group or down separator)
        while attr_end < len(data) and data[attr_end] not in (SEPARATORS['unit'], 
                                                               SEPARATORS['group'], 
                                                               SEPARATORS['down']):
            attr_end += 1
        
        if attr_end == attr_start:
            break
            
        attr_id = data[attr_start:attr_end]
        
        if attr_id not in ATTR_LOOKUP:
            break
            
        attr_name, attr_type = ATTR_LOOKUP[attr_id]
        
        if attr_type == 'value':
            # Value attribute with unit separator
            if attr_end < len(data) and data[attr_end] == SEPARATORS['unit']:
                val_start = attr_end + 1
                val_end = val_start
                while val_end < len(data) and data[val_end] != SEPARATORS['group']:
                    val_end += 1
                instruction[attr_name] = data[val_start:val_end]
                pos = val_end
                if pos < len(data) and data[pos] == SEPARATORS['group']:
                    pos += 1
                    
        elif attr_type == 'boolean':
            # Boolean attribute (no value, just presence)
            instruction[attr_name] = True
            pos = attr_end
            if pos < len(data) and data[pos] == SEPARATORS['group']:
                pos += 1
                
        elif attr_type == 'tag':
            # Tag attribute with nested structure
            if attr_end < len(data) and data[attr_end] == SEPARATORS['down']:
                nested_start = attr_end + 1
                
                if attr_name == 'image':
                    # Find matching up separator
                    nested_end = nested_start
                    depth = 1
                    while nested_end < len(data) and depth > 0:
                        if data[nested_end] == SEPARATORS['down']:
                            depth += 1
                        elif data[nested_end] == SEPARATORS['up']:
                            depth -= 1
                        nested_end += 1
                    
                    # Parse the image content
                    image_data = data[nested_start:nested_end-1]
                    instruction[attr_name] = deserialize_instruction(image_data)
                    pos = nested_end
                    
                elif attr_name == 'table':
                    # Parse table structure
                    table = []
                    tbl_pos = nested_start
                    
                    # Skip outer list_start
                    if tbl_pos < len(data) and data[tbl_pos] == SEPARATORS['list_start']:
                        tbl_pos += 1
                    
                    # Process rows
                    while tbl_pos < len(data) and data[tbl_pos] != SEPARATORS['list_end']:
                        if data[tbl_pos] == SEPARATORS['list_start']:
                            # Start of a row
                            row = []
                            tbl_pos += 1
                            
                            # Process cells in row
                            while tbl_pos < len(data) and data[tbl_pos] != SEPARATORS['list_end']:
                                # Find next record separator (end of cell)
                                cell_end = tbl_pos
                                while cell_end < len(data) and data[cell_end] not in (SEPARATORS['record'], 
                                                                                       SEPARATORS['list_end']):
                                    cell_end += 1
                                
                                if cell_end > tbl_pos:
                                    cell_data = data[tbl_pos:cell_end]
                                    cell = deserialize_instruction(cell_data)
                                    if cell:
                                        row.append(cell)
                                
                                tbl_pos = cell_end
                                if tbl_pos < len(data) and data[tbl_pos] == SEPARATORS['record']:
                                    tbl_pos += 1
                            
                            # Skip row list_end
                            if tbl_pos < len(data) and data[tbl_pos] == SEPARATORS['list_end']:
                                tbl_pos += 1
                            
                            if row:
                                table.append(row)
                        else:
                            tbl_pos += 1
                    
                    # Skip table list_end
                    if tbl_pos < len(data) and data[tbl_pos] == SEPARATORS['list_end']:
                        tbl_pos += 1
                    
                    # Skip up separator
                    if tbl_pos < len(data) and data[tbl_pos] == SEPARATORS['up']:
                        tbl_pos += 1
                    
                    instruction[attr_name] = table
                    pos = tbl_pos
    
    return instruction


def deserialize_instructions(line):
    """Deserialize a line containing multiple instructions separated by record separators"""
    instructions = []
    
    # Split by record separator to get individual instructions
    instruction_strs = line.split(SEPARATORS['record'])
    
    for inst_str in instruction_strs:
        if inst_str:  # Skip empty strings
            instruction = deserialize_instruction(inst_str)
            if instruction:
                instructions.append(instruction)
    
    return instructions


def deserialize_instructions_list(serialized_data):
    """Deserialize multiple instruction lists separated by file separators"""
    instructions_list = []
    
    # Split by file separator
    lines = serialized_data.split(SEPARATORS['file'])
    
    for line in lines:
        if line:  # Skip empty lines
            instructions = deserialize_instructions(line)
            if instructions:
                instructions_list.append(instructions)
    
    return instructions_list
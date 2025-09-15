from .convert_txt_to_instructions import convert_txt_to_instructions
from ..convert_instructions_to_dict import convert_instructions_to_dict


# FIX THIS # TODO TODO
def combine_text_wraparound(instructions_list):
    """Used for e.g. text files where the next line is meant to be part of the same paragraph, but the next next line is a new paragraph"""

    # merge instructions
    new_instructions_list = []
    current_instructions = []
    
    for line_num in range(len(instructions_list) - 1):
        instructions = instructions_list[line_num]
        # Add wraparound attribute to each instruction
        for instruction in instructions:
            instruction['wraparound'] = True

        # Only add space if this is NOT the first line of the paragraph
        if current_instructions and 'text' in instructions[0]:
            instructions[0]['text'] = ' ' + instructions[0]['text']
        
        # Extend current_instructions with this line's instructions
        current_instructions.extend(instructions)
        
        if instructions_list[line_num + 1] == []:  # Next line is empty
            if current_instructions:  # Only append if not empty
                new_instructions_list.append(current_instructions)
            current_instructions = []  # Reset for new paragraph
    
    # Handle the last line
    if instructions_list:  # Check if list is not empty
        last_instructions = instructions_list[-1]
        
        # Only add space if this is NOT the first line of the paragraph
        if current_instructions and 'text' in last_instructions[0]:
            last_instructions[0]['text'] = ' ' + last_instructions[0]['text']
            
        current_instructions.extend(last_instructions)
        if current_instructions:  # Only append if not empty
            new_instructions_list.append(current_instructions)

    return new_instructions_list

        
def txt2dict(content,mapping_dict=None,encoding='utf-8'):
    content = content.decode(encoding=encoding)
    instructions_list = convert_txt_to_instructions(content=content)

    # we need to add a filter here, ideally via mapping
    # should use whether ends with '.' to merge. into blocks
    # probably add default and if detected for the pdf use case

    instructions_list = combine_text_wraparound(instructions_list=instructions_list)

    # handle dash headers e.g. [{'text': 'Item 2.  Properties', 'wraparound': True}, {'text': ' -------------------', 'wraparound': True}]
    # duct tape solution TODO fix
    for instructions in instructions_list:
        if 'text' in instructions[-1]:
            if set(instructions[-1]['text'].replace(' ','')) == {'-'}:
                # add bold to all instructions
                [item.update({'bold': True}) or item for item in instructions]
                instructions.pop()
    
    instructions_list = [item for item in instructions_list if item !=[]]

    dct = convert_instructions_to_dict(instructions_list=instructions_list,mapping_dict=mapping_dict)
    return dct
    
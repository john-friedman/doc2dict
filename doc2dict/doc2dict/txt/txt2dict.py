from .convert_txt_to_instructions import convert_txt_to_instructions
from ..convert_instructions_to_dict import convert_instructions_to_dict


# FIX THIS # TODO TODO
def combine_text_wraparound(instructions_list):
    """Used for e.g. text files where the next line is meant to be part of the same paragraph, but the next next line is a new paragraph"""

    # merge instructions
    new_instructions_list = []
    current_instructions = []
    
    for line_num in range(len(instructions_list) - 1):
        current_instructions.append(instructions_list[line_num])
        current_instructions.append({'text':' ','wraparound':True})
        
        if instructions_list[line_num + 1] == []:  # Next line is empty
            new_instructions_list.append(current_instructions)
            current_instructions = []
    
    # Handle the last line
    current_instructions.append(instructions_list[-1])
    if current_instructions:
        new_instructions_list.append(current_instructions)
    
    print(new_instructions_list)
    return new_instructions_list

        
def txt2dict(content,mapping_dict=None,encoding='utf-8'):
    content = content.decode(encoding=encoding)
    instructions_list = convert_txt_to_instructions(content=content)

    # we need to add a filter here, ideally via mapping
    # should use whether ends with '.' to merge. into blocks
    # probably add default and if detected for the pdf use case

    instructions_list = combine_text_wraparound(instructions_list=instructions_list)



    dct = convert_instructions_to_dict(instructions_list=instructions_list,mapping_dict=mapping_dict)
    return dct
    
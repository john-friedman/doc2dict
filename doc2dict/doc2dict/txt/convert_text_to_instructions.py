
# need to rememember how html 2 instructions treats empty lines
# may need to rejig to standardize

TAB_SIZE = 4

def get_left_indent(line):
    count = 0
    for c in line:
        if c == '\t':
            count += TAB_SIZE
        elif c.isspace() and c not in '\r\n\f\v':
            count += 1
        else:
            break
    return count

def convert_text_to_instructions(content,mapping_dict=None):
    lines = content.split('\n')
    instructions_list = []

    for line in lines:
        instructions = []
        if len(line) != 0:
            instruction = {'text':line}
            left_indent = get_left_indent(line)
            if left_indent != 0:
                instruction['left-indent'] = str(left_indent)

            instructions.append(instruction)
            instructions_list.append(instructions)
        else:
            instructions_list.append([])

    return instructions_list
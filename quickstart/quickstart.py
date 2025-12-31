from doc2dict import convert_html_to_instructions, html2dict
from selectolax.parser import HTMLParser

# Load your html file
with open('example_output\html\msft_10k_2024.html','r') as f:
    content = f.read()


body = HTMLParser(content).body

# convert html to a series of instructions
instructions = convert_html_to_instructions(body)

with open('instructions.txt','w',encoding='utf-8') as f:
    for instruction in instructions:
        f.write(str(instruction))
        f.write('\n')

# visualize the conversion
""" visualize_instructions(instructions)

# convert instructions to dictionary
dct = html2dict(content,mapping_dict=None)

# visualize dictionary
visualize_dict(dct)

 """
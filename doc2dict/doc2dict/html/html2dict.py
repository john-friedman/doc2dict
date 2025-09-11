from .convert_html_to_instructions import convert_html_to_instructions
from ..convert_instructions_to_dict import convert_instructions_to_dict
from selectolax.parser import HTMLParser
def html2dict(content,mapping_dict=None):
    parser = HTMLParser(content)

    body = parser.body
    instructions = convert_html_to_instructions(body)
    dct = convert_instructions_to_dict(instructions, mapping_dict)
    return dct
from .xml.parser import xml2dict
from .txt.parser import txt2dict
from .dict2dict import dict2dict

from .html.convert_html_to_instructions import convert_html_to_instructions
from .html.convert_instructions_to_dict import convert_instructions_to_dict
from .html.visualize_instructions import visualize_instructions
from .html.visualize_dict import visualize_dict
from .html.html2dict import html2dict

from .pdf.pdf2dict import pdf2dict

from .utils.utils import get_title
from .utils.format_dict import unnest_dict, flatten_dict
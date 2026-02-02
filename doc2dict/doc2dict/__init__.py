from .xml.parser import xml2dict
from .txt.txt2dict import txt2dict
from .dict2dict import dict2dict

from .html.convert_html_to_instructions import convert_html_to_instructions
from .convert_instructions_to_dict import convert_instructions_to_dict
from .html.visualize_instructions import visualize_instructions
from .html.visualize_dict import visualize_dict
from .html.html2dict import html2dict

from .pdf.pdf2dict import pdf2dict

from .utils.utils import get_title, get_title_from_dict, get_title_from_tuples
from .utils.format_dict import unnest_dict, flatten_dict, convert_data_tuples_to_dict,convert_dict_to_data_tuples, convert_dict_to_columnar

from .mapping_dicts.standard_config import STANDARD_CONFIG
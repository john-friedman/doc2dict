import pypdfium2 as pdfium
from .pdf_utils import get_text, get_font_name, get_font, get_font_size
from .utils import get_font_attributes, assign_line, standardize_font_size


def convert_pdf_to_instructions(content):

    # Open the PDF
    pdf = pdfium.PdfDocument(content)

    instructions_stream = []
    # Extract text and font info from each page
    for page_index in range(len(pdf)):
        page = pdf[page_index]
        text_page = page.get_textpage()
        page_width = page.get_width()
        

        # Get page objects
        for obj in page.get_objects():
            text = get_text(text_page, obj)
            font = get_font(obj)
            font_name = get_font_name(font)
            font_attributes = get_font_attributes(font_name) # mild duplication
            
            font_size = get_font_size(obj)

            

            # left bottom righ top
            coords_tuple = obj.get_pos()
            
            # lets not add items if font size is 0  
            if font_size is None:
                continue
            else:
                instruction = {'text': text}  | {'coords': coords_tuple, 'font-size': font_size, 'font-name': font_name} | font_attributes
                instructions_stream.append(instruction)

    
    # Clean up resources
    pdf.close()

    #instructions_stream = standardize_font_size(instructions_stream)
    instructions_list = assign_line(instructions_stream)


    return instructions_list
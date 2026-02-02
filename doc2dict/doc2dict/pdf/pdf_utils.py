import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c
from ctypes import c_ushort, c_ulong, POINTER, c_float, c_void_p, c_size_t, c_uint8, c_int


def get_text(text_page,obj):
    text_len = pdfium_c.FPDFTextObj_GetText(
        obj.raw,               # FPDF_PAGEOBJECT
        text_page.raw,                  # FPDF_TEXTPAGE (NULL in this case)
        None,                  # POINTER(FPDF_WCHAR) - NULL to get the length
        c_ulong(0)             # c_ulong - specify 0 to get the required buffer size
    )
    
    # Create buffer for the text
    buffer = pdfium_c.create_string_buffer(text_len * 2)  # UTF-16LE encoding
    text_ptr = pdfium_c.cast(buffer, pdfium_c.POINTER(pdfium_c.c_ushort))
    
    # Second call to actually get the text
    chars_copied = pdfium_c.FPDFTextObj_GetText(
        obj.raw,               # FPDF_PAGEOBJECT
        text_page.raw,                  # FPDF_TEXTPAGE (NULL in this case)
        text_ptr,              # POINTER(FPDF_WCHAR) - pointer to our buffer
        c_ulong(text_len)      # c_ulong - the buffer size
    )
    
    # Convert UTF-16LE to string
    # Only convert the number of characters actually copied
    text = buffer.raw[:chars_copied*2].decode('utf-16le', errors='ignore')

    # band aid fix for special char maps
    text = text.encode('ascii', 'ignore').decode('ascii')

    # remove buffer
    text = text.strip('\x00')
    return text


def get_font_size(obj):
    # Create a c_float to receive the font size value
    font_size = c_float(0.0)
    
    # Call the PDFium function to get the font size
    result = pdfium_c.FPDFTextObj_GetFontSize(
        obj.raw,                 # FPDF_PAGEOBJECT
        pdfium_c.byref(font_size)  # POINTER(c_float)
    )
    
    # Check if the function call was successful
    if result: 
        matrix = obj.get_matrix().get()
        # Apply the transformation matrix to the font size
        mean_scale = (matrix[0] + matrix[3]) / 2

        return round(font_size.value * mean_scale,2)
    else:
        return None


def get_font(obj):
    font = pdfium_c.FPDFTextObj_GetFont(obj.raw)
    return font

def get_font_name(font):
    # Get font name
    name_len = pdfium_c.FPDFFont_GetBaseFontName(font, None, 0)
    name_buffer = pdfium_c.create_string_buffer(name_len)
    pdfium_c.FPDFFont_GetBaseFontName(font, name_buffer, name_len)
    font_name = name_buffer.value.decode('utf-8', errors='ignore')
    
    
    return font_name

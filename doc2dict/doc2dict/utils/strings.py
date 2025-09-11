import re
def check_string_style(text):
    if not text or not text.strip():
        return {}

    styles = {}

    if text.isupper():
        styles['all_caps'] = True
    else:
        # Stop words that can be lowercase in proper case
        stop_words = r'\b(and|or|of|the|in|on|at|to|for|with|by|a|an)\b'
        
        # Replace stop words with placeholder, check if remaining words are proper case
        text_no_stops = re.sub(stop_words, 'STOP', text, flags=re.IGNORECASE)
        
        # Check if all non-stop words start with capital and have at least one capital
        if re.match(r'^[A-Z][a-zA-Z]*(\s+(STOP|[A-Z][a-zA-Z]*))*$', text_no_stops) and re.search(r'[A-Z]', text):
            styles['proper_case'] = True

    return styles
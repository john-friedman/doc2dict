

def convert_text_to_instructions(content):
    lines = content.split('\n')

    # need to remember how instrunctions_list vs instructions work
    # i think its
    # each newline in html like div, creates a new instruction block
    # issue with that is e.g. pdf-> html.
    # nah thats fine, within a div looks different depending on window format os not important
    # this new rule will fit in with the pdf-> html stuff

    # what we need to do
    # each line becomes instruction block with e.g. styles

    # then send to convert to dict, which will handle wrap around
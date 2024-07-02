from ..ruletxt2python import parse_line

def test_parse_line():
    input_line = "[OPM-conclusion]        the upcoming changes section is visible if"
    
    header, body = parse_line(input_line)

    assert header == "OPM-conclusion"
    assert body == "the upcoming changes section is visible if"

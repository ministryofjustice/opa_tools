from ..ruletxt2python import convert2python, process_attributes_csv_buffer

import pytest

@pytest.fixture(autouse=True)
def process_attributes():
    attributes = '''Attribute Text
the upcoming changes section is visible
the LAR rules apply to this application
the client is passported
'''
    process_attributes_csv_buffer(attributes)

def test_if():
    input = '''
[OPM-conclusion]        the upcoming changes section is visible if
[OPM-level1]            the LAR rules apply to this application and
[OPM-level1]            the client is passported
'''
    expected_output = '''the_upcoming_changes_section_is_visible = (
    the_LAR_rules_apply_to_this_application and
    the_client_is_passported
)'''
    assert convert2python(input) == expected_output

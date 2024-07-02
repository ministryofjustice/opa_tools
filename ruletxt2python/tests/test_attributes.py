from ..ruletxt2python import attribute_root_name_to_variable, process_attributes_csv_buffer, get_attributes_converter, identify_attributes

import pytest

class TestAttributeNameToVariable:
    def test_simple(self):
        input = 'is over 18'
        assert attribute_root_name_to_variable(input) == 'is_over_18'

    def test_complicated(self):
        input = "there will be any change in the LAR client's or partner's financial circumstances within the next 12 months"
        assert attribute_root_name_to_variable(input) == "there_will_be_any_change_in_the_LAR_clients_or_partners_financial_circumstances_within_the_next_12_months"


@pytest.fixture
def root_csv():
    return '''Attribute Text
the heading for the child non means summary screen
some attribute
another attribute
'''

@pytest.fixture
def substrings_csv():
    return '''Attribute Text
a
a b
a b c
b cc
a b c d
'''

class TestProcessAttributes:
    def test_root(self, root_csv):
        process_attributes_csv_buffer(root_csv)
        assert get_attributes_converter()['the heading for the child non means summary screen'] == \
        'the_heading_for_the_child_non_means_summary_screen'

class TestIdentifyAttributes:
    def test_attribute_only(self, root_csv):
        process_attributes_csv_buffer(root_csv)
        assert identify_attributes("the heading for the child non means summary screen") == ("<attr>", ["the heading for the child non means summary screen"])

    def test_attribute_between(self, root_csv):
        process_attributes_csv_buffer(root_csv)
        assert identify_attributes("START some attribute END") == ("START <attr> END", ["some attribute"])

    def test_multiple(self, root_csv):
        process_attributes_csv_buffer(root_csv)
        assert identify_attributes("some attribute > another attribute") == ("<attr> > <attr>", ["some attribute", "another attribute"])

    def test_substrings(self, substrings_csv):
        process_attributes_csv_buffer(substrings_csv)
        assert identify_attributes("a b a b c a b cc a b c d") == ('<attr> <attr> <attr>c <attr>', ['a b', 'a b c', 'a b c', 'a b c d'])

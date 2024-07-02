from ..ruletxt2python import convert_logic_with_indents, process_attributes_csv_buffer

import pytest

@pytest.fixture(autouse=True)
def process_attributes():
    attributes = '''Attribute Text
a thing
b thing
c thing
the partner is not included in the assessment
there will be any change in the LAR client's financial circumstances within the next 12 months
the partner is included in the assessment
there will be any change in the LAR client's or partner's financial circumstances within the next 12 months
'''
    process_attributes_csv_buffer(attributes)

class TestConvertLogic():
    def test_and(self):
        input = '''
a thing and
b thing
and
c thing
'''
        assert convert_logic_with_indents(input) == '''a_thing and
b_thing and
c_thing'''

    def test_all_and(self):
        input = '''
all
    a thing and
    b thing
    and
    c thing
'''
        assert convert_logic_with_indents(input) == '''(
    a_thing and
    b_thing and
    c_thing
)'''

    def test_or(self):
        input = '''
a thing or
b thing
or
c thing
'''
        assert convert_logic_with_indents(input) == '''a_thing or
b_thing or
c_thing'''

    def test_any_or(self):
        input = '''
any
    a thing or
    b thing
    or
    c thing
'''
        assert convert_logic_with_indents(input) == '''(
    a_thing or
    b_thing or
    c_thing
)'''

    def test_nest(self):
        input = '''
a thing and
    b thing
    or
    c thing
'''
        assert convert_logic_with_indents(input) == '''a_thing and
(
    b_thing or
    c_thing
)'''


    def test_realistic(self):
        input = '''
both
    the partner is not included in the assessment and
    there will be any change in the LAR client's financial circumstances within the next 12 months
or
both
    the partner is included in the assessment and
    there will be any change in the LAR client's or partner's financial circumstances within the next 12 months
'''
        assert convert_logic_with_indents(input) == '''(
    the_partner_is_not_included_in_the_assessment and
    there_will_be_any_change_in_the_LAR_client_s_financial_circumstances_within_the_next_12_months
)
or
(
    the_partner_is_included_in_the_assessment and
    there_will_be_any_change_in_the_LAR_client_s_or_partner_s_financial_circumstances_within_the_next_12_months
)'''

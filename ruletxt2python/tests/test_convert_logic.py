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
the MOD309 value
the additional property is Subject Matter of Dispute within the proceedings to which this application relates
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

    def test_either_or(self):
        input = '''
either
    a thing or
    b thing
'''
        assert convert_logic_with_indents(input) == '''(
    a_thing or
    b_thing
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

    def test_operator_expression(self):
        assert convert_logic_with_indents('the MOD309 value <> “MOD309”') == 'the_MOD309_value != "MOD309"'

    def test_is_known(self):
        assert convert_logic_with_indents('it is known whether or not the additional property is Subject Matter of Dispute within the proceedings to which this application relates') == \
            'the_additional_property_is_Subject_Matter_of_Dispute_within_the_proceedings_to_which_this_application_relates != None'

    # def test_exists(self):
    #     assert convert_logic_with_indents('Exists(the inquests, the inquest name is known)') == \
    #         'TheInquest.exists(lambda e: e.the_inquest_name != None)'

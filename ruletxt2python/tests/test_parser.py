from ..parser import parse, TreeNode
from ..ruletxtast2py import Actions

import pytest
import ast


def test_if_simple():
    input = '''[OPM-conclusion]        the_upcoming_changes_section_is_visible if
[OPM-level1]            the_LAR_rules_apply_to_this_application and
[OPM-level1]            some_attribute
'''
    ast_ = parse(input, actions=Actions())
    assert ast.unparse(ast_) == "the_upcoming_changes_section_is_visible = the_LAR_rules_apply_to_this_application and some_attribute\n"

def test_if_nested():
    input = '''[OPM-conclusion]  abc if
[OPM-level1] "z" or
[OPM-level1] all
[OPM-level2(]   "a"
[OPM-level2]    and
[OPM-level2]    "b" and "c"
[OPM-level1)]'''
    ast_ = parse(input, actions=Actions())
    assert ast.unparse(ast_) == "abc = 'z' or ('a' and 'b' and 'c')"

def test_assignment():
    input = '''[OPM-conclusion]        the_version_number_of_the_means_rulebase = "v4.2.8"'''
    ast_ = parse(input, actions=Actions())
    assert ast.unparse(ast_) == "the_version_number_of_the_means_rulebase = 'v4.2.8'"

def test_curly_quotes():
    input = '''[OPM-conclusion] a = “23B”'''
    ast_ = parse(input, actions=Actions())
    assert ast.unparse(ast_) == "a = '23B'"

def test_date():
    input = '''[OPM-conclusion] the_version_date_of_the_means_rulebase = 2024-07-02'''
    ast_ = parse(input, actions=Actions())
    assert ast.unparse(ast_) == '''import datetime
the_version_date_of_the_means_rulebase = datetime.date(2024, 7, 2)'''

def test_two_rules():
    input = '''[OPM-conclusion] a = "1"
[OPM-conclusion] b = "2"
    '''
    ast_ = parse(input, actions=Actions())
    assert ast.unparse(ast_) == "a = '1'\nb = '2'"

from ..parser import parse, TreeNode
from ..ruletxtast2py import Actions

import pytest
import ast

def print_tree(node, label='tree', indent=0):
    if isinstance(node, TreeNode):
        text = node.text
    elif isinstance(node, ast.AST):
        text = ast.unparse(node)
    else:
        text = repr(node)
    print('  ' * indent + f'{label or "unknown":<10}: {text}')
    if label in ('Whitespace', 'Attribute') or not isinstance(node, TreeNode):
        # don't need to recurse further into every character
        return
    labels = [property for property in dir(node) if not property.startswith('__') and property not in ('elements', 'offset', 'text')]
    element_to_label = dict((getattr(node, label), label) for label in labels)
    for i, element in enumerate(node.elements):
        label = element_to_label.get(element, f'{i}')
        print_tree(element, label, indent + 1)

def test_if_simple():
    input = '''[OPM-conclusion]        the_upcoming_changes_section_is_visible if
[OPM-level1]            the_LAR_rules_apply_to_this_application and
[OPM-level1]            some_attribute
'''
    tree = parse(input, actions=Actions())
    print_tree(tree)
    ast_ = tree.elements[0].elements[0]
    #assert ast.dump(ast_) == "Assign(targets=[Name(id='the_upcoming_changes_section_is_visible', ctx=Store())], value=BoolOp(op=And(), values=[Name(id='the_LAR_rules_apply_to_this_application', ctx=Load()), Name(id='some_attribute', ctx=Load())]))"
    assert ast.unparse(ast_) == "the_upcoming_changes_section_is_visible = the_LAR_rules_apply_to_this_application and some_attribute\n"

def test_if_nested():
    input = '''[OPM-conclusion]  abc if
[OPM-level1] "z" or
[OPM-level1] all
[OPM-level2(]   "a"
[OPM-level2]    and
[OPM-level2]    "b" and "c"
[OPM-level1)]'''
    tree = parse(input, actions=Actions())
    print_tree(tree)
    ast_ = tree.elements[0].elements[0]
    # assert ast.dump(ast_) == "Assign(targets=[Name(id='abc', ctx=Store())], value=BoolOp(op=Or(), values=[Constant(value='z'), BoolOp(op=And(), values=[Constant(value='a'), Constant(value='b'), Constant(value='c')])]))"
    assert ast.unparse(ast_) == "abc = 'z' or ('a' and 'b' and 'c')"

def test_assignment():
    input = '''[OPM-conclusion]        the_version_number_of_the_means_rulebase = "v4.2.8"'''
    tree = parse(input, actions=Actions())
    print_tree(tree)
    ast_ = tree.elements[0].elements[0]
    assert ast.unparse(ast_) == "the_version_number_of_the_means_rulebase = 'v4.2.8'"

def test_curly_quotes():
    input = '''[OPM-conclusion] a = “23B”'''
    tree = parse(input, actions=Actions())
    print_tree(tree)
    ast_ = tree.elements[0].elements[0]
    assert ast.unparse(ast_) == "a = '23B'"

def test_date():
    input = '''[OPM-conclusion] the_version_date_of_the_means_rulebase = 2024-07-02'''
    tree = parse(input, actions=Actions())
    print_tree(tree)
    ast_ = tree.elements[0].elements[0]
    assert ast.unparse(ast_) == "the_version_date_of_the_means_rulebase = datetime.date(2024, 7, 2)"
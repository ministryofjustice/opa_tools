from ..parser import parse, TreeNode
from ..ruletxtast2py import Actions

import pytest
import ast

def print_tree(node, label='tree', indent=0):
    if isinstance(node, TreeNode):
        text = node.text
    elif isinstance(node, ast.AST):
        breakpoint()
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

# @pytest.fixture(autouse=True)
# def process_attributes():
#     attributes = '''Attribute Text
# the upcoming changes section is visible
# the LAR rules apply to this application
# the client is passported
# '''
#     process_attributes_csv_buffer(attributes)

def test_if():
    input = '''[OPM-conclusion]        the_upcoming_changes_section_is_visible if
# [OPM-level1]            the_LAR_rules_apply_to_this_application and
# [OPM-level1]            some_attribute
'''
# [OPM-level1]            any
# [OPM-level2]                the_application_is_Special_Children_Act
# [OPM-level2]                or
# [OPM-level2]                the_application_is_Illegal_Immigration_Act
# '''
    expected_output = None

    tree = parse(input, actions=Actions())
    print_tree(tree)
    # breakpoint()

    # pycode = parse(input, )
    # print(pycode)

    # assert tree == expected_output
    raise 0

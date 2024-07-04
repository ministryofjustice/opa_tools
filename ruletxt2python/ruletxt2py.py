from parser_actions import Actions
from ruletxt_parser import parse
from attributes import identify_attributes, attribute_incl_variants_to_variable, attribute_root_name_to_variable

import argparse
import re
import ast



parse_state = None
logic = []
code = []
attributes_converter = None
attributes_pattern = None


def parse_line(input_line):
    '''e.g. "[OPM-conclusion]        the upcoming changes section is visible if"
         -> "[OPM-conclusion]", "the upcoming changes section is visible if"
    '''
    pattern = r"\[(.*?)\]\s*(.*)"
    match = re.match(pattern, input_line)
    assert match, f"Could not parse line: {input_line!r}"
    header, body = match.groups()
    return header, body

def convert_logic_with_indents(input_logic_with_indents):
    # convert indents to levels
    input_logic_by_level = []
    for input_line in input_logic_with_indents.split('\n'):
        if not input_line.strip():
            continue
        pattern = r"(\s*)(.*)"
        match = re.match(pattern, input_line)
        assert match, f"Could not parse line: {input_line!r}"
        indents, input_logic_line = match.groups()
        level = int(len(indents) / 4)
        input_logic_by_level.append((level, input_logic_line))

    return convert_logic(input_logic_by_level)

def convert_logic(input_logic_by_level):
    '''e.g. [(1, "both")
             (2, "the partner is not included in the assessment and")
             (2, "the client owns or have a financial interest in their main dwelling")]
         -> ["(",
             "    not the_partner_is_not_included_in_the_assessment and"
             "    the_client_owns_or_have_a_financial_interest_in_their_main_dwelling"
             ")"]
    '''
    output_logic = []
    line_index = -1
    for level, input_line in input_logic_by_level:
        line_index += 1
        if line_index > 0:
            change_in_line_index = input_logic_by_level[line_index][0] - input_logic_by_level[line_index - 1][0]
            if change_in_line_index == 1:
                # start of sub-logic
                output_logic.append('    ' * (level - 2) + '(')
            elif change_in_line_index == -1:
                # end of sub-logic
                output_logic.append('    ' * (level - 1) + ')')

        canonized_input, attributes = identify_attributes(input_line)
        if canonized_input == '<attr>':
            output_logic.append('    ' * (level) + f'{attribute_incl_variants_to_variable(attributes[0])}')
        else:
            attribute_operator_pattern = r"<attr> (and|or)$"
            match = re.match(attribute_operator_pattern, canonized_input)
            if match:
                operator = match.groups()[0]
                output_logic.append('    ' * (level) + f'{attribute_incl_variants_to_variable(attributes[0])} {operator}')
            else:
                operator_pattern = r"(and|or)"
                match = re.match(operator_pattern, canonized_input)
                if match:
                    operator = match.groups()[0]
                    if output_logic[-1].endswith(')'):
                        output_logic.append('    ' * (level) + f'{operator}')
                    else:
                        output_logic[-1] += f' {operator}'
                else:
                    operator_pattern = r"(any|all|both|either)$"
                    match = re.match(operator_pattern, canonized_input)
                    if match:
                        continue
                    else:
                        pattern1 = r"<attr> (and|or|<>|=) <attr>$"
                        pattern2 = r"<attr> (and|or|<>|=) (.*)$"
                        match1 = re.match(pattern1, canonized_input)
                        match2 = re.match(pattern2, canonized_input)
                        if match1 or match2:
                            operator = match2.groups()[0]
                            if match1:
                                right_hand_expression = attribute_incl_variants_to_variable(attributes[1])
                            else:
                                right_hand_expression = match2.groups()[1]
                                # straighten curly quotes
                                right_hand_expression = re.sub(r'[“”]', '"', right_hand_expression)
                            OPERATOR_CONVERTER = {'<>': '!=', '=': '=='}
                            if operator in OPERATOR_CONVERTER:
                                operator = OPERATOR_CONVERTER[operator]
                            output_logic.append('    ' * (level) + f'{attribute_incl_variants_to_variable(attributes[0])} {operator} {right_hand_expression}')
                        else:
                            pattern = r"it is known whether (or not )?<attr>$"
                            match = re.match(pattern, canonized_input)
                            if match:
                                output_logic.append('    ' * (level) + f'{attribute_incl_variants_to_variable(attributes[0])} != None')
                            else:
                                assert 0, f"Could not parse line: {input_line!r} ({canonized_input})"
    # close any remaining braces
    if level > 0:
        for level in range(level - 1, -1, -1):
            output_logic.append('    ' * (level-1) + ')')
    return '\n'.join(output_logic)


class IfBlockRule(object):
    # [OPM-conclusion]        the upcoming changes section is visible if
    # [OPM-level1]            the LAR rules apply to this application and
    # [OPM-level1]            the client is passported
    def __init__(self, conclusion_line, output):
        self.conclusion = conclusion_line.split(' if')[0]
        self.logic = []  # level, logic_line
        self.output = output

    def add_line(self, header, body):
        level = int(header.split('OPM-level')[1])
        self.logic.append((level, body))

    def finish(self):
        output = [f'{attribute_root_name_to_variable(self.conclusion)} = (']
        logic = convert_logic(self.logic)
        for line in logic.split('\n'):
            output.append(f'{line}')
        self.output.extend(output)

def convert_paragraphs(paragraphs):
        
    for paragraph_index, p in enumerate(paragraphs):
        style = p.style.style_id
        if style == 'OPM-conclusion':
            if parse_state:
                # the end of previous 'if block'
                finish_the_if_block(code, conclusion_attribute, logic)
                parse_state = None

            parse_state = 'if block'
            conclusion_attribute = p.text.split(' if')[0]
        elif style.startswith('OPM-level'):
            if parse_state != 'if block':
                print(f'ERROR, logic outside a block paragraph={paragraph_index} {style=} text={p.text}')
                break
            level = int(style.split('OPM-level')[1])
            logic.append((level, p.text))
        elif style == 'OPM-blankline':
            print('\n')
        elif style in ('OPM-commentary', 'OPM-RuleName') or style.startswith('OPM-Heading') or style.startswith('TOC') or style.startswith('Comment-'):
            if p.text.strip():
                lines = p.text.split('\n')
                for line in lines:
                    print(f'# {line}')
                print('\n')
        else:
            print(f'IGNORE paragraph paragraph={paragraph_index} {style=} text={p.text}')

    if parse_state == 'if block':
        finish_the_if_block(code, conclusion_attribute, logic)


def parse_table(table, table_index):
    code = []
    for row_index, r in enumerate(table.rows):
        row_cells = tuple(c for c in r.cells)
        if len(row_cells) != 2:
            print(f'ERROR, table row has too many cells {table_index=} {row_index=} {len(row_cells)=}')
            return None
        
        cell0_style = row_cells[0].paragraphs[0].style.style_id
        cell1_style = row_cells[1].paragraphs[0].style.style_id    
        # print (f'{cell0_style=} {cell1_style=}')
        if row_index == 0:
            if cell1_style != 'OPM-conclusion':
                print(f'ERROR, table first row should be style: OPM-conclusion {table_index=} {row_index=} {cell0_style=}')
                return None
            conclusion_attribute = row_cells[1].paragraphs[0].text
            code.append(f'{conclusion_attribute} = ')
        elif cell1_style == 'OPM-level1':
            value = row_cells[0].paragraphs[0].text
            condition = row_cells[1].paragraphs[0].text
            if row_index != 1:
                code[-1] += f' else\\'
            code.append(f'    {value} if ({condition})')
        elif cell1_style == 'OPM-Alternativeconclusion':
            value = row_cells[0].paragraphs[0].text
            if row_index != 1:
                code[-1] += f' else\\'
            code.append(f'    {value}')            
        else:
            print(f'ERROR, table unknown style: {table_index=} {row_index=} {cell1_style=}')
            return None
    return code

def convert2python(ruletxt, output_file=None):
    output_lines = []
    current_rule = None
    for line_index, input_line in enumerate(ruletxt.split('\n')):
        # blank lines
        if not input_line.strip():
            # output_lines.append('')
            continue

        header, body = parse_line(input_line)
        
        if header == 'OPM-conclusion':
            if body.endswith(' if'):
                if current_rule:
                    current_rule.finish()
                    current_rule = None
                current_rule = IfBlockRule(body, output_lines)
        elif header.startswith('OPM-level'):
            if not current_rule:
                print(f'ERROR, logic outside a block line={line_index} {input_line}')
                continue
            current_rule.add_line(header, body)
        elif header == 'OPM-blankline':
            output_lines.append('')
        elif header in ('OPM-commentary', 'OPM-RuleName') or header.startswith('OPM-Heading') or header.startswith('TOC') or header.startswith('Comment-'):
            if body.strip():
                breakpoint
                for line in body.split('\n'):
                    output_lines.append(f'# {line}')
        else:
            print(f'IGNORE paragraph line={line_index} {input_line}')

    if current_rule:
        current_rule.finish()
        current_rule = None
        
    output = '\n'.join(output_lines)
    return output

def parse_args():
    parser = argparse.ArgumentParser(description='Convert ruletxt file to python')
    parser.add_argument('attributes_csv_filepath', type=str, help='The attributes CSV file path')
    parser.add_argument('input_filepath', type=str, help='The input ruletxt file path')
    parser.add_argument('-o', '--output_filepath', type=str, help='The output python file path', default=None)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()

    print(args.input_filepath)
    with open(args.input_filepath, 'r') as input_f:
        ruletxt = input_f.read()

    output_python_ast = parse(ruletxt, actions=Actions())
    output_python = ast.unparse(output_python_ast)

    # process_attributes_csv(args.attributes_csv_filepath)

    output = convert2python(ruletxt)

    if args.output_filepath:
        with open(args.output_filepath, 'w') as f:
            f.write(output)
    else:
        print(output)

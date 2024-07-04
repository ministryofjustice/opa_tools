from ruletxt2python.attributes import attribute_incl_variants_to_variable

import ast
from ast import Expr, List, Constant, Load, Name, Store


class Actions(object):
    def __init__(self):
        self.imports = []

    def document(self, input, start, end, elements):
        rules = elements[1]
        body = [element.elements[0] for element in rules.elements]

        imports = [ast.Import(names=[ast.alias(name=import_)]) for import_ in self.imports]
        return PythonFile(imports + body)
    
    def assignment(self, input, start, end, elements):
        attribute = elements[2]
        expression = elements[6]
        return ast.Assign(
            targets=[attribute],
            value=expression,
            lineno=0)

    def if_block(self, input, start, end, elements):
        attribute = elements[2]
        expression = elements[6]
        # OPA's "if" is actually assignment
        return ast.Assign(
            targets=[attribute],
            value=expression,
            lineno=0)
        # return ast.If(test=elements[0].text, body=attribute.text)
        # return f'{elements[3].text} = {elements[0].text}'

    def expression(self, input, start, end, elements):
        return elements[1]

    def operator_expression(self, input, start, end, elements):
        expressions = [elements[4]]
        loop = elements[7]
        operator = loop.elements[0].Operator
        expressions.extend(
            [element.Expression for element in loop.elements]
        )

        if operator.text == 'and':
            op = ast.And()
        elif operator.text == 'or':
            op = ast.Or()
        else:
            raise NotImplementedError()
        return ast.BoolOp(
                op=op,
                values=expressions,
                type_ignores=[])

    def bracketed_operator_expression(self, input, start, end, elements):
        expressions = [
            elements[5]
        ]
        loop = elements[8]
        operator = loop.elements[0].Operator
        expressions.extend(
            [element.Expression for element in loop.elements]
        )

        # todo more expressions
        if operator.text == 'and':
            op = ast.And()
        elif operator.text == 'or':
            op = ast.Or()
        else:
            raise NotImplementedError()
        return ast.BoolOp(
                op=op,
                values=expressions,
                type_ignores=[])

    def comment(self, input, start, end, elements):
        comment_text = elements[2]
        return Comment(comment_text.text)

    def empty_conclusion(self, input, start, end, elements):
        return Comment('')

    def string(self, input, start, end, elements):
        name = elements[1].text
        return ast.Constant(value=name)

    def date(self, input, start, end, elements):
        year, month, day = int(elements[0].text), int(elements[2].text), int(elements[4].text)
        self.imports.append('datetime')
        return ast.Call(func=ast.Attribute(value=Name(id='datetime', ctx=Load()), attr='date', ctx=Load()), args=[
            Constant(value=year), Constant(value=month), Constant(value=day)
            ], keywords=[])

    def attribute(self, input, start, end, elements):
        name = ''.join((e.text for e in elements))
        name = attribute_incl_variants_to_variable(name)
        return Name(id=name, ctx=Store())

class PythonFile(object):
    # Can't represent a python file as ast.Module, because an AST doesn't include comments.
    # So create our own object containing a list of AST elements and comments.
    def __init__(self, statements):
        self.statements = statements  # list of ASTs and Comments

    def get_code(self):
        code_string = ''
        for statement in self.statements:
            if isinstance(statement, ast.AST):
                code_string += ast.unparse(statement) + '\n'
            elif isinstance(statement, Comment):
                code_string += statement.get_code() + '\n'
        return code_string

class Comment(object):
    def __init__(self, comment_string):
        assert isinstance(comment_string, str)
        self.comment_string = comment_string

    def get_code(self):
        return f'# {self.comment_string}'.rstrip()

import ast
from ast import Expr, List, Constant, Load, Name, Store

class Actions(object):
    def document(self, input, start, end, elements):
        rule = elements[1]
        return rule
    
    def if_block(self, input, start, end, elements):
        attribute = elements[2]
        expression = elements[6]
        return ast.Assign(
            targets=[attribute],
            value=expression, #Constant(value=True),
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

    def string(self, input, start, end, elements):
        name = elements[1].text
        return ast.Constant(value=name)

    def attribute(self, input, start, end, elements):
        name = ''.join((e.text for e in elements))
        return Name(id=name, ctx=Store())

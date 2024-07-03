import ast
from ast import Expr, List, Constant, Load, Name, Store

class Actions(object):
    def make_if(self, input, start, end, elements):
        attribute = elements[0]
        return ast.Assign(
            targets=[Name(id=attribute.text, ctx=Store())],
            value=Constant(value=True),
            lineno=0)
        # return ast.If(test=elements[0].text, body=attribute.text)
        # return f'{elements[3].text} = {elements[0].text}'
    
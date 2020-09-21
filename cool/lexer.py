from .cmp import Grammar, LR1Parser

class Node:
    pass

class ProgramNode(Node):
    def __init__(self, declarations):
        self.declarations = declarations
        self.line = declarations[0].line
        self.column = declarations[0].column

class DeclarationNode(Node):
    pass

class ClassDeclarationNode(DeclarationNode):
    def __init__(self, idx, features, parent=None):
        self.id = idx
        self.parent = parent
        self.features = features
        self.line = idx.line
        self.column = idx.column

class AttrDeclarationNode(DeclarationNode):
    def __init__(self, idx, typex, expression=None):
        self.id = idx
        self.type = typex
        self.expression = expression
        self.line = idx.line
        self.column = idx.column

class FuncDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, return_type, body):
        self.id = idx
        self.params = params
        self.type = return_type
        self.body = body
        self.line = idx.line
        self.column = idx.column

class ExpressionNode(Node):
    pass

class IfThenElseNode(ExpressionNode):
    def __init__(self, condition, if_body, else_body):
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body
        self.line = condition.line
        self.column = condition.column

class WhileLoopNode(ExpressionNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
        self.line = condition.line
        self.column = condition.column
        

class BlockNode(ExpressionNode):
    def __init__(self, expressions):
        self.expressions = expressions
        self.line = expressions[-1].line
        self.column = expressions[-1].column

class LetInNode(ExpressionNode):
    def __init__(self, let_body, in_body):
        self.let_body = let_body
        self.in_body = in_body
        self.line = in_body.line
        self.column = in_body.column

class CaseOfNode(ExpressionNode):
    def __init__(self, expression, branches):
        self.expression = expression
        self.branches = branches
        self.line = expression.line
        self.column = expression.column

class AssignNode(ExpressionNode):
    def __init__(self, idx, expression):
        self.id = idx
        self.expression = expression
        self.line = idx.line
        self.column = idx.column

class UnaryNode(ExpressionNode):
    def __init__(self, expression):
        self.expression = expression
        self.line = expression.line
        self.column = expression.column

class NotNode(UnaryNode):
    pass

class BinaryNode(ExpressionNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.line = left.line
        self.column = left.column

class LessEqualNode(BinaryNode):
    pass

class LessNode(BinaryNode):
    pass

class EqualNode(BinaryNode):
    pass

class ArithmeticNode(BinaryNode):
    pass

class PlusNode(ArithmeticNode):
    pass

class MinusNode(ArithmeticNode):
    pass

class StarNode(ArithmeticNode):
    pass

class DivNode(ArithmeticNode):
    pass

class IsVoidNode(UnaryNode):
    pass

class ComplementNode(UnaryNode):
    pass

class FunctionCallNode(ExpressionNode):
    def __init__(self, obj, idx, args, typex=None):
        self.obj = obj
        self.id = idx
        self.args = args
        self.type = typex
        self.line = idx.line
        self.column = idx.column

class MemberCallNode(ExpressionNode):
    def __init__(self, idx, args):
        self.id = idx
        self.args = args
        self.line = idx.line
        self.column = idx.column

class NewNode(ExpressionNode):
    def __init__(self, typex):
        self.type = typex
        self.line = typex.line
        self.column = typex.column

class AtomicNode(ExpressionNode):
    def __init__(self, token):
        self.token = token
        self.line = token.line
        self.column = token.column

class IntegerNode(AtomicNode):
    pass

class IdNode(AtomicNode):
    pass

class StringNode(AtomicNode):
    pass

class BoolNode(AtomicNode):
    pass


# grammar 
CoolGrammar = Grammar()

#non-terminals
program = CoolGrammar.NonTerminal('<program>', startSymbol=True)
class_list, def_class = CoolGrammar.NonTerminals('<class-list> <def-class>')
feature_list, feature = CoolGrammar.NonTerminals('<feature-list> <feature>')
param_list, param = CoolGrammar.NonTerminals('<param-list> <param>')
expr, member_call, expr_list, let_list, case_list = CoolGrammar.NonTerminals('<expr> <member-call> <expr-list> <let-list> <case-list>')
truth_expr, comp_expr = CoolGrammar.NonTerminals('<truth-expr> <comp-expr>')
arith, term, factor, factor_2 = CoolGrammar.NonTerminals('<arith> <term> <factor> <factor-2>')
atom, func_call, arg_list = CoolGrammar.NonTerminals('<atom> <func-call> <arg-list>')

#terminals
classx, inherits = CoolGrammar.Terminals('class inherits')
ifx, then, elsex, fi = CoolGrammar.Terminals('if then else fi')
whilex, loop, pool = CoolGrammar.Terminals('while loop pool')
let, inx = CoolGrammar.Terminals('let in')
case, of, esac = CoolGrammar.Terminals('case of esac')



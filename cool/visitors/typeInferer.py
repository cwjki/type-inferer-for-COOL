from cool.cmp import visitor, ErrorType, SelfType, AutoType, SemanticError
from cool.ast import *
from cool.errors import INFERENCE_ON, INF_ATTR, INF_PARAM, INF_RETRN, INF_VAR

class TypeInferer:
    def __init__(self, context, errors=[], inferences=[]):
        self.context = context
        self.errors = errors
        self.inferences = inferences
        self.current_type = None 
        self.current_method = None

        self.int_type = self.context.get_type('Int')
        self.string_type = self.context.get_type('String')
        self.bool_type = self.context.get_type('Bool')
        self.object_type = self.context.get_type('Object')
        self.io_type = self.context.get_type('IO')

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node, scope):
        self.changed = False

        for declaration, child_scope in zip(node.declarations, scope.children):
            self.visit(declaration, child_scope)

        return self.changed

    @visitor.when(ClassDeclarationNode)
    def visit(self, node, scope):
        self.current_type = self.context.get_type(node.id.lex)

        for feature, child_scope in zip(node.features, scope.children):
            self.visit(feature, child_scope)
        
        for attr, var in zip(self.current_type.attributes, scope.locals):
            if var.infer_type():
                self.changed = True
                attr.type = var.type
                self.inferences.append(INF_ATTR % (self.current_type.name, attr.name, var.type.name))

    @visitor.when(AttrDeclarationNode)
    def visit(self, node, scope):
        expr = node.expression
        if expr:
            attr = self.current_type.get_attribute(node.id.lex)
            self.visit(expr, scope.children[0], attr.type)
            expr_type = expr.static_type

            var = scope.find_variable(node.id.lex)
            var.set_upper_type(expr_type)
            if var.infer_type():
                self.changed = True
                attr.type = var.type
                self.inferences.append(INF_ATTR % (self.current_type.name, attr.name, var.type.name))

    @visitor.when(FuncDeclarationNode)
    def visit(self, node, scope):
        self.current_method = self.current_type.get_method(node.id.lex)
        return_type = self.current_method.return_type
        return_type = self.current_type if isinstance(return_type, SelfType) else return_type
        
        self.visit(node.body, scope.children[0], self.current_type, return_type)
        body_type = node.body.static_type

        for i, var in enumerate(scope.locals[1:]):
            if var.infer_type():
                self.changed = True
                self.current_method.param_types[i] = var.type
                self.inferences.append(INF_PARAM % (self.current_method.name, self.current_type.name, var.name, var.type.name))

        var = self.current_method.return_info
        var.set_lower_type(body_type)
        if var.infer_type():
            self.changed = True
            self.current_method.return_type = var.type
            self.inferences.append(INF_RETRN % (self.current_method.name, self.current_type.name, var.type.name,))

    @visitor.when(IfThenElseNode)
    def visit(self, node, scope, expected_type=None):
        self.visit(node.condition, scope.children[0], self.bool_type)
        self.visit(node.if_body, scope.children[1])
        self.visit(node.else_body, scope.children[2])

        if_type = node.if_body.static_type
        else_type = node.else_body.static_type
        node.static_type = if_type.type_union(else_type)

    @visitor.when(WhileLoopNode)
    def visit(self, node, scope, expected_type=None):
        self.visit(node.condition, scope.children[0], self.bool_type)
        self.visit(node.body, scope.children[1])
        node.static_type = self.object_type

    @visitor.when(BlockNode)
    def visit(self, node, scope, expected_type=None):
        for expr, child_scope in zip(node.expressions[:-1], scope.children[:-1]):
            self.visit(expr, child_scope)
        
        self.visit(node.expressions[-1], scope.children[-1], expected_type)
        node.static_type = node.expressions[-1].static_type

    @visitor.when(LetInNode)
    def visit(self, node, scope, expected_type=None):
        for (idx, typex, expr), child_scope, (i, var) in zip(node.let_body, scope.children[:-1], enumerate(scope.locals)):
            if expr:
                self.visit(expr, child_scope, var.type if var.infered else None)
                expr_type = expr.static_type

                var,set_upper_type(expr_type)
                if var.infer_type():
                    self.changed = True
                    typex.name = var.type.name
                    self.inferences.append(INFERENCE_ON % (idx.line, idx.column) + INF_VAR % (var.name, var.type.name))

        self.visit(node.in_body, scope.children[-1], expected_type)

        for i, var in enumerate(scope.locals):
            if var.infer_type():
                self.changed = True
                idx, typex, _ = node.let_body[i]
                typex.name = var.type.name
                self.inferences.append(INFERENCE_ON % (idx.line, idx.column) + INF_VAR % (var.name, var.type))

        node.static_type = node.in_body.static_type

    @visitor.when(CaseOfNode)
    def visit(self, node, scope, expected_type=None):
        self.visit(node.expression, scope.children[0])
        node.static_type = None

        for (idx, typex, expr), child_scope in zip(node.branches, scope.children[1:]):
            self.visit(expr, child_scope)
            expr_type = expr.static_type
            node.static_type = node.static_type.type_union(expr_type) if node.static_type else expr_type
        


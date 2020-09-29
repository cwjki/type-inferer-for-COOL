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














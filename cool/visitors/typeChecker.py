from cool.cmp import visitor, ErrorType, SelfType, AutoType, SemanticError, Scope
from cool.ast import *
from cool.errors import ERROR_ON, WRONG_SIGNATURE, SELF_IS_READONLY, LOCAL_ALREADY_DEFINED, INCOMPATIBLE_TYPES, VARIABLE_NOT_DEFINED, INVALID_OPERATION, CYCLIC_INHERITANCE

class TypeChecker:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.current_method = None
        self.errors = errors

        self.int_type = self.context.get_type('Int')
        self.string_type = self.context.get_type('String')
        self.bool_type = self.context.get_type('Bool')
        self.object_type = self.context.get_type('Object')
        self.io_type = self.context.get_type('IO')
    
    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node, scope = None):
        scope = Scope()
        for declaration in node.declarations:
            self.visit(declaration, scope.create_child())
        return scope

    @visitor.when(ClassDeclarationNode)
    def visit(self, node, scope):
        self.current_type = self.context.get_type(node.id.lex)

        parent = self.current_type.parent
        while parent:
            if parent == self.current_type:
                self.errors.append(ERROR_ON % (node.line, node.column) + CYCLIC_INHERITANCE % (parent.name))
                self.current_type.parent = self.object_type
                break

            parent = parent.parent

        for attr in self.current_type.attributes:
            scope.define_variable(attr.name, attr.type)

        for feature in node.features:
            self.visit(feature, scope.create_child())

    @visitor.when(AttrDeclarationNode)
    def visit(self, node, scope):
        expr = node.expression
        if expr:
            self.visit(expr, scope.create_child())
            expr_type = expr.static_type

            attr = self.current_type.get_atrribute(node.id.lex)
            node_type = attr.type
            node_type = self.current_type if isinstance(node_type, SelfType) else node_type
            if not expr_type.conforms_to(node_type):
                self.errors.append(ERROR_ON % (expr.line, expr.column) + INCOMPATIBLE_TYPES % (expr_type.name, node_type.name))
    
    @visitor.when(FuncDeclarationNode)
    def visit(self, node, scope):
        self.current_method = self.current_type.get_method(node.id.lex)

        parent = self.current_type.parent
        if parent:
            try:
                parent_method = parent.get_method(node.id.lex)
            except SemanticError:
                pass
            else:
                if parent_method.param_types != self.current_method.param_types or parent_method.return_type != self.current_method.return_type:
                    self.errors.append(ERROR_ON % (node.line, node.column) + WRONG_SIGNATURE % (self.current_method.name, self.current_type.name, parent.name))

        scope.define_variable('self', self.current_type)

        for pname, ptype in zip(self.current_method.param_names, self.current_method.param_types):
            scope.define_variable(pname, ptype)
        
        body = node.body
        self.visit(body, scope.create_child())

        body_type = body.static_type
        return_type = self.current_type if isinstance(self.current_method.return_type, SelfType) else self.current_method.return_type

        if not body_type.conforms_to(return_type):
            self.errors.append(ERROR_ON % (body.line, body.column) + INCOMPATIBLE_TYPES % (body_type.name, return_type.name))


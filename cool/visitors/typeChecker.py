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

    @visitor.when(IfThenElseNode)
    def visit(self, node, scope):
        condition = node.condition
        self.visit(node.condition, scope.create_child())
        condition_type = condition.static_type

        if not condition_type.conforms_to(self.bool_type):
            self.errors.append(ERROR_ON % (condition.line, condition.column) + INCOMPATIBLE_TYPES % (condition_type.name, self.bool_type.name))

        self.visit(node.if_body, scope.create_child())
        if_type = node.if_body.static_type

        self.visit(node.else_body, scope.create_child())
        else_type = node.else_body.static_type

        node.static_type = if_type.type_union(else_type)

    @visitor.when(WhileLoopNode)
    def visit(self, node, scope):
        condition = node.condition
        self.visit(condition, scope.create_child())
        condition_type = condition.static_type

        if not condition_type.conforms_to(self.bool_type):
            self.errors.append(ERROR_ON % (condition.line, condition.column) + INCOMPATIBLE_TYPES % (condition_type.name, self.bool_type.name))

        self.visit(node.body, scope.create_child())
        node.static_type = self.object_type

    @visitor.when(BlockNode)
    def visit(self, node, scope):
        for expr in node.expressions:
            self.visit(expr, scope.create_child())
        
        node.static_type = node.expressions[-1].static_type

    @visitor.when(LetInNode)
    def visit(self, node, scope):
        for idx, typex, expr in node.let_body:
            try:
                node_type = self.context.get_type(typex.lex)
            except SemanticError as error:
                self.errors.append(ERROR_ON % (typex.line, typex.column) + error.text)
                node_type = ErrorType()

            id_type = self.current_type if isinstance(node_type, SelfType) else node_type
            child_scope = scope.create_child()

            if expr:
                self.visit(expr, child_scope)
                expr_type = expr.static_type
                if not expr_type.conforms_to(id_type):
                    self.errors.append(ERROR_ON % (expr.line, expr.column) + INCOMPATIBLE_TYPES % (expr_type.name, id_type.name))
            
            scope.define_variable(idx.lex, id_type)
        
        self.visit(node.in_body, scope.create_child())
        node.static_type = node.in_body.static_type

    @visitor.when(CaseOfNode)
    def visit(self, node, scope):
        self.visit(node.expression, scope.create_child())

        node.static_type = None
        for idx, typex, expr in node.branches:
            try:
                node_type = self.context.get_type(typex.lex)
            except SemanticError as error:
                self.errors.append(ERROR_ON % (typex.line, typex.column) + error.lex)
            else:
                if isinstance(node_type, SelfType) or isinstance(node_type, AutoType):
                    self.errors.append(ERROR_ON % (typex.line, typex.column) + f'Type "{node_type.name}" cannot be used as case branch type.')
                    node_type = ErrorType()

            id_type = node_type

            child_scope = scope.create_child()
            child_scope.define_variable(idx.lex, id_type)
            self.visit(expr, child_scope)
            expr_type = expr.static_type

            node.static_type = node.static_type.type_union(expr_type) if node.static_type else expr_type
        
    @visitor.when(AssignNode)
    def visit(self, node, scope):
        expr = node.expression
        self.visit(expr, scope.create_child())
        expr_type = expr.static_type

        if scope.is_defined(node.id.lex):
            var = scope.find_variable(node.id.lex)
            node_type = var.type

            if var.name == 'self':
                self.errors.append(ERROR_ON % (node.line, node.column) + SELF_IS_READONLY)
            elif not expr_type.conforms_to(node_type):
                self.errors.append(ERROR_ON % (expr.line, expr.column) + INCOMPATIBLE_TYPES % (expr_type.name, node_type.name))
        else:
            self.errors.append(ERROR_ON % (node.line, node.column) + VARIABLE_NOT_DEFINED % (node.id.lex, self.current_method.name))

        node.static_type = expr_type

    @visitor.when(NotNode)
    def visit(self, node, scope):
        expr = node.expression
        self.visit(expr, scope.create_child())
        expr_type = expr.static_type

        if not expr_type.conforms_to(self.bool_type):
            self.errors.append(ERROR_ON % (expr.line, expr.column) + INCOMPATIBLE_TYPES % (expr_type.name, self.bool_type.name))

        node.static_type = self.bool_type
        
          

from cool.cmp import ErrorType, SelfType, SemanticError, visitor
from cool.ast import ProgramNode, ClassDeclarationNode, AttrDeclarationNode, FuncDeclarationNode
from cool.errors import ERROR_ON

class TypeBuilder:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.errors = errors

        self.object_type = self.context.get_type('Object')
        
        self.int_type = self.context.get_type('Int')
        self.int_type.set_parent(self.object_type)
        self.int_type.sealed = True

        self.string_type = self.context.get_type('String')
        self.string_type.set_parent(self.object_type)
        self.string_type.sealed = True

        self.bool_type = self.context.get_type('Bool')
        self.bool_type.set_parent(self.object_type)
        self.bool_type.sealed = True

        self.io_type = self.context.get_type('IO')
        self.io_type.set_parent(self.object_type)

        self.object_type.define_method('abort', [], [], self.object_type)
        self.object_type.define_method('type_name', [], [], self.string_type)
        self.object_type.define_method('copy', [], [], SelfType())

        self.string_type.define_method('length', [], [], self.int_type)
        self.string_type.define_method('concat', ['s'], [self.string_type], self.string_type)
        self.string_type.define_method('substr', ['i', 'l'], [self.int_type, self.int_type], self.string_type)

        self.io_type.define_method('out_string', ['x'], [self.string_type], SelfType())
        self.io_type.define_method('out_int', ['x'], [self.int_type], SelfType())
        self.io_type.define_method('in_string', [], [], self.string_type)
        self.io_type.define_method('in_int', [], [], self.int_type)


    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node):
        for class_def in node.declaration:
            self.visit(class_def)

        try:
            self.context.get_type('Main').get_method('main')
        except SemanticError:
            self.errors.append(ERROR_ON % (node.line, node.column) + 'Every program must have a class Main with a method main.')

    @visitor.when(ClassDeclarationNode)
    def visit(self, node):
        self.current_type = self.context.get_type(node.id.lex)

        parent = node.parent
        if parent:
            try:
                parent_type = self.context.get_type(parent.lex)
                self.current_type.set_parent(parent_type)
            except SemanticError as error:
                self.errors.append(ERROR_ON % (parent.line, parent.column) + error.text)
        else:
            self.current_type.set_parent(self.object_type)

        for feature in node.feature:
            self.visit(feature)
        
    @visitor.when(AttrDeclarationNode)
    def visit(self, node):
        try:
            attr_type = self.context.get_type(node.type.lex)
        except SemanticError as error:
            self.errors.append(ERROR_ON % (node.line, node.column) + error.text)
            attr_type = ErrorType()

        try:
            self.current_type.define_attribute(node.id.lex, attr_type)
        except SemanticError as error:
            self.errors.append(ERROR_ON % (node.line, node.column) + error.text)


    @visitor.when(FuncDeclarationNode)
    def visit(self, node):
        arg_names, arg_types = [], []
        for idx, typex in node.params:
            try:
                arg_type = self.context.get_type(typex.lex)
            except SemanticError as error:
                self.errors.append(ERROR_ON % (node.line, node.column) + error.text)
                arg_type = ErrorType()
            else:
                if isinstance(arg_type, SelfType):
                    self.errors.append(ERROR_ON % (node.line, node.column) + f'Type "{arg_type.name}" can not be used as a parameter type')
                    arg_type = ErrorType()
            
            arg_names.append(idx.lex)
            arg_types.append(arg_type)
        
        try:
            return_type = self.context.get_type(node.type.lex)
        except SemanticError as error:
            self.errors.append(ERROR_ON % (node.line, node.column) + error.text)
            return_type = ErrorType()
        
        try:
            self.current_type.define_method(node.id.lex, arg_names, arg_types, return_type)
        except SemanticError as error:
            self.errors.append(ERROR_ON % (node.line, node.column) + error.text)
        

from cool.cmp import visitor, Context, SelfType, AutoType, SemanticError
from cool.ast import ProgramNode, ClassDeclarationNode
from cool.errors import ERROR_ON

class TypeCollector():
    def __init__(self, errors = []):
        self.context = Context()
        self.errors = errors

        self.context.create_type('Int')
        self.context.create_type('String')
        self.context.create_type('Bool')
        self.context.create_type('Object')
        self.context.create_type('IO')

        self.context.add_type(SelfType())
        self.context.add_type(AutoType())

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node):
        for class_def in node.declarations:
            self.visit(class_def)

    @visitor.when(ClassDeclarationNode)
    def visit(self, node):
        try:
            self.context.create_type(node.id.lex)
        except SemanticError as error:
            self.errors.append(ERROR_ON % (node.line, node.column) + error)
    

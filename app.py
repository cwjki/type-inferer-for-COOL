from flask import Flask, render_template, url_for, request, redirect
from cool import evaluate_reverse_parse
from cool import LR1Parser
from cool import CoolGrammar
from cool import tokenizer
from cool import FormatVisitor, TypeCollector, TypeBuilder, TypeChecker, TypeInferer

import sys

class Parsing_Error():
    pass
class Result():
    pass

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    try:
        if request.method == 'POST':

            code = request.form['code']
            tokens = tokenizer(code)
            CoolParser = LR1Parser(CoolGrammar)
            parse, operations = CoolParser(tokens)
            if not operations:
                parsing_error = Parsing_Error()
                parsing_error.token = parse.lex
                parsing_error.line = parse.line
                parsing_error.column = parse.column
                return render_template('index.html', parsing_error=parsing_error)

            result = Result()

            ast = evaluate_reverse_parse(parse, operations, tokens)
            formatter = FormatVisitor()
            result.tree = formatter.visit(ast)
            
            errors = []
            # TYPE COLLECTOR
            collector = TypeCollector(errors)
            collector.visit(ast)
            context = collector.context
            result.collector_errors = errors
            result.collector_context = context

            # TYPE BUILDER
            builder = TypeBuilder(context, errors)
            builder.visit(ast)
            result.builder_errors = errors[len(result.collector_errors):]
            result.builder_context = context

            # TYPE CHECKER
            checker = TypeChecker(context, errors)
            scope = checker.visit(ast)
            result.checker_errors = errors[len(result.collector_errors) + len(result.builder_errors):]
            result.checker_context = context

            result.errors = errors

            # TYPE INFERER
            inferences = []
            inferer = TypeInferer(context, errors, inferences)
            while inferer.visit(ast, scope): pass

            result.inferences = inferences
            result.inferer_context = context
            
            return render_template('index.html', parsing_error=None, result=result)
        
        else:
            return render_template('index.html', parsing_error=None )
    
    except:
        print("Error", sys.exc_info()[0])
        return render_template('index.html', parsing_error=None )


if __name__ == "__main__":
    app.run(debug=True)
    
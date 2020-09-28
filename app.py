from flask import Flask, render_template, url_for, request, redirect
from cool import evaluate_reverse_parse
from cool import LR1Parser
from cool import CoolGrammar
from cool import tokenizer
from cool import FormatVisitor, TypeCollector, TypeBuilder, TypeChecker

import sys

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
                #Error
                return

            ast = evaluate_reverse_parse(parse, operations, tokens)
            formatter = FormatVisitor()
            tree = formatter.visit(ast)

            errors = []
            collector = TypeCollector(errors)
            collector.visit(ast)
            context = collector.context

            builder = TypeBuilder(context, errors)
            builder.visit(ast)

            checker = TypeChecker(context, errors)
            scope = checker.visit(ast)
            
            print("Fin")
            
            return render_template('index.html', boolean=False )
        
        else:
            return render_template('index.html', boolean=False )
    
    except:
        print("Error", sys.exc_info()[0])
        return render_template('index.html', boolean=False )


if __name__ == "__main__":
    app.run(debug=True)
    
from flask import Flask, render_template, url_for, request, redirect
from cool.cmp.evaluation import evaluate_reverse_parse
from cool.cmp.grammartools import LR1Parser
from cool.coolGrammar import CoolGrammar
from cool.lexer import tokenizer
from cool import FormatVisitor

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
            print(tree)

            
            return render_template('index.html', boolean=False )
        
        else:
            return render_template('index.html', boolean=False )
    
    except:
        return render_template('index.html', boolean=False )


if __name__ == "__main__":
    app.run(debug=True)
    
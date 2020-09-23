from flask import Flask, render_template, url_for, request, redirect
from cool import coolAnalyzer

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    try:
        if request.method == 'POST':
            return render_template('index.html', boolean=False )
        
        else:
            return render_template('index.html', boolean=False )
    
    except:
        return render_template('index.html', boolean=False )


if __name__ == "__main__":
    app.run()
    
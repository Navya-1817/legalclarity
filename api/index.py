from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Hello from Vercel!</h1><p>Flask is working correctly.</p>'

@app.route('/test')
def test():
    return {'status': 'ok', 'message': 'Basic Flask app is working'}

if __name__ == '__main__':
    app.run()

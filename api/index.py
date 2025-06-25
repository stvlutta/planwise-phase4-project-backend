from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def health_check():
    return jsonify({'message': 'PlanWise Backend API is running on Vercel!', 'status': 'healthy'})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/test')
def test():
    return jsonify({'message': 'Test endpoint working!'})

# Vercel entry point
def handler(request):
    return app(request)

if __name__ == '__main__':
    app.run(debug=True)
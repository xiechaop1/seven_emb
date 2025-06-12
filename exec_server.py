from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

@app.route('/api/version', methods=['GET'])
def get_version():
    if not os.path.exists('version.json'):
        return jsonify({'error': 'version.json not found'}), 404
    with open('version.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) 
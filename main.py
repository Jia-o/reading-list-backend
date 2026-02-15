import os
import random
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
from googleapiclient.discovery import build
from google.oauth2 import service_account

app = Flask(__name__)
CORS(app)  # This allows your frontend to talk to this API

# 1. Setup Google Auth
# On Render, you will store your Service Account JSON in an Environment Variable
SERVICE_ACCOUNT_INFO = os.environ.get('GOOGLE_CREDS') 
DOCUMENT_ID = os.environ.get('DOC_ID')

def get_docs_service():
    # Parse the credentials from the environment variable
    import json
    info = json.loads(SERVICE_ACCOUNT_INFO)
    creds = service_account.Credentials.from_service_account_info(info)
    return build('docs', 'v1', credentials=creds)

@app.route('/get-link', methods=['GET'])
def get_link():
    service = get_docs_service()
    doc = service.documents().get(documentId=DOCUMENT_ID).execute()
    
    content = doc.get('body').get('content')
    readings = []

    # Simple Parsing Logic
    for element in content:
        if 'paragraph' in element:
            text = ""
            for run in element['paragraph']['elements']:
                if 'textRun' in run:
                    text += run['textRun']['content']
            
            # Look for lines like: [Title](URL) #Theme
            # Match pattern: URL inside () and themes starting with #
            url_match = re.search(r'\((https?://[^\)]+)\)', text)
            if url_match:
                url = url_match.group(1)
                themes = re.findall(r'#(\w+)', text.lower())
                readings.append({"url": url, "themes": themes})

    # Filter by vibe if requested
    vibe = request.args.get('vibe')
    if vibe:
        readings = [r for r in readings if vibe.lower() in r['themes']]

    if not readings:
        return jsonify({"error": "No matching readings found"}), 404

    return jsonify(random.choice(readings))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
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

@app.route('/get-data', methods=['GET'])
def get_data():
    service = get_docs_service()
    doc = service.documents().get(documentId=DOCUMENT_ID).execute()
    content = doc.get('body').get('content')
    
    readings = []
    all_tags = set()

    for element in content:
        if 'paragraph' in element:
            # We need to collect the text and the link separately
            full_text = ""
            extracted_link = None
            
            for run in element['paragraph']['elements']:
                text_run = run.get('textRun', {})
                text_content = text_run.get('content', "")
                full_text += text_content
                
                # Check if this specific run of text has a link attached
                # Most often, the link is on the 'Title' part before the '|'
                style = text_run.get('textStyle', {})
                if 'link' in style:
                    extracted_link = style['link'].get('url')

            if "|" in full_text:
                parts = full_text.split("|")
                title = parts[0].strip()
                
                # Extract tags from the second half (after the |)
                tags = re.findall(r'#(\w+)', parts[1].lower())
                for t in tags: 
                    all_tags.add(t)

                if title:
                    readings.append({
                        "title": title,
                        "url": extracted_link, # This is the URL pulled from the Title style
                        "themes": tags
                    })

    return jsonify({
        "readings": readings,
        "tags": sorted(list(all_tags))
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
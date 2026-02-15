import os
import random
import re
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from googleapiclient.discovery import build
from google.oauth2 import service_account

app = Flask(__name__)
CORS(app)

SERVICE_ACCOUNT_INFO = os.environ.get('GOOGLE_CREDS') 
DOCUMENT_ID = os.environ.get('DOC_ID')

def get_docs_service():
    info = json.loads(SERVICE_ACCOUNT_INFO)
    creds = service_account.Credentials.from_service_account_info(info)
    return build('docs', 'v1', credentials=creds)

@app.route('/get-data', methods=['GET'])
def get_data():
    try:
        service = get_docs_service()
        doc = service.documents().get(documentId=DOCUMENT_ID).execute()
        content = doc.get('body').get('content')
        
        readings = []
        all_tags = set()

        for element in content:
            if 'paragraph' in element:
                full_text = ""
                extracted_link = None
                
                # We loop through elements to find the link and build the text
                for run in element['paragraph']['elements']:
                    text_run = run.get('textRun', {})
                    text_content = text_run.get('content', "")
                    full_text += text_content
                    
                    # Google Docs often puts the link style on the Title run
                    style = text_run.get('textStyle', {})
                    if 'link' in style:
                        extracted_link = style['link'].get('url')

                # CLEANING STEP:
                # Remove actual newlines and those weird non-breaking spaces (\xa0)
                clean_line = full_text.replace('\n', ' ').replace('\xa0', ' ').strip()

                if "|" in clean_line:
                    parts = clean_line.split("|")
                    title = parts[0].strip()
                    
                    # Use a more flexible Regex for tags: 
                    # Looks for # followed by alphanumeric characters
                    tags = re.findall(r'#(\w+)', parts[1].lower())
                    
                    for t in tags: 
                        all_tags.add(t)

                    if title:
                        readings.append({
                            "title": title,
                            "url": extracted_link,
                            "themes": tags
                        })

        print(f"Successfully parsed {len(readings)} articles and {len(all_tags)} tags.")
        return jsonify({
            "readings": readings,
            "tags": sorted(list(all_tags))
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
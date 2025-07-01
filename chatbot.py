from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import re
import difflib

app = Flask(__name__)
CORS(app)

# Absolute path to PDF folder
BASE_DIR = os.path.join(os.getcwd(), "pdfs")

# Clean user query
def clean_text(text):
    noise = ['pdf', 'notes', 'note', 'give', 'me', 'download', 'file', 'semester', 'sem', 'please']
    words = re.findall(r'\b\w+\b', text.lower())
    return [w for w in words if w not in noise]

# Match similar words
def find_best_match(word, options):
    matches = difflib.get_close_matches(word, options, n=1, cutoff=0.6)
    return matches[0] if matches else None

@app.route('/getpdf', methods=['POST'])
def get_pdf():
    data = request.json
    query = data.get('query', '').lower()
    words = clean_text(query)

    # Clean keywords
    subjects = ['sql', 'python', 'bcom', 'ba', 'nda', 'flipflop', 'dsa', 'oops', 'financialaccounting']
    semesters = ['1st', '2nd', '3rd', '4th', '5th', '6th', '1', '2', '3', '4']
    languages = ['english', 'hindi']

    subject = semester = language = None

    for word in words:
        if not subject:
            subject = find_best_match(word, subjects)
        if not semester and word in semesters:
            semester = word
        if not language and word in languages:
            language = word

    try:
        matching_links = []
        for filename in os.listdir(BASE_DIR):
            name = filename.lower()

            # CASE 1: exact or fuzzy matched subject
            if (subject in name if subject else False) and \
               (semester in name if semester else True) and \
               (language in name if language else True):
                file_url = f"http://127.0.0.1:5000/download/{filename}"
                link = f'<a href="{file_url}" download style="color:#FFD700; font-weight:bold; text-decoration:none;">📥 {filename}</a><br>'
                matching_links.append(link)

        # ✅ If found matching PDFs
        if matching_links:
            return jsonify({"response": "✅ PDF(s) Found:<br>" + "".join(matching_links)})

        # 🔁 If subject not matched, fallback: show related PDFs using query words
        partial_links = []
        for filename in os.listdir(BASE_DIR):
            name = filename.lower()
            if any(word in name for word in words):
                file_url = f"http://127.0.0.1:5000/download/{filename}"
                link = f'<a href="{file_url}" download style="color:#FFD700;">📥 {filename}</a><br>'
                partial_links.append(link)

        if partial_links:
            return jsonify({"response": "🤖 Closest related PDFs we found:<br>" + "".join(partial_links)})

    except Exception as e:
        print("Error:", e)

    return jsonify({"response": "❌ Sorry bro, no matching PDF found for your request."})


# ✅ ROUTE TO SERVE FILES
@app.route('/download/<path:filename>')
def download_file(filename):
    print("User requested:", filename)
    return send_from_directory(BASE_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

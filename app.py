from flask import Flask, request, jsonify, render_template
import os
import uuid
from werkzeug.utils import secure_filename
import sqlite3
import datetime

import database
import utils

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max limit

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Create unique filename to avoid overwrites
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return file_path, filename
    return None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}), 200

@app.route('/evaluate', methods=['POST'])
def evaluate():
    if 'jd' not in request.files or 'resumes' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    jd_file = request.files['jd']
    resumes_files = request.files.getlist('resumes')
    
    if jd_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    # Process JD
    jd_path, jd_name = save_file(jd_file)
    if not jd_path:
        return jsonify({"error": "Invalid JD file"}), 400
    
    jd_text = utils.extract_text(jd_path)
    if not jd_text:
        return jsonify({"error": "Could not extract text from JD"}), 400
    
    processed_jd_text = utils.preprocess_text(jd_text)
    
    resume_data = []
    processed_resume_texts = []
    
    # Process Resumes
    for resume_file in resumes_files:
        if resume_file.filename == '':
            continue
            
        r_path, r_name = save_file(resume_file)
        if not r_path:
            continue
            
        r_text = utils.extract_text(r_path)
        if not r_text:
            continue
            
        # Store in DB
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO resumes (filename, extracted_text) VALUES (?, ?)', (r_name, r_text))
        resume_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        processed_r_text = utils.preprocess_text(r_text)
        processed_resume_texts.append(processed_r_text)
        
        resume_data.append({
            'resume_id': resume_id,
            'filename': r_name,
            'text': r_text
        })
    
    if not resume_data:
        return jsonify({"error": "No valid resumes processed"}), 400
        
    # Calculate Similarity
    # Note: calculate_similarity expects a list of resume texts, corresponding to the resume_data list
    similarities = utils.calculate_similarity(processed_jd_text, processed_resume_texts)
    
    results = []
    
    # Store Results and format output
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    for i, score in enumerate(similarities):
        resume_info = resume_data[i]
        
        # Insert result
        cursor.execute('INSERT INTO results (resume_id, score) VALUES (?, ?)', (resume_info['resume_id'], float(score)))
        
        # Normalize BERT score (typically 0.2 to 1.0)
        # We scale it so that >0.2 starts counting, and >0.8 is high
        raw_score = float(score)
        print(f"DEBUG: {resume_info['filename']} Raw BERT Score: {raw_score}")
        
        # Formula: (score - 0.25) / 0.75 * 100
        # 0.25 or lower -> 0%
        # 0.625 -> 50%
        # 1.0 -> 100%
        final_score = max(0, (raw_score - 0.25) / 0.75) * 100
        final_score = min(final_score, 100.0)
        
        # Generate Reason
        reason = utils.generate_reason(final_score, jd_text, resume_info['text'])
        
        # Extract Skills
        extracted_skills = utils.extract_skills(resume_info['text'])
        
        # AI Evidence Extraction
        highlight = utils.extract_highlight(jd_text, resume_info['text'])
        
        results.append({
            'rank': 0, # Placeholder, will assign rank
            'filename': resume_info['filename'],
            'score': round(final_score, 2),
            'reason': reason,
            'skills': extracted_skills,
            'highlight': highlight
        })
        
    conn.commit()
    conn.close()
    
    # Sort by score descending
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # assign rank
    for i, res in enumerate(results):
        res['rank'] = i + 1
        
    return jsonify(results), 200

if __name__ == '__main__':
    database.init_db()
    app.run(debug=True, port=5000)

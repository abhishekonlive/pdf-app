from flask import Flask, render_template, request, send_file, jsonify
from PyPDF2 import PdfMerger
import os
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='.')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    if 'files' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files')
    if len(files) < 2:
        return jsonify({'error': 'At least 2 PDF files required'}), 400
    
    merger = PdfMerger()
    temp_files = []
    
    try:
        for file in files:
            if file.filename.endswith('.pdf'):
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                file.save(temp_file.name)
                temp_files.append(temp_file.name)
                merger.append(temp_file.name)
        
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        merger.write(output_file.name)
        merger.close()
        
        return send_file(output_file.name, as_attachment=True, download_name='merged.pdf')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

if __name__ == '__main__':
    app.run(debug=True)
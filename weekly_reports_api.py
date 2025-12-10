"""
Weekly Development Reports API
Handles upload, storage, and retrieval of weekly development reports
"""

import os
import json
from datetime import datetime
from flask import request, jsonify, send_file
from werkzeug.utils import secure_filename

# Storage directory for reports
REPORTS_DIR = "weekly_reports_uploads"
REPORTS_INDEX = "weekly_reports_index.json"

def init_reports_storage():
    """Initialize reports storage directory and index"""
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
    if not os.path.exists(REPORTS_INDEX):
        with open(REPORTS_INDEX, 'w') as f:
            json.dump({"reports": []}, f)

def register_weekly_reports_routes(app):
    """Register all weekly reports API routes"""
    
    @app.route('/api/reports/upload-weekly', methods=['POST'])
    def upload_weekly_report():
        """Upload a weekly development report"""
        try:
            init_reports_storage()
            
            if 'report' not in request.files:
                return jsonify({"success": False, "error": "No file provided"}), 400
            
            file = request.files['report']
            week = request.form.get('week', 'Unknown')
            
            if file.filename == '':
                return jsonify({"success": False, "error": "No file selected"}), 400
            
            # Secure filename
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stored_filename = f"{week}_{timestamp}_{filename}"
            filepath = os.path.join(REPORTS_DIR, stored_filename)
            
            # Save file
            file.save(filepath)
            
            # Update index
            with open(REPORTS_INDEX, 'r') as f:
                index = json.load(f)
            
            report_entry = {
                "id": timestamp,
                "week": week,
                "filename": filename,
                "stored_filename": stored_filename,
                "uploaded_at": datetime.now().isoformat(),
                "file_type": filename.split('.')[-1] if '.' in filename else 'unknown'
            }
            
            index["reports"].insert(0, report_entry)  # Most recent first
            
            with open(REPORTS_INDEX, 'w') as f:
                json.dump(index, f, indent=2)
            
            return jsonify({
                "success": True,
                "report_id": timestamp,
                "filename": filename
            }), 200
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/reports/weekly-list', methods=['GET'])
    def list_weekly_reports():
        """Get list of all weekly reports"""
        try:
            init_reports_storage()
            
            with open(REPORTS_INDEX, 'r') as f:
                index = json.load(f)
            
            return jsonify({
                "success": True,
                "reports": index.get("reports", [])
            }), 200
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/reports/view/<report_id>', methods=['GET'])
    def view_weekly_report(report_id):
        """View a weekly report (opens in browser)"""
        try:
            init_reports_storage()
            
            with open(REPORTS_INDEX, 'r') as f:
                index = json.load(f)
            
            report = next((r for r in index["reports"] if r["id"] == report_id), None)
            
            if not report:
                return "Report not found", 404
            
            filepath = os.path.join(REPORTS_DIR, report["stored_filename"])
            
            if not os.path.exists(filepath):
                return "Report file not found", 404
            
            # Determine mimetype based on file extension
            file_type = report["file_type"]
            mimetype_map = {
                'pdf': 'application/pdf',
                'html': 'text/html',
                'md': 'text/markdown',
                'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }
            mimetype = mimetype_map.get(file_type, 'application/octet-stream')
            
            return send_file(filepath, mimetype=mimetype)
            
        except Exception as e:
            return f"Error viewing report: {str(e)}", 500
    
    @app.route('/api/reports/download/<report_id>', methods=['GET'])
    def download_weekly_report(report_id):
        """Download a weekly report"""
        try:
            init_reports_storage()
            
            with open(REPORTS_INDEX, 'r') as f:
                index = json.load(f)
            
            report = next((r for r in index["reports"] if r["id"] == report_id), None)
            
            if not report:
                return "Report not found", 404
            
            filepath = os.path.join(REPORTS_DIR, report["stored_filename"])
            
            if not os.path.exists(filepath):
                return "Report file not found", 404
            
            return send_file(
                filepath,
                as_attachment=True,
                download_name=report["filename"]
            )
            
        except Exception as e:
            return f"Error downloading report: {str(e)}", 500

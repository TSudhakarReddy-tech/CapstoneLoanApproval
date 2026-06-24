#!/usr/bin/env python3
"""Simple HTTP dashboard for Loan Approval System."""

from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import requests
import os

API_URL = "http://localhost:8000/api"

class DashboardHandler(SimpleHTTPRequestHandler):
    """Handle dashboard requests."""

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.get_index_page().encode())
        elif self.path == "/api/status":
            self.send_status_response()
        elif self.path.startswith("/api/applications/"):
            app_id = self.path.split("/")[-1]
            self.get_application_status(app_id)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle POST requests."""
        if self.path == "/api/applications":
            self.submit_application()
        else:
            self.send_response(404)
            self.end_headers()

    def get_index_page(self):
        """Return the main dashboard HTML."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💰 Loan Approval System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        .card h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }

        .form-group {
            margin-bottom: 15px;
        }

        label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 600;
        }

        input, select {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
            transition: border-color 0.3s;
        }

        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }

        .dti-display {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            font-size: 1.1em;
            font-weight: bold;
        }

        .dti-good { color: #28a745; }
        .dti-moderate { color: #ffc107; }
        .dti-high { color: #dc3545; }

        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s;
        }

        button:hover {
            transform: translateY(-2px);
        }

        button:active {
            transform: translateY(0);
        }

        .result {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
            border-left: 5px solid #667eea;
        }

        .result h3 {
            margin-bottom: 10px;
            color: #333;
        }

        .result p {
            margin: 8px 0;
            color: #666;
        }

        .status-badge {
            display: inline-block;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-right: 10px;
        }

        .status-approved { background: #d4edda; color: #155724; }
        .status-rejected { background: #f8d7da; color: #721c24; }
        .status-review { background: #fff3cd; color: #856404; }

        .case-id {
            font-family: monospace;
            background: #e9ecef;
            padding: 8px 12px;
            border-radius: 3px;
            font-weight: bold;
        }

        .decision-summary {
            background: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #667eea;
            margin: 15px 0;
            white-space: pre-wrap;
            font-size: 0.95em;
            max-height: 300px;
            overflow-y: auto;
        }

        .loading {
            text-align: center;
            padding: 20px;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #721c24;
        }

        .success {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #155724;
        }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }

        .metric {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }

        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #667eea;
        }

        .metric-label {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }

        @media (max-width: 768px) {
            .content {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 Loan Approval System</h1>
            <p>AI-Powered Loan Decision Engine</p>
        </div>

        <div class="content">
            <!-- New Application Form -->
            <div class="card">
                <h2>📝 New Application</h2>
                <form id="applicationForm">
                    <div class="form-group">
                        <label>Full Name *</label>
                        <input type="text" name="name" required>
                    </div>

                    <div class="form-group">
                        <label>Age *</label>
                        <input type="number" name="age" min="18" max="80" value="35" required>
                    </div>

                    <div class="form-group">
                        <label>Monthly Income ($) *</label>
                        <input type="number" name="income" min="1000" value="5000" required>
                    </div>

                    <div class="form-group">
                        <label>Total Liabilities ($) *</label>
                        <input type="number" name="liabilities" min="0" value="0" required>
                    </div>

                    <div class="form-group">
                        <label>Credit Score *</label>
                        <input type="number" name="credit" min="300" max="850" value="750" required>
                    </div>

                    <div class="form-group">
                        <label>Employment Type *</label>
                        <select name="employment" required>
                            <option value="Salaried">Salaried</option>
                            <option value="Self-employed">Self-employed</option>
                            <option value="Business Owner">Business Owner</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Years at Current Employment *</label>
                        <input type="number" name="years" min="0" step="0.5" value="3" required>
                    </div>

                    <div class="form-group">
                        <label>Requested Loan Amount ($) *</label>
                        <input type="number" name="loanAmount" min="5000" value="50000" required>
                    </div>

                    <div class="form-group">
                        <label>Loan Tenure (Months) *</label>
                        <input type="number" name="tenure" min="6" max="360" value="60" required>
                    </div>

                    <!-- DTI Display -->
                    <div id="dtiDisplay" class="dti-display" style="display:none;">
                        DTI: <span id="dtiValue">0%</span>
                    </div>

                    <button type="submit">🚀 Submit Application</button>
                </form>

                <div id="submitResult"></div>
            </div>

            <!-- Application Status Checker -->
            <div class="card">
                <h2>📊 Application Status</h2>
                <div class="form-group">
                    <label>Application ID *</label>
                    <input type="text" id="statusAppId" placeholder="Paste Application ID here">
                </div>

                <button onclick="checkStatus()">🔍 Check Status</button>

                <div id="statusResult"></div>
            </div>
        </div>
    </div>

    <script>
        const API_URL = "http://localhost:8000/api";

        // Calculate DTI in real-time
        document.getElementById('applicationForm').addEventListener('input', calculateDTI);

        function calculateDTI() {
            const income = parseFloat(document.querySelector('input[name="income"]').value) || 0;
            const liabilities = parseFloat(document.querySelector('input[name="liabilities"]').value) || 0;
            const loanAmount = parseFloat(document.querySelector('input[name="loanAmount"]').value) || 0;
            const tenure = parseFloat(document.querySelector('input[name="tenure"]').value) || 1;

            if (income > 0 && tenure > 0) {
                const monthlyPayment = loanAmount / tenure;
                const totalDebt = (liabilities / 12) + monthlyPayment;
                const dti = (totalDebt / income) * 100;

                const display = document.getElementById('dtiDisplay');
                const value = document.getElementById('dtiValue');
                display.style.display = 'block';
                value.textContent = dti.toFixed(1) + '%';

                // Color code DTI
                if (dti < 43) {
                    display.style.color = '#28a745';
                    display.style.background = '#d4edda';
                } else if (dti < 50) {
                    display.style.color = '#ffc107';
                    display.style.background = '#fff3cd';
                } else {
                    display.style.color = '#dc3545';
                    display.style.background = '#f8d7da';
                }
            }
        }

        // Submit application
        document.getElementById('applicationForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const form = e.target;
            const result = document.getElementById('submitResult');

            result.innerHTML = '<div class="loading"><div class="spinner"></div><p>Processing...</p></div>';

            try {
                const response = await fetch(`${API_URL}/applications`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        applicant_name: form.name.value,
                        age: parseInt(form.age.value),
                        monthly_income: parseFloat(form.income.value),
                        employment_type: form.employment.value,
                        years_employed: parseFloat(form.years.value),
                        credit_score: parseInt(form.credit.value),
                        total_liabilities: parseFloat(form.liabilities.value),
                        loan_amount: parseFloat(form.loanAmount.value),
                        loan_tenure_months: parseInt(form.tenure.value),
                        location: "Not specified"
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    result.innerHTML = `
                        <div class="success">
                            <strong>✅ Application Submitted!</strong><br>
                            Application ID: <span class="case-id">${data.application_id}</span><br>
                            Status: ${data.status}<br>
                            <small>Copy the Application ID to check status</small>
                        </div>
                    `;
                    document.getElementById('statusAppId').value = data.application_id;
                } else {
                    result.innerHTML = '<div class="error">Error submitting application</div>';
                }
            } catch (error) {
                result.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        });

        // Check application status
        async function checkStatus() {
            const appId = document.getElementById('statusAppId').value;
            const result = document.getElementById('statusResult');

            if (!appId) {
                result.innerHTML = '<div class="error">Please enter an Application ID</div>';
                return;
            }

            result.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading...</p></div>';

            try {
                const response = await fetch(`${API_URL}/applications/${appId}`);

                if (!response.ok) {
                    result.innerHTML = '<div class="error">Application not found</div>';
                    return;
                }

                const data = await response.json();
                const decision = data.decision || {};

                const statusBadge = {
                    'APPROVED': 'status-approved',
                    'REJECTED': 'status-rejected',
                    'UNDER_REVIEW': 'status-review'
                }[decision.decision_category] || 'status-review';

                result.innerHTML = `
                    <div class="result">
                        <div style="margin-bottom: 15px;">
                            <span class="status-badge ${statusBadge}">
                                ${decision.decision_category || 'UNKNOWN'}
                            </span>
                        </div>

                        <div class="grid-2">
                            <div class="metric">
                                <div class="metric-label">Case ID</div>
                                <div class="case-id">${decision.case_id || 'N/A'}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">Confidence</div>
                                <div class="metric-value">${(decision.confidence_score * 100).toFixed(1)}%</div>
                            </div>
                        </div>

                        <div class="grid-2" style="margin-top: 15px;">
                            <div class="metric">
                                <div class="metric-label">Risk Level</div>
                                <div class="metric-value">${decision.risk_level || 'UNKNOWN'}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">Case Reference</div>
                                <div style="font-size: 1.1em; color: #667eea; font-weight: bold;">${decision.case_reference || 'N/A'}</div>
                            </div>
                        </div>

                        <h4 style="margin-top: 20px; margin-bottom: 10px;">📋 Decision Summary</h4>
                        <div class="decision-summary">${decision.decision_summary || 'No summary available'}</div>

                        ${decision.rejection_reason ? `
                        <h4 style="margin-top: 20px; margin-bottom: 10px;">❌ Rejection Reason</h4>
                        <div style="background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24;">
                            ${decision.rejection_reason}
                        </div>
                        ` : ''}

                        ${decision.approval_conditions ? `
                        <h4 style="margin-top: 20px; margin-bottom: 10px;">✅ Approval Conditions</h4>
                        <div style="background: #d4edda; padding: 10px; border-radius: 5px; color: #155724;">
                            <pre>${JSON.stringify(decision.approval_conditions, null, 2)}</pre>
                        </div>
                        ` : ''}
                    </div>
                `;
            } catch (error) {
                result.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        }

        // Allow Enter key to check status
        document.getElementById('statusAppId').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') checkStatus();
        });
    </script>
</body>
</html>
"""

    def send_status_response(self):
        """Send API status."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        status = {"status": "running", "api": API_URL}
        self.wfile.write(json.dumps(status).encode())

    def get_application_status(self, app_id):
        """Get application status from API."""
        try:
            response = requests.get(f"{API_URL}/applications/{app_id}")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(response.content)
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def submit_application(self):
        """Submit application to API."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            response = requests.post(f"{API_URL}/applications", json=data)
            self.send_response(response.status_code)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(response.content)
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8501), DashboardHandler)
    print("🚀 Dashboard running on http://localhost:8501")
    print("💰 Loan Approval Dashboard is ready!")
    server.serve_forever()

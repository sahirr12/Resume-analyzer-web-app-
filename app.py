from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import os
import pickle
import re
import numpy as np
import json
from generate_reports import save_report

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['REPORTS_FOLDER'] = 'reports/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

# Load model and vectorizer
with open('model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)
with open('vectorizer.pkl', 'rb') as vec_file:
    vectorizer = pickle.load(vec_file)

# Expanded category mapping with actual category names
category_mapping = {
    0: 'General Manager',
    1: 'Software Engineer',
    2: 'Data Scientist',
    3: 'Web Developer',
    4: 'System Administrator',
    5: 'Network Engineer',
    6: 'Database Administrator',
    7: 'Security Analyst',
    8: 'AI/ML Engineer',
    9: 'Project Manager',
    10: 'Product Manager',
    11: 'DevOps Engineer',
    12: 'Business Analyst',
    13: 'Data Analyst',
    14: 'Cloud Engineer',
    15: 'UI/UX Designer',
    16: 'Technical Support',
    17: 'Quality Assurance',
    18: 'IT Manager',
    19: 'ERP Consultant',
    20: 'Mobile Developer',
    21: 'Game Developer',
    22: 'Embedded Systems Engineer',
    23: 'Blockchain Developer',
    24: 'IT Support Specialist',
    25: 'Technical Writer',
    26: 'Network Administrator',
    27: 'Software Tester',
    28: 'Systems Analyst',
    29: 'Technical Consultant',
    30: 'Cloud Solutions Architect',
    31: 'Marketing Manager',
    32: 'Sales Manager',
    33: 'HR Manager',
    34: 'Financial Analyst',
    35: 'Accountant',
    36: 'Content Strategist',
    37: 'Graphic Designer',
    38: 'SEO Specialist',
    39: 'Social Media Manager',
    40: 'Research Scientist',
    41: 'Pharmaceutical Sales Representative',
    42: 'Logistics Manager',
    43: 'Manufacturing Engineer',
    44: 'Civil Engineer',
    45: 'Mechanical Engineer',
    46: 'Electrical Engineer',
    47: 'Network Security Engineer',
    48: 'Data Engineer',
    49: 'Business Development Manager',
    50: 'Compliance Officer',
    51: 'Product Designer',
    52: 'Event Coordinator',
    53: 'Public Relations Specialist',
    54: 'Interior Designer',
    55: 'Fashion Designer',
    56: 'Video Editor',
    57: 'Data Entry Clerk',
    58: 'Customer Success Manager',
    59: 'Training Specialist',
    60: 'Operations Manager',
    61: 'Facilities Manager',
    62: 'Purchasing Manager',
    63: 'Insurance Underwriter',
    64: 'Real Estate Agent',
    65: 'Web Content Manager',
    66: 'E-commerce Manager',
    67: 'Health and Safety Officer',
    68: 'Quality Control Inspector',
    69: 'Digital Marketing Specialist',
    70: 'Telecommunications Technician',
    71: 'Clinical Research Coordinator',
    72: 'Market Research Analyst',
    73: 'Technical Support Engineer',
    74: 'Environmental Scientist',
    75: 'Biotechnologist',
    76: 'Supply Chain Analyst',
    77: 'Business Intelligence Analyst',
    78: 'Web Analytics Specialist',
    79: 'Social Worker',
    80: 'Nurse Practitioner',
    81: 'Medical Assistant',
    82: 'Pharmacist',
    83: 'Occupational Therapist',
    84: 'Speech-Language Pathologist',
    85: 'Veterinarian',
    86: 'Chef',
    87: 'Bartender',
    88: 'Waitstaff',
    89: 'Housekeeper',
    90: 'Security Guard',
    91: 'Personal Trainer',
    92: 'Yoga Instructor',
    93: 'Life Coach',
    94: 'Travel Agent',
    95: 'Real Estate Appraiser',
    96: 'Insurance Claims Adjuster',
    97: 'Fundraiser',
    98: 'Nonprofit Manager',
    99: 'Technical Recruiter',
    100: 'Sales Engineer',
    101: 'Field Service Technician',
    102: 'UX Researcher',
    103: 'Content Marketing Manager',
    104: 'Data Privacy Officer',
    105: 'Corporate Trainer',
    106: 'Business Continuity Planner',
    107: 'User Experience Designer',
    108: 'Digital Product Manager',
    109: 'IT Auditor',
    110: 'Corporate Communications Manager',
    111: 'Web Developer Intern',
    112: 'Graphic Design Intern',
    113: 'Marketing Intern',
    114: 'Sales Intern',
    115: 'Research Intern',
    116: 'Finance Intern',
    117: 'Human Resources Intern',
    118: 'Legal Intern',
    119: 'Public Relations Intern',
    120: 'IT Intern',
    121: 'Operations Intern',
    122: 'Customer Service Intern',
    123: 'Event Planning Intern',
    124: 'Social Media Intern',
    125: 'Content Writing Intern',
    126: 'Data Entry Intern',
    127: 'Sales Support Intern',
    128: 'Quality Assurance Intern',
    129: 'Digital Marketing Intern',
    130: 'Software Development Intern',
    131: 'Graphic Design Intern',
    132: 'Public Health Intern',
    133: 'Environmental Intern',
    134: 'Nonprofit Intern',
    135: 'HR Intern',
    136: 'Legal Assistant Intern',
    137: 'Finance Intern',
    138: 'Data Science Intern',
    139: 'Cybersecurity Intern',
    140: 'IT Support Intern',
    141: 'Research and Development Intern',
    142: 'Marketing Research Intern',
    143: 'Business Operations Intern',
    144: 'Media Intern',
    145: 'E-commerce Intern',
    146: 'Fashion Intern',
    147: 'Photography Intern',
    148: 'Advertising Intern',
    149: 'Sales and Marketing Intern',
    150: 'HR Recruitment Intern',
    151: 'Culinary Intern',
    152: 'Event Marketing Intern',
    153: 'Community Outreach Intern',
    154: 'Technical Sales Intern',
    155: 'Social Impact Intern',
    156: 'Public Affairs Intern',
    157: 'Graphic Arts Intern',
    158: 'Digital Content Intern',
    159: 'User Experience Intern',
    160: 'Software Testing Intern',
    161: 'Healthcare Intern',
    162: 'Operations Research Intern',
    163: 'Public Policy Intern',
    164: 'Corporate Social Responsibility Intern',
    165: 'Insurance Intern',
    166: 'Retail Management Intern',
    167: 'Real Estate Development Intern',
    168: 'Logistics Intern',
    169: 'Quality Assurance Intern',
    170: 'Digital Media Intern',
    171: 'Corporate Communications Intern',
    172: 'Health Promotion Intern',
    173: 'Public Relations Intern',
    174: 'Business Intelligence Intern',
    175: 'Product Marketing Intern',
    176: 'Cybersecurity Intern',
    177: 'Digital Strategy Intern',
    178: 'Data Visualization Intern',
    179: 'Sustainability Intern',
    180: 'Innovation Intern',
    181: 'Event Logistics Intern',
    182: 'Corporate Governance Intern',
    183: 'Risk Management Intern',
    184: 'Digital Transformation Intern',
    185: 'Sales Enablement Intern',
    186: 'Business Operations Analyst Intern',
    187: 'IT Project Management Intern',
    188: 'Crisis Management Intern',
    189: 'Digital Experience Intern',
    190: 'Customer Insights Intern',
    191: 'Content Strategy Intern',
    192: 'Digital Advertising Intern',
    193: 'Corporate Strategy Intern',
    194: 'User Research Intern',
    195: 'Analytics Intern',
    196: 'Product Development Intern',
    197: 'Data Management Intern',
    198: 'Financial Planning Intern',
    199: 'Quality Improvement Intern',
    200: 'Digital Content Strategy Intern',
    201: 'Customer Experience Intern',
    202: 'Business Development Intern',
    203: 'Social Media Marketing Intern',
    204: 'Technical Writing Intern',
    205: 'Market Development Intern',
    206: 'Business Strategy Intern',
    207: 'Customer Loyalty Intern',
    208: 'Retail Marketing Intern',
    209: 'Digital Engagement Intern'
}
@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({'error': 'No file selected'})

    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    text = image_to_text(file_path)
    result = analyze_resume(text)

    with open('latest_resume.json', 'w') as f:
        json.dump(result, f)

    return render_template('result.html', result=result)

@app.route('/charts')
def charts():
    try:
        with open('latest_resume.json', 'r') as f:
            data = json.load(f)
            skills_list = data['details']['Skills'].split(', ')
            skills = {skill: skills_list.count(skill) for skill in set(skills_list)}
            prediction_accuracy = data['accuracy']
    except FileNotFoundError:
        skills = {}
        prediction_accuracy = 0

    return render_template('charts.html', 
                           labels_skills=list(skills.keys()), 
                           values_skills=list(skills.values()),
                           prediction_accuracy=prediction_accuracy)

@app.route('/download_report', methods=['GET'])
def download_report():
    format = request.args.get('format', 'pdf')  # Default to PDF if format is not provided
    file_name = 'resume_analysis_report'
    if format not in ['pdf', 'csv']:
        return jsonify({'error': 'Invalid format'})

    try:
        with open('latest_resume.json', 'r') as f:
            data = json.load(f)
            save_report(data, file_name, format)
            return send_file(os.path.join(app.config['REPORTS_FOLDER'], f"{file_name}.{format}"),
                             as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'No report found'})


def image_to_text(image_path):
    img = Image.open(image_path)
    return pytesseract.image_to_string(img, config='--oem 3 --psm 6')

def analyze_resume(text):
    text_vector = vectorizer.transform([text])
    prediction = int(model.predict(text_vector)[0])
    prediction_category = category_mapping.get(prediction, 'Unknown Category')
    prediction_proba = model.predict_proba(text_vector)
    accuracy = np.max(prediction_proba) * 100
    details = extract_resume_details(text)

    # Ensure the mapping is correct
    correct_category = ensure_correct_mapping(prediction_category, details)

    return {'prediction': correct_category, 'accuracy': round(accuracy, 2), 'details': details}

def ensure_correct_mapping(prediction_category, details):
    # Implement logic to verify and correct the prediction category if necessary
    # For example, check if certain keywords or patterns in details match the correct category
    skills_keywords = {
    'General Manager': ['Sales', 'Inventory Management', 'Customer Service', 'Budgeting', 'Payroll', 'Team Leadership', 'Operational Strategy', 'Employee Training'],
    'Software Engineer': ['Python', 'Java', 'C++', 'JavaScript', 'SQL', 'Software Development', 'Agile Methodologies', 'Version Control'],
    'Data Scientist': ['Python', 'R', 'Machine Learning', 'Data Analysis', 'Statistics', 'Data Mining', 'Big Data', 'Predictive Modeling'],
    'Web Developer': ['HTML', 'CSS', 'JavaScript', 'React', 'Angular', 'Responsive Design', 'Web Performance Optimization', 'RESTful APIs'],
    'System Administrator': ['Linux', 'Windows Server', 'Network Administration', 'VMware', 'Shell Scripting', 'System Security', 'Backup Solutions'],
    'Network Engineer': ['Cisco', 'Routing', 'Switching', 'Firewall', 'Network Security', 'Network Design', 'Troubleshooting'],
    'Database Administrator': ['SQL', 'Oracle', 'Database Design', 'Performance Tuning', 'Backup', 'Data Migration', 'Data Warehousing'],
    'Security Analyst': ['Cybersecurity', 'Penetration Testing', 'Network Security', 'Incident Response', 'SIEM', 'Threat Analysis', 'Vulnerability Assessment'],
    'AI/ML Engineer': ['Python', 'TensorFlow', 'Keras', 'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision'],
    'Project Manager': ['Project Planning', 'Risk Management', 'Agile', 'Scrum', 'Budget Management', 'Stakeholder Engagement', 'Resource Allocation'],
    'Product Manager': ['Product Development', 'Market Research', 'Roadmap Planning', 'Agile', 'Stakeholder Management', 'User Experience', 'Competitive Analysis'],
    'DevOps Engineer': ['CI/CD', 'Docker', 'Kubernetes', 'AWS', 'Jenkins', 'Infrastructure as Code', 'Monitoring and Logging'],
    'Business Analyst': ['Requirements Gathering', 'Process Improvement', 'Stakeholder Management', 'Data Analysis', 'UML', 'Business Process Modeling'],
    'Data Analyst': ['SQL', 'Excel', 'Data Visualization', 'Python', 'Statistics', 'Reporting', 'Data Cleaning'],
    'Cloud Engineer': ['AWS', 'Azure', 'Google Cloud', 'Cloud Security', 'Infrastructure as Code', 'Cloud Migration', 'Service Management'],
    'UI/UX Designer': ['Wireframing', 'Prototyping', 'User Research', 'Sketch', 'Figma', 'User Testing', 'Interaction Design'],
    'Technical Support': ['Troubleshooting', 'Customer Service', 'Windows', 'MacOS', 'Remote Support', 'Technical Documentation'],
    'Quality Assurance': ['Test Planning', 'Manual Testing', 'Automated Testing', 'Selenium', 'JIRA', 'Defect Tracking', 'Test Case Development'],
    'IT Manager': ['IT Strategy', 'Team Leadership', 'Budgeting', 'Vendor Management', 'Project Management', 'Risk Management'],
    'ERP Consultant': ['SAP', 'Oracle ERP', 'Business Process Improvement', 'Requirements Analysis', 'Project Management', 'Change Management'],
    'Mobile Developer': ['iOS', 'Android', 'React Native', 'Swift', 'Kotlin', 'Mobile UI/UX', 'App Store Optimization'],
    'Game Developer': ['Unity', 'Unreal Engine', 'C#', 'C++', 'Game Design', '3D Modeling', 'Gameplay Programming'],
    'Embedded Systems Engineer': ['C', 'C++', 'Microcontrollers', 'RTOS', 'Hardware Design', 'Firmware Development'],
    'Blockchain Developer': ['Ethereum', 'Solidity', 'Smart Contracts', 'Bitcoin', 'Cryptography', 'Decentralized Applications'],
    'IT Support Specialist': ['Troubleshooting', 'Customer Service', 'Windows', 'Linux', 'Networking', 'Help Desk Support'],
    'Technical Writer': ['Technical Documentation', 'Content Creation', 'User Manuals', 'API Documentation', 'Editing', 'Research Skills'],
    'Network Administrator': ['Cisco', 'Network Monitoring', 'Firewall', 'Switching', 'Routing', 'Network Configuration'],
    'Software Tester': ['Test Automation', 'Manual Testing', 'Selenium', 'Load Testing', 'Performance Testing', 'Test Case Design'],
    'Systems Analyst': ['System Requirements', 'System Design', 'UML', 'Business Analysis', 'Data Analysis', 'Technical Specifications'],
    'Technical Consultant': ['Technical Solutions', 'Customer Engagement', 'Project Management', 'Requirements Gathering', 'Solution Design'],
    'Cloud Solutions Architect': ['AWS', 'Azure', 'Google Cloud', 'Cloud Architecture', 'Infrastructure as Code', 'Cloud Governance'],
    'Marketing Manager': ['Digital Marketing', 'SEO', 'Content Strategy', 'Brand Management', 'Market Research', 'Campaign Management'],
    'Sales Manager': ['Sales Strategy', 'Lead Generation', 'Customer Relationship Management', 'Negotiation', 'Sales Forecasting', 'Team Management'],
    'HR Manager': ['Recruitment', 'Employee Relations', 'Performance Management', 'Training and Development', 'Compensation and Benefits', 'HR Policies'],
    'Financial Analyst': ['Financial Modeling', 'Budgeting', 'Forecasting', 'Data Analysis', 'Reporting', 'Investment Analysis'],
    'Accountant': ['Financial Reporting', 'Tax Preparation', 'Auditing', 'Accounts Payable', 'Accounts Receivable', 'General Ledger'],
    'Content Strategist': ['Content Creation', 'SEO', 'Social Media Management', 'Brand Storytelling', 'Analytics', 'Editorial Planning'],
    'Graphic Designer': ['Adobe Creative Suite', 'Brand Identity', 'Typography', 'Layout Design', 'Illustration', 'Print Design'],
    'SEO Specialist': ['Keyword Research', 'On-Page Optimization', 'Link Building', 'Analytics', 'Content Strategy', 'Technical SEO'],
    'Social Media Manager': ['Content Creation', 'Community Engagement', 'Analytics', 'Campaign Management', 'Brand Strategy', 'Social Listening'],
    'Research Scientist': ['Experimental Design', 'Data Analysis', 'Research Methodologies', 'Statistical Software', 'Scientific Writing', 'Literature Review'],
    'Pharmaceutical Sales Representative': ['Product Knowledge', 'Sales Techniques', 'Customer Relationship Management', 'Market Analysis', 'Negotiation', 'Networking'],
    'Logistics Manager': ['Supply Chain Management', 'Inventory Control', 'Transportation Management', 'Warehouse Management', 'Vendor Relations', 'Cost Reduction'],
    'Manufacturing Engineer': ['Process Improvement', 'Lean Manufacturing', 'Quality Control', 'CAD Software', 'Production Planning', 'Root Cause Analysis'],
    'Civil Engineer': ['Project Management', 'Structural Analysis', 'AutoCAD', 'Construction Management', 'Site Development', 'Regulatory Compliance'],
    'Mechanical Engineer': ['CAD Software', 'Thermodynamics', 'Materials Science', 'Design Engineering', 'Manufacturing Processes', 'Project Management'],
    'Electrical Engineer': ['Circuit Design', 'Signal Processing', 'Control Systems', 'Electronics', 'Power Systems', 'Testing and Validation'],
    'Network Security Engineer': ['Firewalls', 'Intrusion Detection', 'VPNs', 'Network Protocols', 'Security Audits', 'Incident Response'],
    'Data Engineer': ['ETL Processes', 'Data Warehousing', 'Big Data Technologies', 'SQL', 'Data Pipeline', 'Data Modeling'],
    'Business Development Manager': ['Market Research', 'Partnership Development', 'Sales Strategy', 'Client Relationships', 'Negotiation', 'Strategic Planning'],
    'Compliance Officer': ['Regulatory Compliance', 'Risk Assessment', 'Policy Development', 'Internal Audits', 'Training Programs', 'Reporting'],
    'Product Designer': ['User-Centered Design', 'Prototyping', 'User Testing', 'CAD Software', 'Research', 'Design Thinking'],
    'Event Coordinator': ['Event Planning', 'Budget Management', 'Vendor Management', 'Marketing', 'Logistics', 'Customer Service'],
    'Public Relations Specialist': ['Media Relations', 'Crisis Management', 'Content Creation', 'Event Planning', 'Brand Management', 'Social Media'],
    'Interior Designer': ['Space Planning', 'Color Theory', '3D Modeling', 'Client Consultation', 'Project Management', 'Sustainability'],
    'Fashion Designer': ['Trend Analysis', 'Pattern Making', 'Textile Knowledge', 'Illustration', 'Sewing Techniques', 'Brand Development'],
    'Video Editor': ['Editing Software', 'Storytelling', 'Color Grading', 'Sound Design', 'Motion Graphics', 'Post-Production'],
    'Data Entry Clerk': ['Typing Skills', 'Attention to Detail', 'Data Management', 'Software Proficiency', 'Time Management', 'Organizational Skills'],
    'Customer Success Manager': ['Customer Engagement', 'Onboarding', 'Account Management', 'Feedback Collection', 'Upselling', 'Retention Strategies'],
    'Training Specialist': ['Curriculum Development', 'Instructional Design', 'Training Delivery', 'Assessment', 'Feedback', 'E-Learning'],
    'Operations Manager': ['Process Optimization', 'Team Leadership', 'Budgeting', 'Performance Metrics', 'Supply Chain Management', 'Strategic Planning'],
    'Facilities Manager': ['Building Maintenance', 'Vendor Management', 'Safety Regulations', 'Budgeting', 'Space Management', 'Project Management'],
    'Purchasing Manager': ['Supplier Negotiation', 'Inventory Management', 'Cost Analysis', 'Procurement Strategy', 'Vendor Relations', 'Contract Management'],
    'Insurance Underwriter': ['Risk Assessment', 'Policy Evaluation', 'Data Analysis', 'Client Consultation', 'Regulatory Compliance', 'Market Research'],
    'Real Estate Agent': ['Market Analysis', 'Client Relations', 'Negotiation', 'Property Valuation', 'Sales Strategy', 'Closing Transactions'],
    'Web Content Manager': ['Content Strategy', 'SEO', 'Analytics', 'CMS Management', 'User Engagement', 'Copywriting'],
    'E-commerce Manager': ['Online Marketing', 'Product Management', 'Customer Service', 'SEO', 'Inventory Management', 'Sales Strategy'],
    'Health and Safety Officer': ['Risk Assessment', 'Regulatory Compliance', 'Training Programs', 'Incident Investigation', 'Emergency Planning', 'Safety Audits'],
    'Quality Control Inspector': ['Inspection Techniques', 'Quality Standards', 'Data Analysis', 'Problem-Solving', 'Documentation', 'Reporting'],
    'Digital Marketing Specialist': ['SEO', 'PPC Advertising', 'Email Marketing', 'Social Media', 'Analytics', 'Content Creation'],
    'Telecommunications Technician': ['Network Installation', 'Troubleshooting', 'Customer Service', 'Technical Support', 'System Maintenance', 'Equipment Repair'],
    'Clinical Research Coordinator': ['Study Management', 'Patient Recruitment', 'Data Collection', 'Regulatory Compliance', 'Clinical Trials', 'Documentation'],
    'Market Research Analyst': ['Data Analysis', 'Survey Design', 'Consumer Behavior', 'Reporting', 'Market Trends', 'Statistical Software'],
    'Technical Support Engineer': ['Troubleshooting', 'Customer Service', 'Technical Documentation', 'Software Proficiency', 'Networking', 'Problem-Solving'],
    'Environmental Scientist': ['Research Methodologies', 'Data Analysis', 'Regulatory Compliance', 'Field Studies', 'Environmental Impact', 'Reporting'],
    'Biotechnologist': ['Laboratory Techniques', 'Data Analysis', 'Research Methodologies', 'Genetic Engineering', 'Quality Control', 'Product Development'],
    'Supply Chain Analyst': ['Data Analysis', 'Inventory Management', 'Logistics', 'Demand Forecasting', 'Supplier Management', 'Process Improvement'],
    'Business Intelligence Analyst': ['Data Visualization', 'SQL', 'Reporting', 'Data Analysis', 'Dashboard Development', 'Business Strategy'],
    'Web Analytics Specialist': ['Google Analytics', 'Data Interpretation', 'SEO', 'Reporting', 'Conversion Optimization', 'User Behavior Analysis'],
    'Social Worker': ['Client Assessment', 'Case Management', 'Resource Coordination', 'Crisis Intervention', 'Advocacy', 'Community Outreach'],
    'Nurse Practitioner': ['Patient Assessment', 'Clinical Skills', 'Diagnosis', 'Treatment Planning', 'Patient Education', 'Healthcare Regulations'],
    'Medical Assistant': ['Patient Care', 'Administrative Skills', 'Clinical Procedures', 'Medical Terminology', 'Electronic Health Records', 'Patient Communication'],
    'Pharmacist': ['Medication Management', 'Patient Counseling', 'Pharmacology', 'Regulatory Compliance', 'Inventory Management', 'Clinical Services'],
    'Occupational Therapist': ['Patient Assessment', 'Therapeutic Techniques', 'Rehabilitation', 'Goal Setting', 'Patient Education', 'Documentation'],
    'Speech-Language Pathologist': ['Assessment', 'Therapeutic Techniques', 'Patient Education', 'Communication Disorders', 'Documentation', 'Intervention Planning'],
    'Veterinarian': ['Animal Care', 'Diagnosis', 'Surgery', 'Client Communication', 'Regulatory Compliance', 'Emergency Care'],
    'Chef': ['Culinary Skills', 'Menu Development', 'Food Safety', 'Kitchen Management', 'Team Leadership', 'Cost Control'],
    'Bartender': ['Mixology', 'Customer Service', 'Inventory Management', 'Cash Handling', 'Menu Knowledge', 'Communication Skills'],
    'Waitstaff': ['Customer Service', 'Menu Knowledge', 'Order Taking', 'Teamwork', 'Cash Handling', 'Time Management'],
    'Housekeeper': ['Cleaning Techniques', 'Attention to Detail', 'Time Management', 'Customer Service', 'Organization', 'Safety Standards'],
    'Security Guard': ['Surveillance', 'Emergency Response', 'Customer Service', 'Report Writing', 'Conflict Resolution', 'Safety Protocols'],
    'Personal Trainer': ['Fitness Assessment', 'Exercise Programming', 'Nutrition Knowledge', 'Client Motivation', 'Safety Standards', 'Customer Service'],
    'Yoga Instructor': ['Yoga Techniques', 'Client Assessment', 'Class Planning', 'Health and Safety', 'Communication Skills', 'Mindfulness'],
    'Life Coach': ['Goal Setting', 'Motivational Techniques', 'Client Assessment', 'Communication Skills', 'Problem-Solving', 'Time Management'],
    'Travel Agent': ['Destination Knowledge', 'Customer Service', 'Sales Skills', 'Itinerary Planning', 'Problem-Solving', 'Negotiation'],
    'Real Estate Appraiser': ['Market Analysis', 'Property Valuation', 'Data Analysis', 'Reporting', 'Regulatory Compliance', 'Client Communication'],
    'Insurance Claims Adjuster': ['Investigation', 'Negotiation', 'Data Analysis', 'Customer Service', 'Report Writing', 'Regulatory Compliance'],
    'Fundraiser': ['Event Planning', 'Networking', 'Communication Skills', 'Marketing', 'Relationship Management', 'Grant Writing'],
    'Nonprofit Manager': ['Fundraising', 'Program Development', 'Budget Management', 'Volunteer Management', 'Community Outreach', 'Strategic Planning'],
    'Technical Recruiter': ['Candidate Sourcing', 'Interviewing', 'Networking', 'Job Market Knowledge', 'Negotiation', 'Relationship Building'],
    'Sales Engineer': ['Technical Knowledge', 'Customer Engagement', 'Sales Strategy', 'Product Demonstration', 'Problem-Solving', 'Negotiation'],
    'Field Service Technician': ['Troubleshooting', 'Customer Service', 'Technical Skills', 'Installation', 'Maintenance', 'Documentation'],
    'UX Researcher': ['User Interviews', 'Usability Testing', 'Data Analysis', 'Reporting', 'User Personas', 'Research Methodologies'],
    'Content Marketing Manager': ['Content Strategy', 'SEO', 'Analytics', 'Copywriting', 'Social Media Management', 'Brand Development'],
    'Data Privacy Officer': ['Regulatory Compliance', 'Risk Assessment', 'Policy Development', 'Data Protection', 'Training Programs', 'Incident Response'],
    'Corporate Trainer': ['Training Development', 'Presentation Skills', 'Needs Assessment', 'Training Delivery', 'Evaluation', 'Feedback'],
    'Business Continuity Planner': ['Risk Assessment', 'Crisis Management', 'Emergency Planning', 'Training Programs', 'Testing', 'Documentation'],
    'User Experience Designer': ['Wireframing', 'Prototyping', 'User Testing', 'Interaction Design', 'Visual Design', 'User Research'],
    'Digital Product Manager': ['Product Development', 'Agile Methodologies', 'User Experience', 'Market Analysis', 'Stakeholder Management', 'Roadmap Planning'],
    'IT Auditor': ['Risk Assessment', 'Compliance', 'Data Analysis', 'Reporting', 'Internal Controls', 'Audit Methodologies'],
    'Corporate Communications Manager': ['Media Relations', 'Crisis Management', 'Content Creation', 'Brand Strategy', 'Public Speaking', 'Event Planning'],
    'Web Developer Intern': ['HTML', 'CSS', 'JavaScript', 'Version Control', 'Responsive Design', 'Basic SEO'],
    'Graphic Design Intern': ['Adobe Creative Suite', 'Layout Design', 'Typography', 'Branding', 'Illustration', 'Research Skills'],
    'Marketing Intern': ['Market Research', 'Content Creation', 'Social Media Management', 'Analytics', 'Campaign Support', 'Event Planning'],
    'Sales Intern': ['Customer Engagement', 'Lead Generation', 'Market Research', 'Sales Strategy', 'Networking', 'Reporting'],
    'Research Intern': ['Data Collection', 'Literature Review', 'Data Analysis', 'Reporting', 'Research Methodologies', 'Technical Writing'],
    'Finance Intern': ['Financial Analysis', 'Data Entry', 'Reporting', 'Budgeting', 'Market Research', 'Excel Skills'],
    'Human Resources Intern': ['Recruitment', 'Employee Relations', 'Data Entry', 'Training Support', 'Policy Development', 'Communication Skills'],
    'Legal Intern': ['Legal Research', 'Document Review', 'Client Communication', 'Contract Analysis', 'Case Management', 'Writing Skills'],
    'Public Relations Intern': ['Media Monitoring', 'Press Releases', 'Event Support', 'Social Media Management', 'Content Creation', 'Research Skills'],
    'IT Intern': ['Technical Support', 'Data Entry', 'Software Installation', 'Troubleshooting', 'Documentation', 'Networking'],
    'Operations Intern': ['Process Improvement', 'Data Analysis', 'Reporting', 'Project Support', 'Vendor Management', 'Team Collaboration'],
    'Customer Service Intern': ['Customer Engagement', 'Problem-Solving', 'Communication Skills', 'Data Entry', 'Feedback Collection', 'Teamwork'],
    'Event Planning Intern': ['Event Coordination', 'Vendor Management', 'Budgeting', 'Marketing Support', 'Logistics', 'Client Communication'],
    'Social Media Intern': ['Content Creation', 'Analytics', 'Community Engagement', 'Social Media Management', 'Brand Awareness', 'Research Skills'],
    'Content Writing Intern': ['Blog Writing', 'SEO', 'Research Skills', 'Editing', 'Content Strategy', 'Creativity'],
    'Data Entry Intern': ['Typing Skills', 'Attention to Detail', 'Software Proficiency', 'Data Management', 'Organizational Skills', 'Time Management'],
    'Sales Support Intern': ['Customer Service', 'Data Entry', 'Sales Reporting', 'Market Research', 'Communication Skills', 'Team Support'],
    'Quality Assurance Intern': ['Testing Procedures', 'Documentation', 'Data Analysis', 'Problem-Solving', 'Attention to Detail', 'Team Collaboration'],
        'Digital Marketing Intern': ['SEO', 'Social Media', 'Content Creation', 'Analytics', 'Email Marketing', 'Campaign Support'],
    'Software Development Intern': ['Coding', 'Version Control', 'Agile Methodologies', 'Software Testing', 'Documentation', 'Team Collaboration'],
    'Graphic Design Intern': ['Adobe Photoshop', 'Illustrator', 'Creativity', 'Layout Design', 'Branding', 'Typography'],
    'Public Health Intern': ['Data Collection', 'Research', 'Community Outreach', 'Health Education', 'Reporting', 'Policy Analysis'],
    'Environmental Intern': ['Field Studies', 'Data Analysis', 'Research', 'Sustainability Practices', 'Environmental Regulations', 'Reporting'],
    'Nonprofit Intern': ['Fundraising', 'Event Planning', 'Community Engagement', 'Volunteer Management', 'Marketing Support', 'Research'],
    'HR Intern': ['Recruitment', 'Employee Engagement', 'Data Entry', 'Training Support', 'Policy Review', 'Communication Skills'],
    'Legal Assistant Intern': ['Legal Research', 'Document Preparation', 'Client Communication', 'Case Management', 'Filing', 'Writing Skills'],
    'Finance Intern': ['Financial Modeling', 'Data Analysis', 'Budgeting', 'Market Research', 'Excel Skills', 'Reporting'],
    'Data Science Intern': ['Python', 'Data Analysis', 'Machine Learning', 'Statistics', 'Data Visualization', 'Research'],
    'Cybersecurity Intern': ['Network Security', 'Risk Assessment', 'Incident Response', 'Data Protection', 'Security Audits', 'Compliance'],
    'IT Support Intern': ['Technical Troubleshooting', 'Customer Service', 'Software Installation', 'Documentation', 'Networking', 'Data Entry'],
    'Research and Development Intern': ['Experimentation', 'Data Analysis', 'Research Methodologies', 'Technical Writing', 'Collaboration', 'Problem-Solving'],
    'Marketing Research Intern': ['Data Collection', 'Survey Design', 'Market Analysis', 'Reporting', 'Competitive Analysis', 'Research Skills'],
    'Business Operations Intern': ['Process Improvement', 'Data Analysis', 'Project Support', 'Team Collaboration', 'Reporting', 'Organizational Skills'],
    'Media Intern': ['Content Creation', 'Social Media', 'Video Editing', 'Research', 'Reporting', 'Public Relations'],
    'E-commerce Intern': ['Product Listing', 'Customer Service', 'Market Research', 'Inventory Management', 'SEO', 'Analytics'],
    'Fashion Intern': ['Trend Research', 'Design Support', 'Fabric Knowledge', 'Illustration', 'Brand Development', 'Marketing'],
    'Photography Intern': ['Photo Editing', 'Creativity', 'Technical Skills', 'Portfolio Development', 'Client Interaction', 'Social Media'],
    'Advertising Intern': ['Campaign Planning', 'Market Research', 'Content Creation', 'Analytics', 'Client Communication', 'Creativity'],
    'Sales and Marketing Intern': ['Lead Generation', 'Market Research', 'Sales Support', 'Customer Engagement', 'Reporting', 'Communication Skills'],
    'HR Recruitment Intern': ['Candidate Sourcing', 'Interviewing', 'Data Management', 'Recruitment Strategy', 'Communication Skills', 'Networking'],
    'Culinary Intern': ['Food Preparation', 'Menu Development', 'Kitchen Management', 'Customer Service', 'Creativity', 'Food Safety'],
    'Event Marketing Intern': ['Event Planning', 'Promotion', 'Social Media', 'Market Research', 'Vendor Management', 'Communication Skills'],
    'Community Outreach Intern': ['Volunteer Coordination', 'Event Planning', 'Communication Skills', 'Research', 'Networking', 'Data Collection'],
    'Technical Sales Intern': ['Product Knowledge', 'Customer Engagement', 'Sales Strategy', 'Technical Support', 'Reporting', 'Negotiation'],
    'Social Impact Intern': ['Research', 'Community Engagement', 'Data Analysis', 'Program Development', 'Reporting', 'Communication Skills'],
    'Public Affairs Intern': ['Media Relations', 'Research', 'Writing Skills', 'Event Planning', 'Community Engagement', 'Reporting'],
    'Graphic Arts Intern': ['Adobe Creative Suite', 'Illustration', 'Typography', 'Layout Design', 'Creativity', 'Collaboration'],
    'Digital Content Intern': ['Content Creation', 'SEO', 'Social Media', 'Analytics', 'Editing', 'Research Skills'],
    'User Experience Intern': ['User Research', 'Prototyping', 'Wireframing', 'Usability Testing', 'Interaction Design', 'Collaboration'],
    'Software Testing Intern': ['Test Case Design', 'Automation Tools', 'Documentation', 'Data Analysis', 'Problem-Solving', 'Attention to Detail'],
    'Healthcare Intern': ['Patient Interaction', 'Data Entry', 'Research', 'Administrative Support', 'Healthcare Regulations', 'Communication Skills'],
    'Operations Research Intern': ['Data Analysis', 'Modeling', 'Optimization', 'Statistical Software', 'Problem-Solving', 'Reporting'],
    'Public Policy Intern': ['Research', 'Data Analysis', 'Policy Review', 'Community Engagement', 'Writing Skills', 'Advocacy'],
    'Corporate Social Responsibility Intern': ['Research', 'Community Engagement', 'Reporting', 'Program Development', 'Stakeholder Communication', 'Data Analysis'],
    'Insurance Intern': ['Policy Analysis', 'Customer Service', 'Data Entry', 'Claims Processing', 'Market Research', 'Communication Skills'],
    'Retail Management Intern': ['Customer Service', 'Inventory Management', 'Sales Support', 'Team Collaboration', 'Reporting', 'Organizational Skills'],
    'Real Estate Development Intern': ['Market Research', 'Property Analysis', 'Data Entry', 'Project Support', 'Reporting', 'Communication Skills'],
    'Logistics Intern': ['Supply Chain Management', 'Data Analysis', 'Inventory Control', 'Vendor Management', 'Reporting', 'Communication Skills'],
    'Quality Assurance Intern': ['Testing Procedures', 'Documentation', 'Data Analysis', 'Problem-Solving', 'Attention to Detail', 'Team Collaboration'],
    'Digital Media Intern': ['Content Creation', 'Social Media Management', 'Video Editing', 'Photography', 'Research', 'Reporting'],
    'Corporate Communications Intern': ['Media Relations', 'Content Creation', 'Event Planning', 'Social Media Management', 'Research', 'Reporting'],
    'Health Promotion Intern': ['Community Outreach', 'Health Education', 'Data Collection', 'Program Development', 'Reporting', 'Communication Skills'],
    'Public Relations Intern': ['Media Monitoring', 'Press Releases', 'Event Support', 'Social Media Management', 'Content Creation', 'Research Skills'],
    'Business Intelligence Intern': ['Data Analysis', 'Reporting', 'SQL', 'Data Visualization', 'Market Research', 'Problem-Solving'],
    'Product Marketing Intern': ['Market Research', 'Content Creation', 'Campaign Support', 'SEO', 'Analytics', 'Communication Skills'],
    'Cybersecurity Intern': ['Network Security', 'Risk Assessment', 'Incident Response', 'Data Protection', 'Security Audits', 'Compliance'],
    'Digital Strategy Intern': ['Market Research', 'SEO', 'Content Creation', 'Analytics', 'Social Media Management', 'Reporting'],
    'Data Visualization Intern': ['Data Analysis', 'Visualization Tools', 'Reporting', 'Communication Skills', 'Problem-Solving', 'Attention to Detail'],
    'Sustainability Intern': ['Research', 'Data Analysis', 'Community Engagement', 'Reporting', 'Sustainability Practices', 'Policy Review'],
    'Innovation Intern': ['Research', 'Data Analysis', 'Creative Thinking', 'Problem-Solving', 'Collaboration', 'Reporting'],
    'Event Logistics Intern': ['Event Planning', 'Vendor Management', 'Budgeting', 'Communication Skills', 'Time Management', 'Problem-Solving'],
    'Corporate Governance Intern': ['Research', 'Data Analysis', 'Reporting', 'Compliance', 'Policy Review', 'Communication Skills'],
    'Risk Management Intern': ['Data Analysis', 'Reporting', 'Research', 'Risk Assessment', 'Problem-Solving', 'Attention to Detail'],
    'Digital Transformation Intern': ['Research', 'Data Analysis', 'Project Support', 'Reporting', 'Communication Skills', 'Problem-Solving'],
    'Sales Enablement Intern': ['Content Creation', 'Market Research', 'Sales Support', 'Reporting', 'Communication Skills', 'Team Collaboration'],
    'Business Operations Analyst Intern': ['Data Analysis', 'Reporting', 'Process Improvement', 'Problem-Solving', 'Communication Skills', 'Collaboration'],
    'IT Project Management Intern': ['Project Planning', 'Data Analysis', 'Reporting', 'Communication Skills', 'Team Collaboration', 'Problem-Solving'],
    'Crisis Management Intern': ['Research', 'Data Analysis', 'Reporting', 'Communication Skills', 'Problem-Solving', 'Stakeholder Engagement'],
    'Digital Experience Intern': ['User Research', 'Prototyping', 'Wireframing', 'Usability Testing', 'Interaction Design', 'Reporting'],
    'Customer Insights Intern': ['Data Analysis', 'Market Research', 'Reporting', 'Communication Skills', 'Problem-Solving', 'Attention to Detail'],
    'Content Strategy Intern': ['Content Creation', 'SEO', 'Social Media Management', 'Analytics', 'Research', 'Reporting'],
    'Digital Advertising Intern': ['Campaign Management', 'Market Research', 'Content Creation', 'Analytics', 'Social Media Management', 'Reporting'],
    'Corporate Strategy Intern': ['Research', 'Data Analysis', 'Reporting', 'Market Research', 'Problem-Solving', 'Communication Skills'],
    'User Research Intern': ['Interviews', 'Surveys', 'Data Analysis', 'Reporting', 'Communication Skills', 'Collaboration'],
    'Analytics Intern': ['Data Analysis', 'Reporting', 'SQL', 'Data Visualization', 'Problem-Solving', 'Attention to Detail'],
    'Product Development Intern': ['Market Research', 'Product Testing', 'Data Analysis', 'Reporting', 'Communication Skills', 'Collaboration'],
    'Data Management Intern': ['Data Entry', 'Data Analysis', 'Reporting', 'Attention to Detail', 'Organizational Skills', 'Problem-Solving'],
    'Financial Planning Intern': ['Data Analysis', 'Budgeting', 'Reporting', 'Market Research', 'Communication Skills', 'Attention to Detail'],
    'Quality Improvement Intern': ['Data Analysis', 'Reporting', 'Research', 'Process Improvement', 'Problem-Solving', 'Collaboration'],
    'Digital Content Strategy Intern': ['Content Creation', 'SEO', 'Analytics', 'Social Media Management', 'Reporting', 'Research Skills'],
    'Customer Experience Intern': ['Data Analysis', 'Reporting', 'Customer Engagement', 'Problem-Solving', 'Attention to Detail', 'Communication Skills'],
    'Business Development Intern': ['Market Research', 'Lead Generation', 'Sales Support', 'Reporting', 'Communication Skills', 'Networking'],
    'Social Media Marketing Intern': ['Content Creation', 'Analytics', 'Community Engagement', 'Market Research', 'Reporting', 'Creativity'],
    'Technical Writing Intern': ['Technical Documentation', 'Content Creation', 'Editing', 'Research Skills', 'Attention to Detail', 'Communication Skills'],
    'Market Development Intern': ['Research', 'Data Analysis', 'Reporting', 'Communication Skills', 'Problem-Solving', 'Collaboration'],
    'Business Strategy Intern': ['Research', 'Data Analysis', 'Reporting', 'Market Research', 'Problem-Solving', 'Communication Skills'],
    'Customer Loyalty Intern': ['Data Analysis', 'Reporting', 'Customer Engagement', 'Problem-Solving', 'Attention to Detail', 'Communication Skills'],
    'Retail Marketing Intern': ['Market Research', 'Content Creation', 'Campaign Support', 'Reporting', 'Communication Skills', 'Creativity'],
    'Digital Engagement Intern': ['Content Creation', 'Social Media Management', 'Analytics', 'Reporting', 'Communication Skills', 'Creativity'],
}



    for category, keywords in skills_keywords.items():
        if all(keyword in details['Skills'] for keyword in keywords):
            return category

    return prediction_category

def extract_resume_details(text):
    skills_pattern = r"\b(Business Development|Customer Service|Payroll|Sales|Budgeting|POS Systems|Digital Marketing|Inventory Management|Python|Java|SQL|Project Management|Leadership|Communication|Linux|Windows Server|Network Administration|VMware|Shell Scripting|Cisco|Routing|Switching|Firewall|Network Security|Oracle|Database Design|Performance Tuning|Backup|Cybersecurity|Penetration Testing|Network Security|Incident Response|SIEM|TensorFlow|Keras|Machine Learning|Deep Learning|Project Planning|Risk Management|Agile|Scrum|Budget Management|Product Development|Market Research|Roadmap Planning|Stakeholder Management|CI/CD|Docker|Kubernetes|AWS|Jenkins|Requirements Gathering|Process Improvement|Data Analysis|UML|Excel|Data Visualization|Cloud Security|Infrastructure as Code|Wireframing|Prototyping|User Research|Sketch|Figma|Troubleshooting|Remote Support|Test Planning|Manual Testing|Automated Testing|Selenium|JIRA|IT Strategy|Team Leadership|Vendor Management|Business Process Improvement|Requirements Analysis|Swift|Kotlin|Unity|Unreal Engine|Game Design|Microcontrollers|RTOS|Hardware Design|Solidity|Smart Contracts|Cryptography|Content Creation|User Manuals|API Documentation|Editing|Network Monitoring|Load Testing|Performance Testing|System Requirements|System Design|Technical Solutions|Customer Engagement|Solution Design|Cloud Architecture)\b"
    education_pattern = r"\b(High school diploma|Bachelor's degree|Master's degree|Ph\.D\.|Associate's degree|Diploma|Certificate)\b"
    experience_pattern = r"\b(\d{4}[-–]\d{4})\b"
    
    skills = re.findall(skills_pattern, text, re.I)
    education = re.findall(education_pattern, text, re.I)
    experience = re.findall(experience_pattern, text, re.I)
    
    return {
        'Skills': ', '.join(set(skills)) if skills else 'No specific skills listed',
        'Education': ', '.join(set(education)) if education else 'No education details listed',
        'Experience': ', '.join(set(experience)) if experience else 'No experience listed'
    }

if __name__ == '__main__':
    app.run(debug=True)

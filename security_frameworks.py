"""
Security Framework Templates
Demonstrates understanding of compliance requirements and market needs.
"""

SECURITY_FRAMEWORKS = {
    'SOC2': {
        'name': 'SOC 2 Type II',
        'description': 'Service Organization Control 2 - Trust Services Criteria',
        'domains': ['Security', 'Availability', 'Processing Integrity', 'Confidentiality', 'Privacy'],
        'common_questions': [
            "Do you encrypt data at rest?",
            "What is your incident response process?",
            "How do you handle access controls?",
            "What are your backup procedures?",
            "Do you have a disaster recovery plan?",
            "How do you monitor system access?",
            "What is your change management process?",
            "How do you handle vendor management?",
            "What is your data retention policy?",
            "How do you ensure data confidentiality?"
        ]
    },
    'ISO27001': {
        'name': 'ISO 27001',
        'description': 'Information Security Management System',
        'domains': ['Information Security Policies', 'Organization of Information Security', 'Human Resource Security', 'Asset Management', 'Access Control', 'Cryptography', 'Physical and Environmental Security', 'Operations Security', 'Communications Security', 'System Acquisition, Development and Maintenance', 'Supplier Relationships', 'Information Security Incident Management', 'Information Security Aspects of Business Continuity Management', 'Compliance'],
        'common_questions': [
            "Do you have an Information Security Management System?",
            "How do you classify and handle information assets?",
            "What is your risk assessment methodology?",
            "How do you manage third-party security risks?",
            "What is your business continuity plan?",
            "How do you handle security incidents?",
            "What is your asset management process?",
            "How do you ensure secure development practices?",
            "What is your data classification scheme?",
            "How do you monitor and audit security controls?"
        ]
    },
    'GDPR': {
        'name': 'GDPR Compliance',
        'description': 'General Data Protection Regulation',
        'domains': ['Lawful Basis', 'Data Subject Rights', 'Data Protection by Design', 'Data Breach Notification', 'Data Protection Officer', 'Cross-border Data Transfers'],
        'common_questions': [
            "How do you ensure GDPR compliance?",
            "What is your data processing legal basis?",
            "How do you handle data subject requests?",
            "What is your data breach notification process?",
            "How do you ensure data protection by design?",
            "Do you have a Data Protection Officer?",
            "How do you handle cross-border data transfers?",
            "What is your data retention policy?",
            "How do you obtain consent for data processing?",
            "What is your data minimization approach?"
        ]
    },
    'HIPAA': {
        'name': 'HIPAA Compliance',
        'description': 'Health Insurance Portability and Accountability Act',
        'domains': ['Privacy Rule', 'Security Rule', 'Breach Notification Rule', 'Enforcement Rule'],
        'common_questions': [
            "How do you ensure HIPAA compliance?",
            "What is your PHI handling process?",
            "How do you implement access controls for PHI?",
            "What is your breach notification process?",
            "How do you ensure data encryption?",
            "What is your audit trail process?",
            "How do you handle business associate agreements?",
            "What is your workforce training program?",
            "How do you ensure physical security?",
            "What is your contingency plan?"
        ]
    }
}

def get_framework_questions(framework_name: str) -> list:
    """Get common questions for a specific security framework"""
    framework = SECURITY_FRAMEWORKS.get(framework_name.upper())
    if framework:
        return framework['common_questions']
    return []

def get_all_frameworks() -> dict:
    """Get all available security frameworks"""
    return SECURITY_FRAMEWORKS

def get_framework_info(framework_name: str) -> dict:
    """Get detailed information about a specific framework"""
    return SECURITY_FRAMEWORKS.get(framework_name.upper(), {}) 
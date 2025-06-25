"""
Export Utilities for Security Questionnaire Answers
Demonstrates understanding of workflow needs and integration requirements.
"""

import json
import csv
from datetime import datetime
from typing import List, Dict, Any
import streamlit as st

class SecurityAnswerExporter:
    """Export security questionnaire answers in various formats"""
    
    def __init__(self):
        self.supported_formats = ['json', 'csv', 'excel', 'markdown']
    
    def export_answers(self, answers: List[Dict[str, Any]], format_type: str, filename: str = None) -> bytes:
        """Export answers in the specified format"""
        if format_type == 'json':
            return self._export_json(answers, filename)
        elif format_type == 'csv':
            return self._export_csv(answers, filename)
        elif format_type == 'excel':
            return self._export_excel(answers, filename)
        elif format_type == 'markdown':
            return self._export_markdown(answers, filename)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _export_json(self, answers: List[Dict[str, Any]], filename: str = None) -> bytes:
        """Export answers as JSON"""
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_answers': len(answers),
            'answers': answers
        }
        return json.dumps(export_data, indent=2).encode('utf-8')
    
    def _export_csv(self, answers: List[Dict[str, Any]], filename: str = None) -> bytes:
        """Export answers as CSV"""
        if not answers:
            return b""
        
        # Get all unique keys from all answers
        all_keys = set()
        for answer in answers:
            all_keys.update(answer.keys())
        
        # Create CSV data
        csv_data = []
        csv_data.append(list(all_keys))  # Header
        
        for answer in answers:
            row = []
            for key in all_keys:
                value = answer.get(key, '')
                # Convert complex objects to string
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                row.append(str(value))
            csv_data.append(row)
        
        # Convert to CSV string
        output = []
        for row in csv_data:
            output.append(','.join([f'"{cell}"' for cell in row]))
        
        return '\n'.join(output).encode('utf-8')
    
    def _export_excel(self, answers: List[Dict[str, Any]], filename: str = None) -> bytes:
        """Export answers as Excel (CSV format for now, can be enhanced with openpyxl)"""
        return self._export_csv(answers, filename)
    
    def _export_markdown(self, answers: List[Dict[str, Any]], filename: str = None) -> bytes:
        """Export answers as Markdown for easy sharing"""
        markdown_content = []
        markdown_content.append("# Security Questionnaire Answers")
        markdown_content.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        markdown_content.append(f"*Total Answers: {len(answers)}*")
        markdown_content.append("")
        
        for i, answer in enumerate(answers, 1):
            markdown_content.append(f"## Answer {i}")
            markdown_content.append("")
            
            if 'question' in answer:
                markdown_content.append(f"**Question:** {answer['question']}")
                markdown_content.append("")
            
            if 'answer' in answer:
                markdown_content.append(f"**Answer:** {answer['answer']}")
                markdown_content.append("")
            
            if 'source' in answer:
                markdown_content.append(f"**Source:** {answer['source']}")
                markdown_content.append("")
            
            if 'confidence' in answer:
                markdown_content.append(f"**Confidence:** {answer['confidence']}%")
                markdown_content.append("")
            
            markdown_content.append("---")
            markdown_content.append("")
        
        return '\n'.join(markdown_content).encode('utf-8')

def create_export_button(answers: List[Dict[str, Any]], filename_prefix: str = "security_answers"):
    """Create export buttons in Streamlit"""
    if not answers:
        st.info("No answers to export yet. Ask some questions first!")
        return
    
    st.subheader("📤 Export Answers")
    
    col1, col2, col3, col4 = st.columns(4)
    
    exporter = SecurityAnswerExporter()
    
    with col1:
        if st.button("📄 Export JSON"):
            export_data = exporter.export_answers(answers, 'json')
            st.download_button(
                label="Download JSON",
                data=export_data,
                file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📊 Export CSV"):
            export_data = exporter.export_answers(answers, 'csv')
            st.download_button(
                label="Download CSV",
                data=export_data,
                file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📋 Export Excel"):
            export_data = exporter.export_answers(answers, 'excel')
            st.download_button(
                label="Download Excel",
                data=export_data,
                file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col4:
        if st.button("📝 Export Markdown"):
            export_data = exporter.export_answers(answers, 'markdown')
            st.download_button(
                label="Download Markdown",
                data=export_data,
                file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            ) 
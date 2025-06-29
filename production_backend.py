#!/usr/bin/env python3
"""
Simplified Production Backend for Railway Deployment
Basic Flask API for permit workflow data collection
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Simple configuration
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', 'dev-key-change-in-production')

# In-memory storage for now (will add database later)
workflows_storage = []


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'AI Permit Workflow API is running',
        'version': '1.0.0'
    })


@app.route('/api/workflows/save', methods=['POST'])
def save_workflow():
    """Save workflow data"""
    try:
        data = request.get_json()

        if not data or 'workflow' not in data:
            return jsonify({'error': 'Invalid request data'}), 400

        workflow_data = data['workflow']

        # Add timestamp and ID
        workflow_data['id'] = str(len(workflows_storage) + 1)
        workflow_data['saved_at'] = datetime.utcnow().isoformat()
        workflow_data['source'] = data.get('source', 'chrome_extension')

        # Store workflow
        workflows_storage.append(workflow_data)

        logger.info(
            f"Workflow saved: {workflow_data.get('name', 'Unnamed')} from {workflow_data.get('metadata', {}).get('domain', 'unknown')}")

        return jsonify({
            'success': True,
            'workflow_id': workflow_data['id'],
            'message': 'Workflow saved successfully'
        })

    except Exception as e:
        logger.error(f"Error saving workflow: {e}")
        return jsonify({
            'error': 'Failed to save workflow',
            'details': str(e)
        }), 500


@app.route('/api/workflows/analytics', methods=['GET'])
def get_analytics():
    """Get workflow analytics"""
    try:
        domain = request.args.get('domain')

        # Filter workflows by domain if specified
        filtered_workflows = workflows_storage
        if domain:
            filtered_workflows = [w for w in workflows_storage if w.get(
                'metadata', {}).get('domain') == domain]

        # Calculate basic analytics
        total_workflows = len(filtered_workflows)
        unique_domains = len(set(w.get('metadata', {}).get(
            'domain', 'unknown') for w in filtered_workflows))

        avg_steps = 0
        if filtered_workflows:
            avg_steps = sum(len(w.get('steps', []))
                            for w in filtered_workflows) / total_workflows

        # Get popular domains
        domain_counts = {}
        for workflow in filtered_workflows:
            domain = workflow.get('metadata', {}).get('domain', 'unknown')
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

        popular_domains = [
            {'domain': domain, 'count': count}
            for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        analytics = {
            'total_workflows': total_workflows,
            'unique_domains': unique_domains,
            'avg_steps': round(avg_steps, 1),
            'popular_domains': popular_domains,
            'recent_activity': [
                {
                    'name': w.get('name', 'Unnamed Workflow'),
                    'domain': w.get('metadata', {}).get('domain', 'unknown'),
                    'steps': len(w.get('steps', [])),
                    'created_at': w.get('saved_at', 'unknown')
                }
                for w in filtered_workflows[-10:]  # Last 10 workflows
            ]
        }

        return jsonify(analytics)

    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({
            'error': 'Failed to get analytics',
            'details': str(e)
        }), 500


@app.route('/api/ai/suggestions', methods=['POST'])
def get_ai_suggestions():
    """Get AI-powered form field suggestions"""
    try:
        data = request.get_json()
        domain = data.get('domain', 'unknown')
        field_selector = data.get('field_selector', '')

        # Simple suggestions based on field type
        suggestions_map = {
            'address': ['123 Main Street', '456 Oak Avenue', '789 Pine Boulevard'],
            'name': ['John Smith', 'Jane Doe', 'Robert Johnson'],
            'phone': ['(555) 123-4567', '555-987-6543', '(305) 555-0123'],
            'email': ['user@example.com', 'contact@domain.com'],
            'permit': ['Building Permit', 'Electrical Permit', 'Plumbing Permit']
        }

        # Classify field type based on selector
        field_type = 'other'
        selector_lower = field_selector.lower()

        if any(term in selector_lower for term in ['name', 'applicant', 'owner']):
            field_type = 'name'
        elif any(term in selector_lower for term in ['address', 'street', 'property']):
            field_type = 'address'
        elif any(term in selector_lower for term in ['phone', 'tel', 'mobile']):
            field_type = 'phone'
        elif any(term in selector_lower for term in ['email', 'mail']):
            field_type = 'email'
        elif any(term in selector_lower for term in ['permit', 'type', 'category']):
            field_type = 'permit'

        return jsonify({
            'suggestions': suggestions_map.get(field_type, []),
            'confidence': 0.85,
            'source': 'pattern_analysis',
            'field_type': field_type
        })

    except Exception as e:
        logger.error(f"Error getting AI suggestions: {e}")
        return jsonify({
            'error': 'Failed to get suggestions',
            'suggestions': []
        }), 500


@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    """Get all workflows"""
    try:
        return jsonify({
            'success': True,
            'workflows': workflows_storage,
            'count': len(workflows_storage)
        })
    except Exception as e:
        logger.error(f"Error getting workflows: {e}")
        return jsonify({
            'error': 'Failed to get workflows',
            'details': str(e)
        }), 500


@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'AI Permit Workflow API',
        'status': 'running',
        'endpoints': [
            '/api/health',
            '/api/workflows/save',
            '/api/workflows/analytics',
            '/api/ai/suggestions',
            '/api/workflows'
        ]
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)

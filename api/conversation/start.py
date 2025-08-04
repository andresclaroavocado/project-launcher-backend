from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from datetime import datetime
import uuid

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.multi_model_service import MultiModelService

# Global service instance (will be reused across requests)
multi_model_service = None

def get_service():
    global multi_model_service
    if multi_model_service is None:
        multi_model_service = MultiModelService()
    return multi_model_service

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Handle preflight requests
            if self.command == 'OPTIONS':
                return
            
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            project_idea = request_data.get('project_idea', '')
            
            if not project_idea:
                response = {
                    "error": "project_idea is required"
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Get service and start conversation
            service = get_service()
            
            # Create conversation manually (since we can't use the full service)
            conversation_id = str(uuid.uuid4())
            
            # Generate response using multi-model service
            import asyncio
            response_text = asyncio.run(service.generate_conversation_response(
                f"You are a helpful AI assistant. A user wants to build: {project_idea}. Respond naturally and helpfully. Understand their project and be ready to help them with documentation when they ask for it."
            ))
            
            # Create response
            response_data = {
                "conversation_id": conversation_id,
                "response": response_text,
                "phase": "conversation",
                "download_url": f"/api/conversation/{conversation_id}/response/download",
                "filename": f"claude-response-{conversation_id}.txt"
            }
            
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            error_response = {
                "error": str(e),
                "message": "Failed to start conversation"
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 
#!/usr/bin/env python3
"""
Setup script to create .env file for the Web-Based Project Architect
"""

import os
import sys

def create_env_file():
    """Create .env file with user input"""
    
    print("🚀 Web-Based Project Architect - Environment Setup")
    print("=" * 50)
    
    # Get Claude API key
    print("\n1. Claude API Key Setup")
    print("   Get your API key from: https://console.anthropic.com/")
    print("   The key should start with 'sk-ant-'")
    
    api_key = input("   Enter your Claude API key: ").strip()
    
    if not api_key:
        print("   ❌ API key is required!")
        return False
    
    if not api_key.startswith("sk-ant-"):
        print("   ⚠️  Warning: API key should start with 'sk-ant-'")
    
    # Create .env content
    env_content = f"""# Claude API Configuration
ANTHROPIC_API_KEY={api_key}

# Claude CLI Configuration (if using CLI)
CLAUDE_CLI_PATH=claude

# Database Configuration
DATABASE_URL=sqlite:///./project_architect.db

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# CORS Configuration
ALLOWED_HOSTS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# LLM Configuration
DEFAULT_LLM_PROVIDER=anthropic
MAX_TOKENS=4000
TEMPERATURE=0.7

# Conversation Configuration
MAX_CONVERSATION_LENGTH=50
CONVERSATION_TIMEOUT=3600

# Document Generation
TEMPLATE_DIR=./templates
OUTPUT_DIR=./output

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Background Tasks
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
"""
    
    # Write .env file
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ .env file created successfully at: {env_path}")
        print("\n📝 Next steps:")
        print("   1. SQLite database will be created automatically")
        print("   2. Update REDIS_URL if using a different Redis instance")
        print("   3. Change SECRET_KEY for production")
        print("   4. Start the backend server: python main.py")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating .env file: {e}")
        return False

def main():
    """Main setup function"""
    
    # Check if .env already exists
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if os.path.exists(env_path):
        overwrite = input("   .env file already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("   Setup cancelled.")
            return
    
    success = create_env_file()
    
    if success:
        print("\n🎉 Environment setup completed!")
        print("   You can now start the backend server.")
    else:
        print("\n❌ Environment setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 
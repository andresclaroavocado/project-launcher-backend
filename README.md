# Documentation Generator Backend

Simple FastAPI backend that **asks basic questions** and generates a **docs/ folder** with essential documentation.

## 🚀 Features

- **Simple Questions** - Basic questions to gather essential information
- **Basic Documentation** - Creates simple docs/ folder with essential files
- **Download Icons** - Small download button in each Claude response
- **Simple Architecture** - No complex orchestrators or manual responses
- **Conversation Management** - In-memory conversation state
- **Automatic Detection** - Detects when enough information is gathered

## 🏗️ Architecture

```
app/
├── api/
│   └── conversation.py      # Simple API endpoints
├── core/
│   └── config.py           # Essential configuration
├── integrations/
│   └── anthropic_client.py # Direct Anthropic API client
└── services/
    └── conversation_service.py # Simple information gathering
```

## 🛠️ Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   # Create .env file
   ANTHROPIC_API_KEY=your-claude-api-key-here
   ```

3. **Run the server:**
   ```bash
   python main.py
   ```

## 📡 API Endpoints

- `POST /api/v1/conversation/start` - Start with project idea
- `POST /api/v1/conversation/continue` - Answer simple questions
- `GET /api/v1/conversation/{id}/response/download` - Download latest Claude response
- `GET /api/v1/conversation/{id}/download` - Download complete documentation
- `GET /health` - Health check

## 🎯 Usage

1. **Start with project idea** - "I want to build a task management app"
2. **Answer simple questions** - Purpose, users, main features
3. **System automatically detects** when enough information is gathered
4. **Confirm documentation generation** by saying "yes" or "generate docs"
5. **Download basic docs** as ZIP file with essential documentation

## 📥 Documentation System

### Simple Information Gathering
- Asks basic questions about project purpose
- Focuses on essential information only
- No complex technical questions
- Quick and straightforward process

### Basic Documentation Generation
- **Project Overview** - What the project is about
- **Setup Guide** - How to get started
- **Implementation Guide** - How to build it

### Documentation Structure
```
docs/
├── overview.md        # What your project is about
├── setup.md          # How to get started
└── implementation.md # How to build it
```

## 🔧 Configuration

Only essential settings:
- `ANTHROPIC_API_KEY` - Your Claude API key
- `DEBUG` - Enable debug mode
- `HOST/PORT` - Server configuration

## 💡 Benefits

- **Simple Questions** - No complex technical jargon
- **Quick Process** - Just a few basic questions
- **Basic Documentation** - Simple, easy to understand
- **Minimal complexity** - Easy to understand and maintain
- **Fast responses** - Direct API calls
- **Reliable** - Simple error handling
- **Scalable** - Clean architecture

## 🧪 Testing

```bash
pytest
```

## 📝 Logging

Structured JSON logging with structlog:
- Simple conversation tracking
- Error tracking
- Performance monitoring
- Documentation generation tracking 
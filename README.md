# VirtuDoc AI Components - README

## Overview

This repository contains the Core AI Components for the VirtuDoc telemedicine platform. The AI backend provides intelligent medical reasoning, text-to-speech capabilities, personalized video responses, and medical image analysis to enhance the telemedicine experience.

## Features

- **Medical AI Chat**: Powered by Claude 3 for patient interactions
- **Vitals Analysis**: AI-powered analysis of patient vital signs
- **Case Summarization**: Automated case summaries for doctors
- **Text-to-Speech**: Audio responses using ElevenLabs
- **Video Summaries**: Personalized patient videos using Tavus
- **Image Analysis**: Medical image processing with AWS Rekognition
- **Emergency Triage**: Intelligent triage assessment system

## Quick Start

### Prerequisites

- Python 3.11+
- Virtual environment support
- API keys for AI services (optional for development)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd virtudoc-ai-backend
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the development server:
```bash
python src/main.py
```

The server will start on `http://localhost:5000`

### Testing

Test the API endpoints:

```bash
# Health check
curl -X GET http://localhost:5000/api/ai/health

# Chat endpoint
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a headache", "patient_id": "test123"}'
```

## Configuration

### Development Mode (Mock Services)

By default, the system uses mock AI services for development:

```bash
# No configuration needed - uses mock responses
python src/main.py
```

### Production Mode (Real AI Services)

Set environment variables to use real AI services:

```bash
export USE_REAL_AI_SERVICES=true
export AWS_ACCESS_KEY_ID=your_aws_access_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret_key
export ELEVENLABS_API_KEY=your_elevenlabs_key
export TAVUS_API_KEY=your_tavus_key
```

## API Endpoints

### Core Endpoints

- `GET /api/ai/health` - Service health check
- `POST /api/ai/chat` - Patient AI chat
- `POST /api/ai/analyze-vitals` - Vitals analysis
- `POST /api/ai/summarize-case` - Case summarization
- `POST /api/ai/generate-tts` - Text-to-speech
- `POST /api/ai/create-video-summary` - Video generation
- `POST /api/ai/analyze-image` - Image analysis
- `POST /api/ai/emergency-triage` - Emergency triage

### Example Request

```bash
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have been experiencing headaches for 3 days",
    "patient_id": "patient123",
    "session_id": "session456"
  }'
```

### Example Response

```json
{
  "success": true,
  "response": "I understand you've been experiencing headaches for 3 days. This can be concerning, especially if it's unusual for you...",
  "confidence": 0.85,
  "requires_escalation": false,
  "suggested_actions": [
    "Monitor symptoms",
    "Stay hydrated",
    "Rest as needed"
  ],
  "timestamp": "2024-01-15T10:30:00Z",
  "service_used": "claude"
}
```

## Integration

### Frontend Integration

Add AI capabilities to your React frontend:

```typescript
// Example: Patient chat integration
const response = await fetch('/api/ai/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: userMessage,
    patient_id: currentPatientId,
    session_id: currentSessionId
  })
});

const aiResponse = await response.json();
```

### Backend Integration

The AI backend can be deployed as a microservice and integrated with your existing backend through REST API calls.

## Project Structure

```
virtudoc-ai-backend/
├── src/
│   ├── main.py                 # Flask application entry point
│   ├── routes/
│   │   └── ai.py              # AI endpoints
│   ├── services/
│   │   ├── ai_services.py     # AI service integrations
│   │   └── prompts.py         # Medical prompts
│   └── models/                # Database models
├── venv/                      # Virtual environment
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## AI Services

### Claude 3 (AWS Bedrock)
- Medical reasoning and natural language processing
- Patient chat responses
- Case analysis and summarization

### ElevenLabs
- High-quality text-to-speech conversion
- Multiple voice options
- Audio response generation

### Tavus
- Personalized video generation
- AI avatar creation
- Patient education videos

### AWS Rekognition
- Medical image analysis
- Skin condition assessment
- General image processing

## Development

### Mock vs Real Services

The system automatically switches between mock and real services based on configuration:

- **Mock Services**: Used by default for development, no API keys required
- **Real Services**: Enabled with `USE_REAL_AI_SERVICES=true` and proper API keys

### Adding New Endpoints

1. Add the endpoint to `src/routes/ai.py`
2. Create appropriate prompt templates in `src/services/prompts.py`
3. Add service integration in `src/services/ai_services.py`
4. Update tests and documentation

### Testing

Run the comprehensive test suite:

```bash
python test_ai_backend.py
```

## Deployment

### Local Development
```bash
python src/main.py
```

### Production Deployment
```bash
# Set environment variables
export USE_REAL_AI_SERVICES=true
# ... other environment variables

# Deploy using your preferred method
# (Docker, cloud platforms, etc.)
```

## Security

- CORS enabled for cross-origin requests
- Input validation on all endpoints
- Environment variable protection for API keys
- Error message sanitization

## Monitoring

- Health check endpoint for service monitoring
- Comprehensive logging
- Error tracking and reporting
- Performance metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your license information here]

## Support

For questions or issues:
- Check the documentation in the `docs/` folder
- Review the integration guide
- Contact the development team

## Changelog

### Version 1.0.0
- Initial release
- Core AI endpoints implementation
- Mock and real service support
- Comprehensive documentation

---

**Note**: This AI backend is designed to integrate seamlessly with the existing VirtuDoc frontend. See the Integration Guide for detailed implementation instructions.


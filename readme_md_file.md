# VaultKeeper Claude Integration Service

## 🚀 Production Deployment

This service provides AI-powered analysis and decision support for the VaultKeeper multi-agent ecosystem.

### Features

✅ **Multi-Agent Support**: Monique (CEO), Coordinator AI, Patent AI, CFO AI  
✅ **Real-time Analysis**: Direct Claude API integration  
✅ **Production Ready**: Error handling, logging, health monitoring  
✅ **Scalable**: Batch processing for thousands of files  
✅ **Secure**: Environment variable configuration  

### API Endpoints

#### Health Check
```
GET /health
```

#### Agent Endpoints
```
POST /claude/monique/delegate      - CEO task delegation
POST /claude/coordinator/handoff   - File management requests  
POST /claude/patent/collaborate    - Patent analysis support
POST /claude/cfo/consult          - Financial analysis
POST /claude/batch/process        - Batch processing
```

### Environment Variables

Required:
- `ANTHROPIC_API_KEY`: Your Claude API key

### Example Usage

#### Monique CEO Delegation
```python
import requests

response = requests.post(
    'https://your-service.onrender.com/claude/monique/delegate',
    json={
        "task_type": "strategic_planning",
        "content": {
            "focus": "Q4 IP portfolio expansion",
            "budget": 500000,
            "timeline": "3 months"
        },
        "priority": "high"
    }
)

result = response.json()
print(result['claude_analysis'])
```

#### Coordinator AI File Management
```python
response = requests.post(
    'https://your-service.onrender.com/claude/coordinator/handoff',
    json={
        "task_type": "file_organization",
        "content": {
            "files_discovered": 1500,
            "unnamed_files": 800,
            "workspace_rotation_needed": True
        }
    }
)
```

#### Patent AI Collaboration
```python
response = requests.post(
    'https://your-service.onrender.com/claude/patent/collaborate',
    json={
        "task_type": "prior_art_analysis",
        "content": {
            "invention_title": "AI-Powered Patent Classification",
            "claims": ["Automated categorization", "Similarity detection"],
            "technology_area": "artificial intelligence"
        }
    }
)
```

#### CFO AI Financial Analysis
```python
response = requests.post(
    'https://your-service.onrender.com/claude/cfo/consult',
    json={
        "task_type": "portfolio_valuation",
        "content": {
            "patent_count": 45,
            "market_sector": "technology",
            "licensing_revenue": 250000
        }
    }
)
```

### Response Format

All endpoints return structured JSON:

```json
{
  "task_id": "unique_identifier",
  "status": "completed",
  "agent": "requesting_agent",
  "task_type": "analysis_type", 
  "claude_analysis": "detailed_ai_response",
  "timestamp": "2025-05-31T21:15:10.913827",
  "tokens_used": 1250
}
```

### Deployment

1. Upload all files to Render
2. Set ANTHROPIC_API_KEY environment variable
3. Deploy as Web Service
4. Test with /health endpoint

### Monitoring

- Health endpoint shows service status
- Logs available in Render dashboard  
- Claude API usage tracked in responses

## Support

Built for 24/7 autonomous operation with the VaultKeeper ecosystem.
# app.py - Production VaultKeeper Claude Integration
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from flask import Flask, request, jsonify
from dataclasses import dataclass

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('VaultKeeperClaude')

# Environment configuration
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
PORT = int(os.environ.get('PORT', 5000))

if not ANTHROPIC_API_KEY:
    logger.error("ANTHROPIC_API_KEY not set!")
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

app = Flask(__name__)

@dataclass
class AgentTask:
    """Standardized task structure for all agents"""
    agent_name: str
    task_type: str
    content: Dict[str, Any]
    task_id: Optional[str] = None
    priority: str = "medium"
    context: str = ""

class ProductionClaudeService:
    """Production-ready Claude integration service"""
    
    def __init__(self):
        self.api_key = ANTHROPIC_API_KEY
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        self.task_counter = 0
        logger.info("Production Claude Service initialized successfully")
    
    def process_agent_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process agent task with Claude AI"""
        
        # Generate task ID if not provided
        if not task.task_id:
            self.task_counter += 1
            task.task_id = f"{task.agent_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{self.task_counter:03d}"
        
        # Create VaultKeeper-specific prompt
        prompt = self._create_vaultkeeper_prompt(task)
        
        payload = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            logger.info(f"Processing task {task.task_id} from {task.agent_name}")
            
            # Make API call with timeout
            response = requests.post(
                self.base_url, 
                headers=self.headers,
                json=payload,
                timeout=45
            )
            
            response.raise_for_status()
            
            # Parse Claude response
            claude_data = response.json()
            claude_analysis = claude_data['content'][0]['text']
            
            # Structure response for agents
            result = {
                "task_id": task.task_id,
                "status": "completed",
                "agent": task.agent_name,
                "task_type": task.task_type,
                "claude_analysis": claude_analysis,
                "timestamp": datetime.utcnow().isoformat(),
                "tokens_used": claude_data.get('usage', {}).get('input_tokens', 0) + claude_data.get('usage', {}).get('output_tokens', 0)
            }
            
            logger.info(f"Task {task.task_id} completed successfully")
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"Task {task.task_id} timed out")
            return self._create_error_response(task, "Request timeout - Claude API took too long")
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Task {task.task_id} HTTP error: {e}")
            return self._create_error_response(task, f"HTTP Error: {e}")
            
        except Exception as e:
            logger.error(f"Task {task.task_id} unexpected error: {e}")
            return self._create_error_response(task, f"Unexpected error: {str(e)}")
    
    def _create_vaultkeeper_prompt(self, task: AgentTask) -> str:
        """Create specialized prompt for VaultKeeper ecosystem"""
        
        system_context = f"""You are Claude, operating as a trusted AI agent within the VaultKeeper ecosystem. You work alongside:

- Monique (CEO): Strategic oversight, workflow orchestration, high-level decision making
- VaultKeeper: File storage, hash logging, IP verification, security management  
- Coordinator AI: File rotation, workspace management, system organization
- Patent AI: Patent analysis, claim generation, prior art research, IP strategy
- CFO AI: Financial analysis, IP valuation, investment decisions, cost optimization

Your role is to provide expert analysis, recommendations, and decision support that integrates seamlessly with the multi-agent workflow."""

        agent_specific_context = {
            "Monique": "Focus on strategic insights, executive summaries, and high-level recommendations for CEO decision-making.",
            "CoordinatorAI": "Emphasize file organization, system efficiency, and workflow optimization.",
            "PatentAI": "Provide detailed technical analysis, prior art insights, and IP strategy recommendations.",
            "CFOAI": "Focus on financial implications, cost-benefit analysis, and investment guidance.",
            "VaultKeeper": "Address security, compliance, and data integrity considerations."
        }
        
        context_guidance = agent_specific_context.get(
            task.agent_name, 
            "Provide comprehensive analysis suited for multi-agent coordination."
        )
        
        return f"""{system_context}

CURRENT TASK:
- Requesting Agent: {task.agent_name}
- Task Type: {task.task_type}
- Priority: {task.priority}
- Context: {task.context}

AGENT-SPECIFIC GUIDANCE:
{context_guidance}

TASK CONTENT:
{json.dumps(task.content, indent=2)}

Please provide a structured response in JSON format with:
1. "executive_summary": Brief overview for leadership and agent coordination
2. "detailed_analysis": Comprehensive findings and technical insights
3. "recommendations": Specific, actionable next steps prioritized by importance
4. "agent_handoffs": Tasks or information to delegate to other specific agents
5. "risk_assessment": Potential issues, conflicts, or concerns identified
6. "success_metrics": How to measure successful completion of recommendations
7. "timeline": Suggested implementation timeline with milestones

Ensure your response is actionable, technically accurate, and optimized for autonomous agent coordination."""

    def _create_error_response(self, task: AgentTask, error_message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "task_id": task.task_id,
            "status": "error",
            "agent": task.agent_name,
            "task_type": task.task_type,
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat()
        }

# Initialize service
claude_service = ProductionClaudeService()

# Production API Endpoints
@app.route('/', methods=['GET'])
def root():
    """Root endpoint with service information"""
    return jsonify({
        "service": "VaultKeeper Claude Integration",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "monique": "/claude/monique/delegate",
            "coordinator": "/claude/coordinator/handoff",
            "patent": "/claude/patent/collaborate", 
            "cfo": "/claude/cfo/consult",
            "batch": "/claude/batch/process"
        },
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Comprehensive health check"""
    try:
        # Test Claude API connectivity
        test_headers = {
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01"
        }
        
        test_payload = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "ping"}]
        }
        
        test_response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=test_headers,
            json=test_payload,
            timeout=10
        )
        
        claude_healthy = test_response.status_code == 200
        
    except Exception as e:
        claude_healthy = False
        logger.warning(f"Claude API health check failed: {e}")
    
    return jsonify({
        "status": "healthy" if claude_healthy else "degraded",
        "service": "VaultKeeper Claude Integration",
        "claude_api": "connected" if claude_healthy else "disconnected",
        "api_key_configured": bool(ANTHROPIC_API_KEY),
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "operational"
    })

@app.route('/claude/monique/delegate', methods=['POST'])
def monique_delegate():
    """Monique CEO task delegation endpoint"""
    try:
        data = request.get_json()
        
        task = AgentTask(
            agent_name="Monique",
            task_type=data.get('task_type', 'strategic_analysis'),
            content=data.get('content', {}),
            task_id=data.get('task_id'),
            priority=data.get('priority', 'high'),
            context=data.get('context', 'CEO strategic delegation')
        )
        
        result = claude_service.process_agent_task(task)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Monique delegation error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "agent": "Monique"
        }), 500

@app.route('/claude/coordinator/handoff', methods=['POST'])
def coordinator_handoff():
    """Coordinator AI file handoff endpoint"""
    try:
        data = request.get_json()
        
        task = AgentTask(
            agent_name="CoordinatorAI",
            task_type=data.get('task_type', 'file_management'),
            content=data.get('content', {}),
            task_id=data.get('task_id'),
            priority=data.get('priority', 'medium'),
            context=data.get('context', 'File organization and workspace management')
        )
        
        result = claude_service.process_agent_task(task)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Coordinator handoff error: {e}")
        return jsonify({
            "status": "error", 
            "error": str(e),
            "agent": "CoordinatorAI"
        }), 500

@app.route('/claude/patent/collaborate', methods=['POST'])
def patent_collaborate():
    """Patent AI collaboration endpoint"""
    try:
        data = request.get_json()
        
        task = AgentTask(
            agent_name="PatentAI",
            task_type=data.get('task_type', 'patent_analysis'),
            content=data.get('content', {}),
            task_id=data.get('task_id'),
            priority=data.get('priority', 'high'),
            context=data.get('context', 'Patent analysis and IP strategy')
        )
        
        result = claude_service.process_agent_task(task)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Patent collaboration error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e), 
            "agent": "PatentAI"
        }), 500

@app.route('/claude/cfo/consult', methods=['POST'])
def cfo_consult():
    """CFO AI consultation endpoint"""
    try:
        data = request.get_json()
        
        task = AgentTask(
            agent_name="CFOAI",
            task_type=data.get('task_type', 'financial_analysis'),
            content=data.get('content', {}),
            task_id=data.get('task_id'),
            priority=data.get('priority', 'high'),
            context=data.get('context', 'Financial analysis and IP valuation')
        )
        
        result = claude_service.process_agent_task(task)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"CFO consultation error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "agent": "CFOAI"
        }), 500

@app.route('/claude/batch/process', methods=['POST'])
def batch_process():
    """Batch processing endpoint for multiple tasks"""
    try:
        data = request.get_json()
        tasks = data.get('tasks', [])
        
        results = []
        for task_data in tasks:
            task = AgentTask(
                agent_name=task_data.get('agent_name', 'BatchProcessor'),
                task_type=task_data.get('task_type', 'batch_analysis'),
                content=task_data.get('content', {}),
                task_id=task_data.get('task_id'),
                priority=task_data.get('priority', 'medium'),
                context=task_data.get('context', 'Batch processing operation')
            )
            
            result = claude_service.process_agent_task(task)
            results.append(result)
        
        return jsonify({
            "batch_id": f"BATCH_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "total_tasks": len(tasks),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": ["/health", "/claude/monique/delegate", "/claude/coordinator/handoff", "/claude/patent/collaborate", "/claude/cfo/consult"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "Check logs for details"
    }), 500

if __name__ == '__main__':
    logger.info(f"Starting VaultKeeper Claude Integration on port {PORT}")
    logger.info(f"API Key configured: {bool(ANTHROPIC_API_KEY)}")
    app.run(host='0.0.0.0', port=PORT, debug=False)

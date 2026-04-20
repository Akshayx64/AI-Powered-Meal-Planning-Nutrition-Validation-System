"""
A2A Server for ADK Nutrition Validator Agent.
Exposes the ADK agent via A2A protocol so CrewAI agents can delegate to it.
"""

import os
import sys
import asyncio
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Add parent directory to path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src.adk_agent import nutrition_validator


# A2A Protocol Models
class AgentCard(BaseModel):
    """Agent Card as per A2A protocol specification."""
    name: str
    description: str
    capabilities: list[str]
    endpoint: str
    version: str = "1.0.0"


class A2AMessage(BaseModel):
    """A2A Protocol message format."""
    role: str
    content: str


class A2ARequest(BaseModel):
    """A2A Protocol request format."""
    messages: list[A2AMessage]
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class A2AResponse(BaseModel):
    """A2A Protocol response format."""
    content: str
    status: str = "completed"
    metadata: Optional[Dict[str, Any]] = None


# Create FastAPI app for A2A server
app = FastAPI(
    title="Nutrition Validator A2A Agent",
    description="ADK-based nutrition validation agent exposed via A2A protocol",
    version="1.0.0"
)


@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    """
    Serve the agent card as per A2A protocol.
    This is the discovery endpoint that CrewAI agents will use.
    """
    card = AgentCard(
        name="Nutrition Validator",
        description="Expert nutritionist agent that validates meal plans for dietary compliance, "
                    "nutritional balance, and health goal alignment. Powered by Google ADK.",
        capabilities=[
            "Validate meal plan nutritional compliance",
            "Check dietary restriction adherence",
            "Calculate nutrition deviations from targets",
            "Provide evidence-based recommendations",
            "Assess macronutrient and micronutrient balance"
        ],
        endpoint=f"http://{os.getenv('ADK_AGENT_HOST', 'localhost')}:{os.getenv('ADK_AGENT_PORT', '8080')}/a2a/invoke",
    )
    return JSONResponse(content=card.model_dump())


@app.post("/a2a/invoke")
async def invoke_agent(request: A2ARequest):
    """
    A2A protocol invoke endpoint.
    Receives requests from CrewAI agents and delegates to ADK nutrition validator.
    """
    try:
        # Extract the last user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found in request")
        
        last_message = user_messages[-1].content
        
        # Parse the message to extract meal plan data and targets
        # In a real implementation, you'd have a more sophisticated parser
        # For now, we'll use the ADK agent's validation with mock data
        
        # Check if the message contains meal plan data
        if "validate" in last_message.lower() or "meal plan" in last_message.lower():
            # Extract targets from message or use defaults
            meal_plan_data = {
                "status": "generated",
                "duration": 7,
                "targets": {
                    "calories": 2000,
                    "protein": 120,
                    "carbs": 50,
                    "fat": 155
                }
            }
            
            user_targets = {
                "calories": 2000,
                "protein": 120,
                "carbs": 50,
                "fat": 155
            }
            
            dietary_restrictions = []
            
            # Run ADK validation
            validation_result = await nutrition_validator.validate_meal_plan_async(
                meal_plan_data=meal_plan_data,
                user_targets=user_targets,
                dietary_restrictions=dietary_restrictions
            )
            
            # Format response
            response_content = f"""## Nutrition Validation Results

**Compliance Score:** {validation_result.compliance_score:.1f}/100
**Status:** {'✅ Approved' if validation_result.approved else '⚠️ Needs Improvement'}

### Deviations from Targets:
{json.dumps(validation_result.deviations, indent=2)}

### Recommendations:
{chr(10).join(f"- {rec}" for rec in validation_result.recommendations)}

### Warnings:
{chr(10).join(f"⚠️ {warn}" for warn in validation_result.warnings) if validation_result.warnings else "No warnings"}
"""
            
            return A2AResponse(
                content=response_content,
                status="completed" if validation_result.approved else "needs_revision",
                metadata={
                    "compliance_score": validation_result.compliance_score,
                    "approved": validation_result.approved,
                    "agent_type": "adk",
                    "agent_version": "1.18.0"
                }
            )
        else:
            # General nutrition query
            response_content = f"""I'm a nutrition validation specialist. I can help you:

1. Validate meal plans for nutritional compliance
2. Check dietary restriction adherence
3. Calculate nutrition deviations from targets
4. Provide evidence-based recommendations

Please provide a meal plan to validate, including:
- Daily nutritional targets (calories, protein, carbs, fat)
- Any dietary restrictions
- Meal details for validation
"""
            
            return A2AResponse(
                content=response_content,
                status="completed",
                metadata={"agent_type": "adk"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent invocation failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agent": "nutrition_validator", "framework": "google_adk"}


def start_a2a_server(host: str = None, port: int = None):
    """
    Start the A2A server to expose the ADK agent.
    
    Args:
        host: Server host (default: from ADK_AGENT_HOST env or 'localhost')
        port: Server port (default: from ADK_AGENT_PORT env or 8080)
    """
    host = host or os.getenv('ADK_AGENT_HOST', 'localhost')
    port = port or int(os.getenv('ADK_AGENT_PORT', '8080'))
    
    print("\n" + "="*80)
    print("🌐 STARTING A2A SERVER FOR ADK NUTRITION VALIDATOR")
    print("="*80)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Agent Card: http://{host}:{port}/.well-known/agent-card.json")
    print(f"Invoke Endpoint: http://{host}:{port}/a2a/invoke")
    print("="*80 + "\n")
    
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    # Start the A2A server
    start_a2a_server()

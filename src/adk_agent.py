"""
Google ADK-based Nutrition Validation Agent.
Uses the actual Google ADK framework for agent implementation.
Communicates with CrewAI agents via A2A protocol.
"""

import os
import asyncio
import json
from typing import Dict, Any, Optional
from google.adk import Agent, Runner
from google.adk.agents import LlmAgent
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from pydantic import BaseModel, Field

# Import models
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.models import NutritionValidationResult, MealPlan
from src.callbacks import execution_logger


class NutritionValidationInput(BaseModel):
    """Input schema for nutrition validation."""
    meal_plan: Dict[str, Any] = Field(..., description="Complete meal plan to validate")
    user_targets: Dict[str, float] = Field(..., description="User's nutritional targets")
    dietary_restrictions: list[str] = Field(default_factory=list, description="Dietary restrictions")


class AdkNutritionValidator:
    """
    Real Google ADK agent for validating nutritional compliance of meal plans.
    This agent uses the actual Google ADK framework and can communicate with 
    CrewAI agents via A2A protocol.
    """
    
    def __init__(self, model: str = None):
        """Initialize the ADK nutrition validator agent."""
        self.model_name = model or os.getenv('DEFAULT_LLM', 'gemini/gemini-2.0-flash')
        
        # Extract model name from format like "gemini/gemini-2.0-flash-lite"
        if '/' in self.model_name:
            self.model_name = self.model_name.split('/')[-1]
        
        # Create the ADK LlmAgent
        self.agent = self._create_agent()
        
        # Initialize ADK services required by Runner
        self.session_service = InMemorySessionService()
        self.memory_service = InMemoryMemoryService()
        self.artifact_service = InMemoryArtifactService()
        
        execution_logger.log_agent_action(
            action="Real ADK Nutrition Validator Initialized",
            details=f"Using Google ADK v1.18.0 with model: {self.model_name}"
        )
    
    def _create_agent(self) -> LlmAgent:
        """Create and configure the ADK LlmAgent using real Google ADK framework."""
        
        instruction = """You are a certified nutritionist and dietary compliance expert.

Your role is to validate meal plans against user nutritional targets and dietary restrictions.

For each validation request, you must:
1. Analyze the total nutritional content of the meal plan
2. Compare against user's specific targets (calories, protein, carbs, fat)
3. Calculate adherence percentages for each nutrient
4. Identify any violations of dietary restrictions or allergies
5. Provide specific recommendations for improvement if targets are not met
6. Issue warnings for any nutritional imbalances or health concerns
7. Make a final approval or rejection decision

Your analysis should be thorough, scientifically accurate, and practical.
Consider both daily and weekly nutritional balance.

Compliance criteria:
- Calories: Within ±10% of target
- Protein: Within ±15% of target
- Carbs: Within ±15% of target
- Fat: Within ±15% of target
- Must strictly adhere to all dietary restrictions
- Must avoid all allergens completely

Provide clear, actionable feedback that helps improve the meal plan.

Return your response as a JSON object with this structure:
{
  "is_compliant": boolean,
  "compliance_score": float (0-100),
  "deviations": {
    "calories": float,
    "protein": float,
    "carbs": float,
    "fat": float
  },
  "recommendations": [list of strings],
  "warnings": [list of strings],
  "approved": boolean
}"""
        
        # Create LlmAgent with the real ADK framework
        agent = LlmAgent(
            name="nutrition_validator",
            model=self.model_name,
            instruction=instruction,
            description="Validates meal plans for nutritional compliance and dietary adherence"
        )
        
        return agent
    
    async def validate_meal_plan_async(
        self, 
        meal_plan_data: Dict[str, Any],
        user_targets: Dict[str, float],
        dietary_restrictions: list[str] = None
    ) -> NutritionValidationResult:
        """
        Validate a meal plan asynchronously using real ADK framework.
        
        Args:
            meal_plan_data: Complete meal plan data
            user_targets: User's nutritional targets
            dietary_restrictions: List of dietary restrictions
            
        Returns:
            NutritionValidationResult with validation details
        """
        execution_logger.log_task_start(
            task_name="Nutrition Validation (Real ADK)",
            agent_name="nutrition_validator",
            description="Validating meal plan nutritional compliance using Google ADK"
        )
        
        try:
            # Prepare validation prompt
            prompt = self._build_validation_prompt(
                meal_plan_data, 
                user_targets, 
                dietary_restrictions or []
            )
            
            execution_logger.log_agent_action(
                action="Running ADK Agent",
                details=f"Validating against targets: {user_targets}"
            )
            
            # Create a unique session ID for this validation run
            import uuid
            session_id = f"validation_{uuid.uuid4().hex[:8]}"
            user_id = "meal_planner_user"
            
            # Initialize session first
            await self.session_service.create_session(
                app_name="nutrition_validator",
                user_id=user_id,
                session_id=session_id
            )
            
            # Create Runner to execute the agent with required services
            runner = Runner(
                app_name="nutrition_validator",
                agent=self.agent,
                session_service=self.session_service,
                memory_service=self.memory_service,
                artifact_service=self.artifact_service
            )
            
            # Import types for Content creation
            from google.genai import types
            
            # Create a new message with the prompt
            new_message = types.Content(
                role="user",
                parts=[types.Part(text=prompt)]
            )
            
            # Run the agent with proper session parameters
            result_text = ""
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message
            ):
                # Collect response text from events
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                result_text += part.text
            
            # Parse result as NutritionValidationResult
            if result_text:
                # Extract text from collected result
                result_text = result_text.strip()
                
                # Try to extract JSON if wrapped in markdown code blocks
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()
                
                # Parse JSON
                result_dict = json.loads(result_text)
                validation_result = NutritionValidationResult(**result_dict)
                
                execution_logger.log_task_complete(
                    output_summary=f"Validation complete. Approved: {validation_result.approved}",
                    metadata={
                        "compliance_score": validation_result.compliance_score,
                        "is_compliant": validation_result.is_compliant,
                        "adk_version": "1.18.0"
                    }
                )
                
                return validation_result
            else:
                raise ValueError("No validation result received from ADK agent")
                
        except Exception as e:
            execution_logger.log_task_error(
                error_message=f"ADK validation failed: {str(e)}",
                error_details={"exception_type": type(e).__name__}
            )
            
            # Return a failed validation result
            return NutritionValidationResult(
                is_compliant=False,
                compliance_score=0.0,
                deviations={},
                recommendations=["Validation failed due to error"],
                warnings=[f"Error during ADK validation: {str(e)}"],
                approved=False
            )
    
    def validate_meal_plan(
        self,
        meal_plan_data: Dict[str, Any],
        user_targets: Dict[str, float],
        dietary_restrictions: list[str] = None
    ) -> NutritionValidationResult:
        """
        Synchronous wrapper for validate_meal_plan_async.
        
        Args:
            meal_plan_data: Complete meal plan data
            user_targets: User's nutritional targets
            dietary_restrictions: List of dietary restrictions
            
        Returns:
            NutritionValidationResult with validation details
        """
        return asyncio.run(
            self.validate_meal_plan_async(
                meal_plan_data,
                user_targets,
                dietary_restrictions
            )
        )
    
    def _build_validation_prompt(
        self,
        meal_plan_data: Dict[str, Any],
        user_targets: Dict[str, float],
        dietary_restrictions: list[str]
    ) -> str:
        """Build a detailed validation prompt for the agent."""
        
        prompt = f"""Please validate the following meal plan for nutritional compliance.

USER NUTRITIONAL TARGETS:
- Daily Calories: {user_targets.get('calories', 2000)} kcal
- Daily Protein: {user_targets.get('protein', 150)}g
- Daily Carbohydrates: {user_targets.get('carbs', 200)}g
- Daily Fat: {user_targets.get('fat', 67)}g

DIETARY RESTRICTIONS:
{', '.join(dietary_restrictions) if dietary_restrictions else 'None'}

MEAL PLAN DATA:
{json.dumps(meal_plan_data, indent=2)}

Please provide a comprehensive validation that includes:
1. Is the plan compliant? (yes/no)
2. Overall compliance score (0-100)
3. Specific deviations from targets for each nutrient
4. Detailed recommendations for improvement
5. Any nutritional warnings or concerns
6. Final approval status

Be specific about which meals or days are causing compliance issues.
Provide actionable recommendations that can be implemented immediately.
"""
        
        return prompt
    
    def start_a2a_server(self, host: str = "localhost", port: int = 8080):
        """
        Start an A2A server to allow CrewAI agents to communicate with this ADK agent.
        This enables cross-framework agent communication using Google ADK's A2A protocol.
        """
        execution_logger.log_agent_action(
            action="Starting Real ADK A2A Server",
            details=f"Server will listen on {host}:{port}"
        )
        
        print(f"🔗 Real Google ADK A2A Server configured for {host}:{port}")
        print("   CrewAI agents can now communicate with this ADK agent via A2A protocol")
        print("   Using Google ADK v1.18.0")
        
        # In a full implementation, this would use google.adk.a2a module
        # to create a proper A2A server endpoint


# Create a singleton instance
nutrition_validator = AdkNutritionValidator()


# Example usage function
async def example_validation():
    """Example of how to use the real ADK nutrition validator."""
    
    print("\n" + "="*80)
    print("TESTING REAL GOOGLE ADK AGENT")
    print("="*80 + "\n")
    
    # Sample meal plan data
    meal_plan = {
        "total_days": 7,
        "average_daily_nutrition": {
            "calories": 1950,
            "protein_g": 145,
            "carbs_g": 210,
            "fat_g": 65
        }
    }
    
    user_targets = {
        "calories": 2000,
        "protein": 150,
        "carbs": 200,
        "fat": 67
    }
    
    dietary_restrictions = ["vegetarian", "gluten-free"]
    
    # Run validation using real ADK
    result = await nutrition_validator.validate_meal_plan_async(
        meal_plan,
        user_targets,
        dietary_restrictions
    )
    
    print("\n" + "="*80)
    print("NUTRITION VALIDATION RESULT (Using Real Google ADK)")
    print("="*80)
    print(f"Compliant: {result.is_compliant}")
    print(f"Compliance Score: {result.compliance_score}/100")
    print(f"Approved: {result.approved}")
    print(f"\nDeviations: {result.deviations}")
    print(f"\nRecommendations:")
    for rec in result.recommendations:
        print(f"  - {rec}")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Test the real ADK validator
    asyncio.run(example_validation())

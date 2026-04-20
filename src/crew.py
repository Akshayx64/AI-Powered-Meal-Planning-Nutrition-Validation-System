"""
CrewAI-based Diet & Meal Planning Crew.
Implements the main meal planning workflow using CrewAI framework.
"""

import os
import sys
import time
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai.a2a import A2AConfig

# Import custom tools
from tools.mcp_tools import recipe_search_tool
from tools.nutrition_tool import nutrition_tool
from tools.mcp_nutrition_tools import get_mcp_nutrition_server

# Import callbacks
from src.callbacks import execution_logger, create_task_callback

# Import Pydantic models for structured outputs
from src.models import (
    PantryAnalysis,
    Recipe,
    MealPlan,
    ShoppingList,
    NutritionValidationResult
)


@CrewBase
class DietMealPlannerCrew:
    """
    Diet & Meal Planning Crew using CrewAI.
    
    This crew consists of 4 specialized agents that work together to create
    personalized meal plans:
    1. Pantry Analyzer - Analyzes available ingredients
    2. Recipe Creator - Generates personalized recipes
    3. Meal Plan Coordinator - Organizes weekly meal schedule
    4. Shopping List Generator - Creates categorized shopping list
    """
    
    agents_config = '../config/agents.yaml'
    tasks_config = '../config/tasks.yaml'
    
    def __init__(self):
        """Initialize the crew with default configuration."""
        self.llm_model = os.getenv('DEFAULT_LLM', 'gpt-4o')
        # Generate timestamp for unique output files
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @before_kickoff
    def before_kickoff_function(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute before the crew starts working.
        Validates inputs and sets up logging.
        """
        print("\n" + "="*80)
        print("🍽️  DIET & MEAL PLANNING CREW - STARTING UP")
        print("="*80 + "\n")
        
        # Log initialization
        execution_logger.log_task_start(
            task_name="Crew Initialization",
            agent_name="System",
            description="Validating inputs and preparing for meal planning"
        )
        
        # Validate required inputs
        required_keys = [
            'dietary_restrictions', 'allergies', 'health_goals',
            'calorie_target', 'protein_target', 'carb_target', 'fat_target',
            'pantry_items', 'meal_count'
        ]
        
        for key in required_keys:
            if key not in inputs:
                raise ValueError(f"Missing required input: {key}")
        
        # Ensure meal_count is reasonable
        if not isinstance(inputs['meal_count'], int) or inputs['meal_count'] < 1 or inputs['meal_count'] > 14:
            inputs['meal_count'] = 7  # Default to 1 week
        
        # Log input summary
        execution_logger.log_task_step(
            step_name="Input Validation Complete",
            details=f"Planning {inputs['meal_count']} days of meals",
            data={
                "calorie_target": inputs['calorie_target'],
                "dietary_restrictions": inputs.get('dietary_restrictions', []),
                "pantry_items_count": len(inputs.get('pantry_items', []))
            }
        )
        
        execution_logger.log_task_complete(
            output_summary="Crew initialization successful, ready to start meal planning"
        )
        
        return inputs
    
    @after_kickoff
    def after_kickoff_function(self, result) -> Any:
        """
        Execute after the crew completes all tasks.
        Performs final validation and logging.
        """
        execution_logger.log_task_start(
            task_name="Crew Finalization",
            agent_name="System",
            description="Finalizing outputs and generating summary"
        )
        
        # Print execution summary
        execution_logger.print_execution_summary()
        
        # Log completion
        print("\n" + "="*80)
        print("✅ DIET & MEAL PLANNING CREW - COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nOutputs generated:")
        print("  📄 output/meal_plan.md - Complete weekly meal plan")
        print("  🛒 output/shopping_list.md - Categorized shopping list")
        print("  📊 logs/agent_execution.log - Detailed execution log")
        print("  📈 logs/task_execution.json - Structured task data")
        print("\n" + "="*80 + "\n")
        
        execution_logger.log_task_complete(
            output_summary="All meal planning tasks completed successfully"
        )
        
        return result
    
    @agent
    def pantry_analyzer(self) -> Agent:
        """Create the Pantry Analyzer agent."""
        execution_logger.log_agent_action(
            action="Creating Pantry Analyzer Agent",
            details="Specialized in ingredient analysis and optimization"
        )
        
        return Agent(
            config=self.agents_config['pantry_analyzer'],
            llm=self.llm_model,
            verbose=True,
            max_iter=10,  # Limit iterations to reduce API calls
            max_retry_limit=2,  # Reduce retries
        )
    
    @agent
    def recipe_creator(self) -> Agent:
        """Create the Recipe Creator agent with MCP nutrition server via stdio transport."""
        execution_logger.log_agent_action(
            action="Creating Recipe Creator Agent",
            details="Equipped with MCP USDA nutrition server (stdio transport)"
        )
        
        # Get MCP nutrition server instance
        try:
            mcp_server = get_mcp_nutrition_server()
            execution_logger.log_agent_action(
                action="MCP Server Initialized",
                details="USDA Nutrition MCP server connected via stdio"
            )
        except Exception as e:
            execution_logger.log_error(
                error_type="MCP Initialization Failed",
                error_message=str(e),
                traceback_info=""
            )
            mcp_server = None
        
        # Build tools list
        tools = [recipe_search_tool, nutrition_tool]  # Fallback tools
        
        return Agent(
            config=self.agents_config['recipe_creator'],
            llm=self.llm_model,
            tools=tools,  # Recipe search + USDA nutrition fallback
            mcp=[mcp_server] if mcp_server else [],  # MCP server via stdio
            verbose=True,
            max_iter=10,
            max_retry_limit=2,
        )
    
    @agent
    def meal_plan_coordinator(self) -> Agent:
        """Create the Meal Plan Coordinator agent."""
        execution_logger.log_agent_action(
            action="Creating Meal Plan Coordinator Agent",
            details="Specialized in weekly meal organization and nutritional balance"
        )
        
        return Agent(
            config=self.agents_config['meal_plan_coordinator'],
            llm=self.llm_model,
            verbose=True,
            max_iter=15,  # Allow more iterations for complex planning
            max_retry_limit=2,
        )
    
    @agent
    def shopping_list_generator(self) -> Agent:
        """Create the Shopping List Generator agent."""
        execution_logger.log_agent_action(
            action="Creating Shopping List Generator Agent",
            details="Specialized in shopping optimization and categorization"
        )
        
        return Agent(
            config=self.agents_config['shopping_list_generator'],
            llm=self.llm_model,
            verbose=True,
            max_iter=10,
            max_retry_limit=2,
        )
    
    @agent
    def nutritionist_advisor(self) -> Agent:
        """Create the Nutritionist Advisor agent with MCP nutrition server and A2A delegation."""
        execution_logger.log_agent_action(
            action="Creating Nutritionist Advisor Agent",
            details="Clinical nutritionist with MCP USDA nutrition + A2A delegation"
        )
        
        # Get MCP nutrition server instance
        try:
            mcp_server = get_mcp_nutrition_server()
        except Exception as e:
            execution_logger.log_error(
                error_type="MCP Initialization Failed",
                error_message=str(e),
                traceback_info=""
            )
            mcp_server = None
        
        # Get A2A server details from environment
        a2a_host = os.getenv('ADK_AGENT_HOST', 'localhost')
        a2a_port = os.getenv('ADK_AGENT_PORT', '8080')
        a2a_endpoint = f"http://{a2a_host}:{a2a_port}/.well-known/agent-card.json"
        
        return Agent(
            config=self.agents_config['nutritionist_advisor'],
            llm=self.llm_model,
            tools=[nutrition_tool],  # USDA nutrition tool with fallback
            mcp=[mcp_server] if mcp_server else [],  # MCP server via stdio
            verbose=True,
            max_iter=10,
            max_retry_limit=2,
            # A2A temporarily disabled to reduce API calls
            # a2a=A2AConfig(
            #     endpoint=a2a_endpoint,
            #     timeout=120,
            #     max_turns=5,
            #     fail_fast=False
            # )
        )
    
    @agent
    def meal_prep_coach(self) -> Agent:
        """Create the Meal Prep Coach agent."""
        execution_logger.log_agent_action(
            action="Creating Meal Prep Coach Agent",
            details="Meal prep specialist providing batch cooking strategies"
        )
        
        return Agent(
            config=self.agents_config['meal_prep_coach'],
            llm=self.llm_model,
            verbose=True,
            max_iter=10,
            max_retry_limit=2,
        )
    
    @task
    def pantry_analysis_task(self) -> Task:
        """Create the pantry analysis task with structured output."""
        time.sleep(2)  # 2 second delay before task to prevent rate limiting
        return Task(
            config=self.tasks_config['pantry_analysis_task'],
            callback=create_task_callback("Pantry Analysis"),
            output_pydantic=PantryAnalysis
        )
    
    @task
    def recipe_generation_task(self) -> Task:
        """Create the recipe generation task with structured output."""
        time.sleep(3)  # 3 second delay to prevent rate limiting
        from pydantic import BaseModel
        from typing import List
        
        # Define a wrapper model for the list of recipes
        class RecipeList(BaseModel):
            recipes: List[Recipe]
        
        return Task(
            config=self.tasks_config['recipe_generation_task'],
            context=[self.pantry_analysis_task()],  # Uses pantry analysis results
            callback=create_task_callback("Recipe Generation"),
            output_pydantic=RecipeList
        )
    
    @task
    def recipe_validation_task(self) -> Task:
        """Create the recipe validation task."""
        time.sleep(3)  # 3 second delay to prevent rate limiting
        return Task(
            config=self.tasks_config['recipe_validation_task'],
            context=[self.recipe_generation_task()],  # Uses generated recipes
            callback=create_task_callback("Recipe Validation")
        )
    
    @task
    def meal_plan_organization_task(self) -> Task:
        """Create the meal plan organization task with validation loop support and structured output."""
        time.sleep(5)  # 5 second delay for complex task
        task_config = self.tasks_config['meal_plan_organization_task'].copy()
        # Add timestamp to output filename - but only save if validation passes
        task_config['output_file'] = f"output/meal_plan_{self.timestamp}.md"
        
        # Add validation loop context to task description
        if 'description' in task_config:
            task_config['description'] += "\n\nIMPORTANT: If ADK validation fails, you may need to regenerate the meal plan with adjustments."
        
        return Task(
            config=task_config,
            context=[self.recipe_validation_task()],  # Uses validated recipes
            callback=create_task_callback("Meal Plan Organization"),
            async_execution=False,  # Ensure synchronous execution for validation
            output_pydantic=MealPlan
        )
    
    @task
    def shopping_list_task(self) -> Task:
        """Create the shopping list generation task with structured output."""
        time.sleep(3)  # 3 second delay to prevent rate limiting
        task_config = self.tasks_config['shopping_list_task'].copy()
        # Add timestamp to output filename
        task_config['output_file'] = f"output/shopping_list_{self.timestamp}.md"
        return Task(
            config=task_config,
            context=[self.meal_plan_organization_task()],  # Uses meal plan
            callback=create_task_callback("Shopping List Generation"),
            output_pydantic=ShoppingList
        )
    
    @task
    def nutritional_analysis_task(self) -> Task:
        """Create the nutritional analysis task with structured output."""
        time.sleep(4)  # 4 second delay to prevent rate limiting
        return Task(
            config=self.tasks_config['nutritional_analysis_task'],
            context=[self.meal_plan_organization_task(), self.shopping_list_task()],  # Uses meal plan + shopping list
            callback=create_task_callback("Nutritional Analysis"),
            output_pydantic=NutritionValidationResult
        )
    
    @task
    def meal_prep_strategy_task(self) -> Task:
        """Create the meal prep strategy task."""
        time.sleep(3)  # 3 second delay to prevent rate limiting
        task_config = self.tasks_config['meal_prep_strategy_task'].copy()
        # Add timestamp to output filename
        task_config['output_file'] = f"output/meal_prep_guide_{self.timestamp}.md"
        return Task(
            config=task_config,
            context=[self.meal_plan_organization_task(), self.shopping_list_task()],  # Uses meal plan + shopping list
            callback=create_task_callback("Meal Prep Strategy")
        )
    
    @crew
    def crew(self) -> Crew:
        """
        Create the Diet & Meal Planning Crew.
        
        The crew executes tasks sequentially with 6 agents and 7 tasks:
        1. Pantry Analysis
        2. Recipe Generation (uses pantry analysis + MCP tools)
        3. Recipe Validation (validates recipe variety and count)
        4. Meal Plan Organization (uses validated recipes)
        5. Shopping List Generation (uses meal plan)
        6. Nutritional Analysis (validates meal plan)
        7. Meal Prep Strategy (provides prep guidance)
        """
        return Crew(
            agents=self.agents,  # Automatically created by @agent decorators (6 agents)
            tasks=self.tasks,    # Automatically created by @task decorators (7 tasks)
            process=Process.sequential,
            verbose=True,
            memory=False,  # Disable memory - no persistence between executions
            max_rpm=5,  # Aggressive rate limit: 5 requests per minute to avoid 429 errors
            share_crew=True,  # Enable crew sharing - agents share context within execution
            step_callback=None,  # Disable step callbacks to reduce API calls
            task_callback=None,  # Disable task callbacks to reduce API calls
        )


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = load_default_inputs()
    try:
        DietMealPlannerCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        DietMealPlannerCrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = load_default_inputs()
    try:
        DietMealPlannerCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def load_default_inputs() -> Dict[str, Any]:
    """Load default inputs from profile."""
    import json
    from pathlib import Path
    
    profile_path = Path(__file__).parent.parent / "profiles" / "default.json"
    if profile_path.exists():
        with open(profile_path, 'r') as f:
            profile = json.load(f)
        
        return {
            "dietary_restrictions": profile.get("dietary_restrictions", ""),
            "allergies": profile.get("allergies", ""),
            "health_goals": profile.get("health_goals", ""),
            "calorie_target": profile.get("calorie_target"),
            "protein_target": profile.get("protein_target_g"),
            "carb_target": profile.get("carbs_target_g"),
            "fat_target": profile.get("fat_target_g"),
            "pantry_items": profile.get("pantry_items", []),
            "meal_count": profile.get("meal_plan_days", 7)
        }
    
    # Default fallback - basic profile
    return {
        "dietary_restrictions": "none",
        "allergies": "none",
        "health_goals": "general health",
        "calorie_target": profile.get("calorie_target", 2000),
        "protein_target": profile.get("protein_target_g", 100),
        "carb_target": profile.get("carbs_target_g", 200),
        "fat_target": profile.get("fat_target_g", 70),
        "pantry_items": profile.get("pantry_items", []),
        "meal_count": 7
    }


# For direct import
def create_meal_planning_crew() -> DietMealPlannerCrew:
    """Factory function to create a new crew instance."""
    return DietMealPlannerCrew()

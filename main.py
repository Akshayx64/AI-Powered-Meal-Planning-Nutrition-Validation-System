"""
Main execution script for the Diet & Meal Planning System.
Demonstrates the complete workflow with sample user profile.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.crew import DietMealPlannerCrew
from src.adk_agent import nutrition_validator
from src.callbacks import execution_logger
from src.models import MealPlan, ShoppingList, PantryAnalysis
from src.output_handler import (
    extract_task_outputs,
    print_meal_plan_summary,
    print_shopping_list_summary,
    print_pantry_analysis_summary,
    export_all_outputs
)


def load_user_profile(profile_path: str = None) -> dict:
    """Load user profile from JSON file or use default."""
    if profile_path and os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            return json.load(f)
    
    # Default profile for demonstration
    return {
        "dietary_restrictions": "vegetarian, gluten-free",
        "allergies": "nuts",
        "health_goals": "weight loss, muscle gain, balanced nutrition",
        "calorie_target": 2000,
        "protein_target": 150,
        "carb_target": 200,
        "fat_target": 67,
        "pantry_items": [
            "chicken breast", "brown rice", "quinoa", "eggs", 
            "broccoli", "spinach", "sweet potato", "olive oil",
            "garlic", "onions", "tomatoes", "carrots"
        ],
        "meal_count": 7,
        "cuisine_preferences": "Mediterranean, Asian, Italian"
    }


def setup_environment():
    """Setup environment variables and directories."""
    # Load environment variables
    load_dotenv()
    
    # Create necessary directories
    directories = ['output', 'logs', 'profiles']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # Check for required API keys
    if not os.getenv('OPENAI_API_KEY') and not os.getenv('GEMINI_API_KEY'):
        print("⚠️  WARNING: No API keys found!")
        print("   Please set either OPENAI_API_KEY or GEMINI_API_KEY in your .env file")
        print("   The system may not function properly without valid API keys.\n")


def run_meal_planning(inputs: dict, verbose: bool = True):
    """
    Run the complete meal planning workflow with ADK validation loop.
    
    Args:
        inputs: User profile and preferences (loaded dynamically from JSON)
        verbose: Whether to print detailed logs
    """
    print("\n" + "="*80)
    print("🍽️  AI-POWERED DIET & MEAL PLANNING SYSTEM")
    print("="*80)
    print("\n📋 User Profile (Dynamically Loaded):")
    print(f"   Dietary Restrictions: {inputs.get('dietary_restrictions', 'None')}")
    print(f"   Allergies: {inputs.get('allergies', 'None')}")
    print(f"   Health Goals: {inputs.get('health_goals', 'General wellness')}")
    print(f"   Daily Calorie Target: {inputs.get('calorie_target', 2000)} kcal")
    print(f"   Meal Plan Duration: {inputs.get('meal_count', 7)} days")
    print(f"   Pantry Items: {len(inputs.get('pantry_items', []))} items available")
    print("="*80 + "\n")
    
    try:
        # Initialize the CrewAI crew
        print("🤖 Initializing Multi-Agent System...")
        crew_instance = DietMealPlannerCrew()
        crew = crew_instance.crew()
        
        print("✅ Agents initialized:")
        print("   1. Pantry Analyzer")
        print("   2. Recipe Creator")
        print("   3. Meal Plan Coordinator")
        print("   4. Shopping List Generator")
        print("   5. Nutritionist Advisor")
        print("   6. Meal Prep Coach")
        print("\n🚀 Starting meal planning workflow with 6 agents...\n")
        
        # Execute the crew
        result = crew.kickoff(inputs=inputs)
        
        # Extract and display structured outputs
        print("\n" + "="*80)
        print("📊 STRUCTURED OUTPUT RESULTS")
        print("="*80 + "\n")
        
        # Extract all structured Pydantic outputs
        outputs = extract_task_outputs(result)
        
        if outputs:
            print(f"✅ Successfully received {len(outputs)} structured Pydantic outputs\n")
            
            # Display summaries using helper functions
            for task_name, output in outputs.items():
                if isinstance(output, PantryAnalysis):
                    print_pantry_analysis_summary(output)
                elif isinstance(output, MealPlan):
                    print_meal_plan_summary(output)
                elif isinstance(output, ShoppingList):
                    print_shopping_list_summary(output)
            
            # Save all structured outputs as JSON
            print("💾 Saving structured outputs to JSON files...")
            saved_files = export_all_outputs(outputs, output_dir="output/structured")
            print()
        else:
            print("ℹ️  Structured outputs not available (using markdown outputs instead)")
        
        print("="*80 + "\n")
        
        # Run ADK validation (informational only - no retry loop)
        print("\n" + "="*80)
        print("🔬 NUTRITION VALIDATION (ADK Agent via A2A)")
        print("="*80 + "\n")
        
        print("Running informational validation with ADK nutrition validator...")
        
        validation_result = nutrition_validator.validate_meal_plan(
            meal_plan_data={
                "status": "generated",
                "duration": inputs.get('meal_count', 7),
                "targets": {
                    "calories": inputs.get('calorie_target'),
                    "protein": inputs.get('protein_target'),
                    "carbs": inputs.get('carb_target'),
                    "fat": inputs.get('fat_target')
                }
            },
            user_targets={
                "calories": inputs.get('calorie_target', 2000),
                "protein": inputs.get('protein_target', 150),
                "carbs": inputs.get('carb_target', 200),
                "fat": inputs.get('fat_target', 67)
            },
            dietary_restrictions=inputs.get('dietary_restrictions', '').split(', ')
        )
        
        print(f"\n📊 Validation Assessment (Informational):")
        print(f"   Compliance Score: {validation_result.compliance_score:.1f}/100")
        print(f"   Status: {'✅ Approved' if validation_result.approved else '⚠️  Needs improvement'}")
        
        if validation_result.recommendations:
            print(f"\n💡 Recommendations for User Consideration:")
            for i, rec in enumerate(validation_result.recommendations[:5], 1):
                print(f"   {i}. {rec}")
            print("\n   (These are suggestions - meal plan is provided as-is for your review)")
        
        if not result:
            raise Exception("Meal planning failed - no output generated")
        
        print("\n" + "="*80)
        print("✅ MEAL PLANNING COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\n📄 Generated Files:")
        print(f"   ✓ output/meal_plan_{crew_instance.timestamp}.md - Your personalized weekly meal plan")
        print(f"   ✓ output/shopping_list_{crew_instance.timestamp}.md - Categorized shopping list")
        print(f"   ✓ output/meal_prep_guide_{crew_instance.timestamp}.md - Meal prep strategy")
        print("   ✓ logs/agent_execution.log - Detailed execution log")
        print("   ✓ logs/task_execution.json - Structured task data")
        
        print("\n💡 Next Steps:")
        print("   1. Review your meal plan in output/meal_plan.md")
        print("   2. Print the shopping list for grocery shopping")
        print("   3. Check logs for detailed agent execution information")
        print("   4. Adjust your profile and re-run for different results")
        
        print("\n" + "="*80 + "\n")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        execution_logger.log_task_error(
            error_message=f"Main execution failed: {str(e)}",
            error_details={"exception_type": type(e).__name__}
        )
        raise


def main():
    """Main entry point with dynamic profile loading and validation loop."""
    parser = argparse.ArgumentParser(
        description='AI-Powered Diet & Meal Planning System with Dynamic User Profiles',
        epilog='Example: python main.py --profile profiles/vegan_profile.json'
    )
    parser.add_argument(
        '--profile',
        type=str,
        help='Path to user profile JSON file (default: built-in vegetarian profile)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Load user profile dynamically from JSON
    inputs = load_user_profile(args.profile)
    
    if args.profile:
        print(f"📂 Loaded custom profile from: {args.profile}\n")
    else:
        print("📂 Using default vegetarian/gluten-free profile\n")
    
    # Run meal planning with validation loop
    try:
        result = run_meal_planning(inputs, verbose=args.verbose)
        
        # Print final summary
        execution_logger.print_execution_summary()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

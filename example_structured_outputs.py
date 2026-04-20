"""
Example script demonstrating usage of structured Pydantic outputs from CrewAI tasks.

This script shows how to:
1. Run the meal planning crew
2. Access structured Pydantic outputs from tasks
3. Save outputs to JSON files
4. Load and manipulate structured data
5. Use the data programmatically
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.crew import DietMealPlannerCrew
from src.output_handler import (
    extract_task_outputs,
    save_structured_output,
    print_meal_plan_summary,
    print_shopping_list_summary,
    print_pantry_analysis_summary,
    export_all_outputs
)
from src.models import MealPlan, ShoppingList, PantryAnalysis


def example_basic_usage():
    """Example 1: Basic usage - run crew and get structured outputs."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Usage with Structured Outputs")
    print("="*80 + "\n")
    
    # Setup inputs
    inputs = {
        "dietary_restrictions": "vegetarian",
        "allergies": "none",
        "health_goals": "weight loss, balanced nutrition",
        "calorie_target": 1800,
        "protein_target": 120,
        "carb_target": 180,
        "fat_target": 60,
        "pantry_items": ["quinoa", "black beans", "spinach", "olive oil", "tomatoes"],
        "meal_count": 3,  # Short test
        "cuisine_preferences": "Mediterranean"
    }
    
    # Initialize and run crew
    print("🚀 Running meal planning crew...")
    crew_instance = DietMealPlannerCrew()
    crew = crew_instance.crew()
    result = crew.kickoff(inputs=inputs)
    
    # Extract structured outputs
    print("\n📊 Extracting structured outputs...")
    outputs = extract_task_outputs(result)
    
    print(f"✅ Received {len(outputs)} structured outputs:")
    for task_name, output in outputs.items():
        print(f"   • {task_name}: {type(output).__name__}")
    
    return outputs


def example_save_and_load():
    """Example 2: Save structured outputs to JSON and load them back."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Save and Load Structured Outputs")
    print("="*80 + "\n")
    
    # Run basic example to get outputs
    outputs = example_basic_usage()
    
    # Save all outputs to JSON
    print("\n💾 Saving outputs to JSON files...")
    saved_files = export_all_outputs(outputs, output_dir="output/structured")
    
    print(f"\n✅ Saved {len(saved_files)} files:")
    for name, path in saved_files.items():
        print(f"   • {name}: {path}")


def example_programmatic_access():
    """Example 3: Access and manipulate structured data programmatically."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Programmatic Access to Structured Data")
    print("="*80 + "\n")
    
    # Get outputs
    outputs = example_basic_usage()
    
    # Example: Access meal plan data
    for task_name, output in outputs.items():
        if isinstance(output, MealPlan):
            print("\n📅 Meal Plan Analysis:")
            print(f"   Duration: {output.total_days} days")
            print(f"   Total meals: {len(output.meals)}")
            
            # Calculate statistics
            total_calories = output.total_nutrition.calories
            avg_calories = output.average_daily_nutrition.calories
            print(f"   Total calories: {total_calories:.0f} kcal")
            print(f"   Average daily: {avg_calories:.0f} kcal")
            
            # Check adherence
            print(f"\n   Goal Adherence:")
            for nutrient, percentage in output.adherence_to_goals.items():
                status = "✅" if 90 <= percentage <= 110 else "⚠️"
                print(f"      {status} {nutrient}: {percentage:.1f}%")
            
            # List all recipes
            print(f"\n   Recipes used:")
            unique_recipes = set()
            for meal in output.meals:
                unique_recipes.add(meal.recipe.name)
            for recipe in sorted(unique_recipes):
                print(f"      • {recipe}")
        
        elif isinstance(output, ShoppingList):
            print("\n🛒 Shopping List Analysis:")
            print(f"   Total items: {output.total_items}")
            if output.estimated_total_cost:
                print(f"   Estimated cost: ${output.estimated_total_cost:.2f}")
            
            # Group by category
            print(f"\n   Items by category:")
            for category, items in output.categories.items():
                print(f"      • {category}: {len(items)} items")
            
            # Find high-priority items
            high_priority = []
            for category, items in output.categories.items():
                for item in items:
                    if item.priority == "high":
                        high_priority.append(item.name)
            
            if high_priority:
                print(f"\n   High-priority items:")
                for item in high_priority:
                    print(f"      ⭐ {item}")
        
        elif isinstance(output, PantryAnalysis):
            print("\n🏪 Pantry Analysis:")
            print(f"   Available items: {len(output.available_items)}")
            print(f"   Coverage: {output.coverage_percentage:.1f}%")
            
            if output.recipe_suggestions:
                print(f"\n   Top recipe suggestions:")
                for suggestion in output.recipe_suggestions[:3]:
                    print(f"      • {suggestion}")


def example_custom_filtering():
    """Example 4: Filter and query structured data."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Custom Filtering and Queries")
    print("="*80 + "\n")
    
    outputs = example_basic_usage()
    
    for task_name, output in outputs.items():
        if isinstance(output, MealPlan):
            print("\n🔍 Filtering meal plan data:\n")
            
            # Find high-protein meals
            print("High-protein meals (>40g protein):")
            for meal in output.meals:
                if meal.recipe.nutrition.protein_g > 40:
                    print(f"   • {meal.recipe.name}: {meal.recipe.nutrition.protein_g}g protein")
            
            # Find breakfast meals
            print("\nBreakfast recipes:")
            for meal in output.meals:
                if meal.meal_type.value == "breakfast":
                    print(f"   • Day {meal.day}: {meal.recipe.name}")
            
            # Find quick recipes (<30 min total time)
            print("\nQuick recipes (< 30 minutes):")
            for meal in output.meals:
                total_time = meal.recipe.prep_time_minutes + meal.recipe.cook_time_minutes
                if total_time < 30:
                    print(f"   • {meal.recipe.name}: {total_time} min")


def example_export_to_api_format():
    """Example 5: Export structured data in API-friendly format."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Export for API Response")
    print("="*80 + "\n")
    
    outputs = example_basic_usage()
    
    # Convert to dictionaries (suitable for JSON API responses)
    api_data = {}
    for task_name, output in outputs.items():
        api_data[task_name] = output.model_dump(exclude_none=True)
    
    print("✅ Converted to API-friendly format:")
    print(f"   Total outputs: {len(api_data)}")
    for name in api_data.keys():
        print(f"   • {name}")
    
    # Example: Create a summary endpoint response
    summary = {
        "status": "success",
        "timestamp": "2025-11-19T12:00:00Z",
        "data": api_data,
        "metadata": {
            "total_outputs": len(api_data),
            "output_types": [type(output).__name__ for output in outputs.values()]
        }
    }
    
    print("\n📦 Example API response structure:")
    print(f"   Status: {summary['status']}")
    print(f"   Outputs: {summary['metadata']['total_outputs']}")
    print(f"   Types: {', '.join(summary['metadata']['output_types'])}")


def example_pretty_printing():
    """Example 6: Use helper functions for pretty printing."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Pretty Printing with Helper Functions")
    print("="*80 + "\n")
    
    outputs = example_basic_usage()
    
    # Use the helper functions from output_handler
    for task_name, output in outputs.items():
        if isinstance(output, MealPlan):
            print_meal_plan_summary(output)
        elif isinstance(output, ShoppingList):
            print_shopping_list_summary(output)
        elif isinstance(output, PantryAnalysis):
            print_pantry_analysis_summary(output)


def main():
    """Run all examples."""
    examples = [
        ("Basic Usage", example_basic_usage),
        ("Save and Load", example_save_and_load),
        ("Programmatic Access", example_programmatic_access),
        ("Custom Filtering", example_custom_filtering),
        ("API Export", example_export_to_api_format),
        ("Pretty Printing", example_pretty_printing)
    ]
    
    print("\n" + "="*80)
    print("🎯 STRUCTURED OUTPUT EXAMPLES")
    print("="*80)
    print("\nThis script demonstrates various ways to use structured Pydantic outputs")
    print("from CrewAI tasks in the Diet & Meal Planning system.\n")
    
    # Run a specific example or all
    if len(sys.argv) > 1:
        example_num = int(sys.argv[1]) - 1
        if 0 <= example_num < len(examples):
            name, func = examples[example_num]
            print(f"\nRunning Example {example_num + 1}: {name}\n")
            func()
        else:
            print(f"❌ Invalid example number. Choose 1-{len(examples)}")
    else:
        print("Available examples:")
        for i, (name, _) in enumerate(examples, 1):
            print(f"   {i}. {name}")
        print("\nUsage: python example_structured_outputs.py [example_number]")
        print("       or run without arguments to see this menu\n")


if __name__ == "__main__":
    main()

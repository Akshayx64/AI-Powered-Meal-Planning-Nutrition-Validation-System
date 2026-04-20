"""
Helper functions for handling structured Pydantic outputs from CrewAI tasks.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

from src.models import (
    MealPlan,
    ShoppingList,
    PantryAnalysis,
    Recipe,
    NutritionValidationResult
)


def save_structured_output(output: Any, output_dir: str = "output", filename_prefix: str = None) -> str:
    """
    Save structured Pydantic output to JSON file.
    
    Args:
        output: Pydantic model instance
        output_dir: Directory to save outputs
        filename_prefix: Optional prefix for filename
    
    Returns:
        Path to saved file
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Determine filename based on output type
    if isinstance(output, MealPlan):
        filename = f"meal_plan_{timestamp}.json"
    elif isinstance(output, ShoppingList):
        filename = f"shopping_list_{timestamp}.json"
    elif isinstance(output, PantryAnalysis):
        filename = f"pantry_analysis_{timestamp}.json"
    elif isinstance(output, NutritionValidationResult):
        filename = f"nutrition_validation_{timestamp}.json"
    else:
        filename = f"output_{timestamp}.json"
    
    if filename_prefix:
        filename = f"{filename_prefix}_{filename}"
    
    filepath = Path(output_dir) / filename
    
    # Convert Pydantic model to dict and save as JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output.model_dump(), f, indent=2, ensure_ascii=False)
    
    return str(filepath)


def load_structured_output(filepath: str, model_class: type) -> Any:
    """
    Load structured output from JSON file and convert to Pydantic model.
    
    Args:
        filepath: Path to JSON file
        model_class: Pydantic model class to instantiate
    
    Returns:
        Pydantic model instance
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return model_class(**data)


def extract_task_outputs(crew_result) -> Dict[str, Any]:
    """
    Extract all structured outputs from CrewAI crew execution result.
    
    Args:
        crew_result: Result from crew.kickoff()
    
    Returns:
        Dictionary mapping task names to their Pydantic outputs
    """
    outputs = {}
    
    if not hasattr(crew_result, 'tasks_output'):
        return outputs
    
    for task_output in crew_result.tasks_output:
        task_name = task_output.name if hasattr(task_output, 'name') else 'unknown'
        
        # Check if task has Pydantic output
        if hasattr(task_output, 'pydantic') and task_output.pydantic is not None:
            outputs[task_name] = task_output.pydantic
    
    return outputs


def print_meal_plan_summary(meal_plan: MealPlan) -> None:
    """Print a formatted summary of a meal plan."""
    print("\n" + "="*80)
    print("📅 MEAL PLAN SUMMARY")
    print("="*80)
    print(f"\n📆 Duration: {meal_plan.total_days} days ({meal_plan.week_start_date})")
    print(f"🍽️  Total Meals: {len(meal_plan.meals)}")
    
    print(f"\n📊 Daily Average Nutrition:")
    avg = meal_plan.average_daily_nutrition
    print(f"   Calories: {avg.calories:.0f} kcal")
    print(f"   Protein:  {avg.protein_g:.1f}g")
    print(f"   Carbs:    {avg.carbs_g:.1f}g")
    print(f"   Fat:      {avg.fat_g:.1f}g")
    if avg.fiber_g:
        print(f"   Fiber:    {avg.fiber_g:.1f}g")
    
    print(f"\n🎯 Goal Adherence:")
    for nutrient, percentage in meal_plan.adherence_to_goals.items():
        status = "✅" if 90 <= percentage <= 110 else "⚠️"
        print(f"   {status} {nutrient.capitalize()}: {percentage:.1f}%")
    
    print(f"\n📋 Meals by Day:")
    current_day = None
    for meal in meal_plan.meals:
        if meal.day != current_day:
            current_day = meal.day
            print(f"\n   Day {meal.day} ({meal.day_name}):")
        print(f"      • {meal.meal_type.value.title()}: {meal.recipe.name}")
    
    print("\n" + "="*80 + "\n")


def print_shopping_list_summary(shopping_list: ShoppingList) -> None:
    """Print a formatted summary of a shopping list."""
    print("\n" + "="*80)
    print("🛒 SHOPPING LIST SUMMARY")
    print("="*80)
    print(f"\n📝 Total Items: {shopping_list.total_items}")
    if shopping_list.estimated_total_cost:
        print(f"💰 Estimated Cost: ${shopping_list.estimated_total_cost:.2f}")
    
    print(f"\n📦 Categories: {len(shopping_list.categories)}")
    for category, items in shopping_list.categories.items():
        category_total = sum(item.estimated_price or 0 for item in items)
        print(f"\n   {category} ({len(items)} items)")
        if category_total > 0:
            print(f"      Subtotal: ${category_total:.2f}")
        for item in items[:3]:  # Show first 3 items
            price_str = f" - ${item.estimated_price:.2f}" if item.estimated_price else ""
            priority = "⭐" if item.priority == "high" else ""
            print(f"      {priority} {item.name}: {item.quantity} {item.unit}{price_str}")
        if len(items) > 3:
            print(f"      ... and {len(items) - 3} more items")
    
    if shopping_list.notes:
        print(f"\n💡 Shopping Notes:")
        for note in shopping_list.notes:
            print(f"   • {note}")
    
    print("\n" + "="*80 + "\n")


def print_pantry_analysis_summary(pantry: PantryAnalysis) -> None:
    """Print a formatted summary of pantry analysis."""
    print("\n" + "="*80)
    print("🏪 PANTRY ANALYSIS SUMMARY")
    print("="*80)
    print(f"\n📦 Available Items: {len(pantry.available_items)}")
    print(f"📊 Coverage: {pantry.coverage_percentage:.1f}% of meal plan ingredients")
    
    if pantry.expiring_soon:
        print(f"\n⚠️  Items Expiring Soon: {len(pantry.expiring_soon)}")
        for item in pantry.expiring_soon[:5]:
            print(f"   • {item.get('name', 'Unknown')}")
    
    if pantry.recipe_suggestions:
        print(f"\n💡 Recipe Suggestions ({len(pantry.recipe_suggestions)}):")
        for recipe in pantry.recipe_suggestions[:5]:
            print(f"   • {recipe}")
    
    print("\n" + "="*80 + "\n")


def print_nutrition_validation_summary(validation: NutritionValidationResult) -> None:
    """Print a formatted summary of nutrition validation."""
    print("\n" + "="*80)
    print("🔬 NUTRITION VALIDATION SUMMARY")
    print("="*80)
    
    status = "✅ APPROVED" if validation.approved else "⚠️  NEEDS IMPROVEMENT"
    print(f"\n{status}")
    print(f"📊 Compliance Score: {validation.compliance_score:.1f}/100")
    print(f"✓ Is Compliant: {validation.is_compliant}")
    
    if validation.deviations:
        print(f"\n📈 Nutrient Deviations:")
        for nutrient, deviation in validation.deviations.items():
            sign = "+" if deviation > 0 else ""
            print(f"   • {nutrient.capitalize()}: {sign}{deviation:.1f}")
    
    if validation.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in validation.recommendations:
            print(f"   • {rec}")
    
    if validation.warnings:
        print(f"\n⚠️  Warnings:")
        for warning in validation.warnings:
            print(f"   • {warning}")
    
    print("\n" + "="*80 + "\n")


def export_all_outputs(outputs: Dict[str, Any], output_dir: str = "output") -> Dict[str, str]:
    """
    Export all structured outputs to JSON files.
    
    Args:
        outputs: Dictionary of task outputs
        output_dir: Directory to save files
    
    Returns:
        Dictionary mapping output types to file paths
    """
    saved_files = {}
    
    for task_name, output in outputs.items():
        try:
            filepath = save_structured_output(output, output_dir, task_name)
            saved_files[task_name] = filepath
            print(f"✅ Saved {task_name}: {filepath}")
        except Exception as e:
            print(f"❌ Failed to save {task_name}: {e}")
    
    return saved_files


def convert_to_dict_for_api(pydantic_model: Any) -> Dict[str, Any]:
    """
    Convert Pydantic model to dictionary suitable for API responses.
    
    Args:
        pydantic_model: Any Pydantic model instance
    
    Returns:
        Dictionary representation
    """
    return pydantic_model.model_dump(exclude_none=True)


def validate_meal_plan_structure(meal_plan: MealPlan) -> List[str]:
    """
    Validate meal plan structure and return list of issues.
    
    Args:
        meal_plan: MealPlan instance to validate
    
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    
    if meal_plan.total_days < 1:
        issues.append("Meal plan must have at least 1 day")
    
    if len(meal_plan.meals) == 0:
        issues.append("Meal plan must contain at least one meal")
    
    if meal_plan.total_days * 3 > len(meal_plan.meals) * 2:
        issues.append(f"Not enough meals for {meal_plan.total_days} days")
    
    # Check for reasonable nutrition values
    avg = meal_plan.average_daily_nutrition
    if avg.calories < 800 or avg.calories > 5000:
        issues.append(f"Average daily calories ({avg.calories}) outside reasonable range")
    
    if avg.protein_g < 20 or avg.protein_g > 400:
        issues.append(f"Average daily protein ({avg.protein_g}g) outside reasonable range")
    
    return issues

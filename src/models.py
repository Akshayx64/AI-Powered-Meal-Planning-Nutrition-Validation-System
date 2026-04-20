"""
Pydantic models for structured data across the meal planning system.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class MealType(str, Enum):
    """Types of meals in the daily schedule."""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class NutritionInfo(BaseModel):
    """Nutritional information for a recipe or meal."""
    calories: float = Field(..., description="Total calories")
    protein_g: float = Field(..., description="Protein in grams")
    carbs_g: float = Field(..., description="Carbohydrates in grams")
    fat_g: float = Field(..., description="Fat in grams")
    fiber_g: Optional[float] = Field(None, description="Fiber in grams")
    sodium_mg: Optional[float] = Field(None, description="Sodium in milligrams")
    sugar_g: Optional[float] = Field(None, description="Sugar in grams")


class Ingredient(BaseModel):
    """A single ingredient with quantity."""
    name: str = Field(..., description="Ingredient name")
    quantity: float = Field(..., description="Quantity amount")
    unit: str = Field(..., description="Unit of measurement (g, ml, cup, tbsp, etc.)")
    category: Optional[str] = Field(None, description="Food category (protein, vegetable, grain, etc.)")
    in_pantry: bool = Field(False, description="Whether ingredient is already in pantry")


class Recipe(BaseModel):
    """A complete recipe with instructions and nutrition."""
    name: str = Field(..., description="Recipe name")
    description: str = Field(..., description="Brief description of the dish")
    meal_type: MealType = Field(..., description="Type of meal")
    servings: int = Field(..., description="Number of servings")
    prep_time_minutes: int = Field(..., description="Preparation time")
    cook_time_minutes: int = Field(..., description="Cooking time")
    difficulty: str = Field(..., description="Difficulty level (easy, medium, hard)")
    ingredients: List[Ingredient] = Field(..., description="List of ingredients")
    instructions: List[str] = Field(..., description="Step-by-step cooking instructions")
    nutrition: NutritionInfo = Field(..., description="Nutritional information per serving")
    tags: List[str] = Field(default_factory=list, description="Tags (vegetarian, gluten-free, etc.)")
    cuisine_type: Optional[str] = Field(None, description="Cuisine type (Italian, Asian, etc.)")


class Meal(BaseModel):
    """A meal in the weekly plan."""
    day: int = Field(..., description="Day number (1-7)", ge=1, le=7)
    day_name: str = Field(..., description="Day of the week")
    meal_type: MealType = Field(..., description="Type of meal")
    recipe: Recipe = Field(..., description="Recipe for this meal")


class GoalAdherence(BaseModel):
    """Adherence to nutritional goals."""
    calories_percent: float = Field(..., description="Percentage adherence to calorie goals")
    protein_percent: float = Field(..., description="Percentage adherence to protein goals")
    carbs_percent: float = Field(..., description="Percentage adherence to carb goals")
    fat_percent: float = Field(..., description="Percentage adherence to fat goals")


class MealPlan(BaseModel):
    """Complete weekly meal plan."""
    week_start_date: str = Field(..., description="Starting date of the meal plan")
    total_days: int = Field(..., description="Number of days in the plan")
    meals: List[Meal] = Field(..., description="List of all meals")
    total_nutrition: NutritionInfo = Field(..., description="Total weekly nutrition")
    average_daily_nutrition: NutritionInfo = Field(..., description="Average daily nutrition")
    adherence_to_goals: GoalAdherence = Field(
        ..., 
        description="Percentage adherence to nutritional goals"
    )


class ShoppingItem(BaseModel):
    """A single item on the shopping list."""
    name: str = Field(..., description="Item name")
    quantity: float = Field(..., description="Total quantity needed")
    unit: str = Field(..., description="Unit of measurement")
    category: str = Field(..., description="Store category (produce, meat, dairy, etc.)")
    estimated_price: Optional[float] = Field(None, description="Estimated price in local currency")
    priority: str = Field(default="normal", description="Priority level (high, normal, low)")


class ShoppingCategory(BaseModel):
    """A category of shopping items."""
    category_name: str = Field(..., description="Category name (produce, meat, dairy, etc.)")
    items: List[ShoppingItem] = Field(..., description="Items in this category")


class ShoppingList(BaseModel):
    """Categorized shopping list."""
    categories: List[ShoppingCategory] = Field(
        ..., 
        description="Items organized by category"
    )
    total_items: int = Field(..., description="Total number of items")
    estimated_total_cost: Optional[float] = Field(None, description="Estimated total cost")
    notes: List[str] = Field(default_factory=list, description="Additional shopping notes")


class ExpiringItem(BaseModel):
    """Item that is expiring soon."""
    name: str = Field(..., description="Item name")
    days_until_expiry: int = Field(..., description="Days until expiration")


class PantryAnalysis(BaseModel):
    """Analysis of available pantry items."""
    available_items: List[Ingredient] = Field(..., description="Items currently in pantry")
    expiring_soon: List[ExpiringItem] = Field(
        default_factory=list,
        description="Items that should be used soon"
    )
    recipe_suggestions: List[str] = Field(
        default_factory=list,
        description="Suggested recipes based on available ingredients"
    )
    coverage_percentage: float = Field(
        ..., 
        description="Percentage of meal plan ingredients already in pantry"
    )


class UserProfile(BaseModel):
    """User dietary profile and preferences."""
    dietary_restrictions: List[str] = Field(
        default_factory=list,
        description="Dietary restrictions (vegetarian, vegan, keto, etc.)"
    )
    allergies: List[str] = Field(
        default_factory=list,
        description="Food allergies"
    )
    health_goals: List[str] = Field(
        default_factory=list,
        description="Health goals (weight loss, muscle gain, etc.)"
    )
    calorie_target: int = Field(..., description="Daily calorie target")
    protein_target: float = Field(..., description="Daily protein target in grams")
    carb_target: float = Field(..., description="Daily carb target in grams")
    fat_target: float = Field(..., description="Daily fat target in grams")
    pantry_items: List[str] = Field(default_factory=list, description="Available pantry items")
    meal_count: int = Field(7, description="Number of days to plan for")
    cuisine_preferences: List[str] = Field(
        default_factory=list,
        description="Preferred cuisines"
    )
    avoid_ingredients: List[str] = Field(
        default_factory=list,
        description="Ingredients to avoid"
    )
    cooking_skill: str = Field("intermediate", description="Cooking skill level")


class NutritionDeviations(BaseModel):
    """Deviations from nutritional targets."""
    calories: float = Field(0.0, description="Calorie deviation from target")
    protein: float = Field(0.0, description="Protein deviation from target (g)")
    carbs: float = Field(0.0, description="Carbs deviation from target (g)")
    fat: float = Field(0.0, description="Fat deviation from target (g)")


class NutritionValidationResult(BaseModel):
    """Result from ADK nutrition validation agent."""
    is_compliant: bool = Field(..., description="Whether meal plan meets nutritional goals")
    compliance_score: float = Field(..., description="Overall compliance score (0-100)")
    deviations: NutritionDeviations = Field(
        default_factory=NutritionDeviations,
        description="Deviations from nutritional targets"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations for improvement"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Nutritional warnings"
    )
    approved: bool = Field(..., description="Whether plan is approved for use")


class TaskExecutionLog(BaseModel):
    """Log entry for task execution monitoring."""
    task_name: str = Field(..., description="Name of the task")
    agent_name: str = Field(..., description="Agent executing the task")
    start_time: str = Field(..., description="Task start timestamp")
    end_time: Optional[str] = Field(None, description="Task end timestamp")
    status: str = Field(..., description="Status (running, completed, failed)")
    output_summary: Optional[str] = Field(None, description="Summary of task output")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class AgentState(BaseModel):
    """Shared state between agents."""
    user_profile: UserProfile = Field(..., description="User dietary profile")
    pantry_analysis: Optional[PantryAnalysis] = Field(None, description="Pantry analysis result")
    recipes: List[Recipe] = Field(default_factory=list, description="Generated recipes")
    meal_plan: Optional[MealPlan] = Field(None, description="Complete meal plan")
    shopping_list: Optional[ShoppingList] = Field(None, description="Shopping list")
    nutrition_validation: Optional[NutritionValidationResult] = Field(
        None, 
        description="Nutrition validation result"
    )
    execution_logs: List[TaskExecutionLog] = Field(
        default_factory=list,
        description="Task execution logs"
    )

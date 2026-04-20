"""
MCP-based Nutrition Tool for fetching nutritional data from USDA FoodData Central.
"""

from crewai.tools import BaseTool
from typing import Type, Dict, Any, Optional
from pydantic import BaseModel, Field
import os
import requests
class NutritionToolInput(BaseModel):
    """Input schema for Nutrition Tool."""
    ingredient_name: str = Field(..., description="Name of the ingredient to look up")
    quantity: float = Field(..., description="Quantity of the ingredient")
    unit: str = Field(..., description="Unit of measurement (g, ml, cup, tbsp, etc.)")


class NutritionTool(BaseTool):
    """
    Tool for fetching nutritional information about ingredients.
    This tool connects to a nutrition API via MCP.
    """
    
    name: str = "nutrition_lookup"
    description: str = (
        "Looks up detailed nutritional information for a given ingredient. "
        "Returns calories, macronutrients (protein, carbs, fat), and micronutrients. "
        "Useful for calculating recipe nutrition and verifying dietary compliance."
    )
    args_schema: Type[BaseModel] = NutritionToolInput

    def _run(
        self,
        ingredient_name: str,
        quantity: float,
        unit: str
    ) -> Dict[str, Any]:
        """
        Fetch nutritional information for an ingredient from USDA MCP server.
        
        Falls back to mock data if API fails.
        """
        # Try to fetch from USDA MCP server first
        api_result = self._fetch_from_usda_mcp(ingredient_name)
        
        if api_result and "error" not in api_result:
            # Use API data
            base_nutrition = api_result
        else:
            # Fall back to mock data
            nutrition_db = self._get_mock_nutrition_data()
            
            # Normalize ingredient name
            ingredient_key = ingredient_name.lower().strip()
            
            if ingredient_key not in nutrition_db:
                return {
                    "ingredient": ingredient_name,
                    "error": f"Nutritional information not found for '{ingredient_name}'",
                    "suggestion": "Try using a more common name or check spelling"
                }
            
            base_nutrition = nutrition_db[ingredient_key]
        
        # Convert quantity to grams for standardization
        quantity_in_grams = self._convert_to_grams(quantity, unit)
        
        # Scale nutrition data based on quantity
        scaled_nutrition = {
            "ingredient": ingredient_name,
            "quantity": quantity,
            "unit": unit,
            "nutrition": {
                "calories": round((base_nutrition["calories"] / 100) * quantity_in_grams, 1),
                "protein_g": round((base_nutrition["protein_g"] / 100) * quantity_in_grams, 1),
                "carbs_g": round((base_nutrition["carbs_g"] / 100) * quantity_in_grams, 1),
                "fat_g": round((base_nutrition["fat_g"] / 100) * quantity_in_grams, 1),
                "fiber_g": round((base_nutrition.get("fiber_g", 0) / 100) * quantity_in_grams, 1),
                "sodium_mg": round((base_nutrition.get("sodium_mg", 0) / 100) * quantity_in_grams, 1),
                "sugar_g": round((base_nutrition.get("sugar_g", 0) / 100) * quantity_in_grams, 1),
            },
            "category": base_nutrition.get("category", "other"),
            "source": base_nutrition.get("source", "USDA FoodData Central" if api_result else "mock_database"),
            "food_description": base_nutrition.get("food_description", ingredient_name)
        }
        
        return scaled_nutrition
    
    def _convert_to_grams(self, quantity: float, unit: str) -> float:
        """Convert various units to grams for standardization."""
        conversions = {
            "g": 1.0,
            "gram": 1.0,
            "grams": 1.0,
            "kg": 1000.0,
            "kilogram": 1000.0,
            "ml": 1.0,  # Approximate for water-based liquids
            "l": 1000.0,
            "cup": 240.0,
            "tbsp": 15.0,
            "tablespoon": 15.0,
            "tsp": 5.0,
            "teaspoon": 5.0,
            "oz": 28.35,
            "ounce": 28.35,
            "lb": 453.59,
            "pound": 453.59,
        }
        
        unit_lower = unit.lower().strip()
        multiplier = conversions.get(unit_lower, 100.0)  # Default to 100g if unknown
        
        return quantity * multiplier
    
    def _fetch_from_usda_mcp(self, ingredient_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch nutrition data from USDA FoodData Central API.
        API Documentation: https://fdc.nal.usda.gov/api-guide.html
        """
        api_key = os.getenv('USDA_API_KEY') or os.getenv('FDC_API_KEY')
        
        if not api_key:
            return None
        
        try:
            # USDA FoodData Central search endpoint
            search_url = 'https://api.nal.usda.gov/fdc/v1/foods/search'
            search_params = {
                'api_key': api_key,
                'query': ingredient_name,
                'pageSize': 1,
                'dataType': ['Survey (FNDDS)', 'Foundation', 'SR Legacy']
            }
            
            response = requests.get(search_url, params=search_params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('foods') and len(data['foods']) > 0:
                    food = data['foods'][0]
                    
                    # Extract nutrition data from foodNutrients
                    nutrients = {}
                    for nutrient in food.get('foodNutrients', []):
                        nutrient_name = nutrient.get('nutrientName', '').lower()
                        nutrient_value = nutrient.get('value', 0)
                        
                        # Map USDA nutrient names to our format
                        if 'energy' in nutrient_name:
                            nutrients['calories'] = nutrient_value
                        elif 'protein' in nutrient_name:
                            nutrients['protein_g'] = nutrient_value
                        elif 'carbohydrate' in nutrient_name:
                            nutrients['carbs_g'] = nutrient_value
                        elif 'total lipid' in nutrient_name or 'fat, total' in nutrient_name:
                            nutrients['fat_g'] = nutrient_value
                        elif 'fiber' in nutrient_name:
                            nutrients['fiber_g'] = nutrient_value
                        elif 'sodium' in nutrient_name:
                            nutrients['sodium_mg'] = nutrient_value
                        elif 'sugars, total' in nutrient_name:
                            nutrients['sugar_g'] = nutrient_value
                    
                    # Return standardized format (per 100g)
                    return {
                        "calories": nutrients.get('calories', 0),
                        "protein_g": nutrients.get('protein_g', 0),
                        "carbs_g": nutrients.get('carbs_g', 0),
                        "fat_g": nutrients.get('fat_g', 0),
                        "fiber_g": nutrients.get('fiber_g', 0),
                        "sodium_mg": nutrients.get('sodium_mg', 0),
                        "sugar_g": nutrients.get('sugar_g', 0),
                        "category": self._categorize_ingredient(nutrients),
                        "source": "USDA FoodData Central",
                        "food_description": food.get('description', ingredient_name)
                    }
            
            return None
            
        except Exception as e:
            print(f"USDA FoodData Central API error: {str(e)}")
            return None
    
    def _categorize_ingredient(self, nutrition_data: Dict[str, Any]) -> str:
        """Categorize ingredient based on macronutrient profile."""
        protein = nutrition_data.get('protein_g', 0)
        carbs = nutrition_data.get('carbohydrates_total_g', 0)
        fat = nutrition_data.get('fat_total_g', 0)
        
        # Simple categorization logic
        if protein > 10 and protein > carbs and protein > fat:
            return "protein"
        elif carbs > 15 and carbs > protein and carbs > fat:
            return "grain"
        elif fat > 10 and fat > protein and fat > carbs:
            return "fat"
        elif carbs < 10 and protein < 5:
            return "vegetable"
        else:
            return "other"
    
    def _get_mock_nutrition_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Mock nutrition database. In production, this would be replaced by
        MCP server calls to a real nutrition API.
        
        Values are per 100g/100ml of ingredient.
        """
        return {
            # Proteins
            "chicken breast": {
                "calories": 165,
                "protein_g": 31,
                "carbs_g": 0,
                "fat_g": 3.6,
                "fiber_g": 0,
                "sodium_mg": 74,
                "sugar_g": 0,
                "category": "protein"
            },
            "salmon": {
                "calories": 208,
                "protein_g": 20,
                "carbs_g": 0,
                "fat_g": 13,
                "fiber_g": 0,
                "sodium_mg": 59,
                "sugar_g": 0,
                "category": "protein"
            },
            "eggs": {
                "calories": 143,
                "protein_g": 13,
                "carbs_g": 1,
                "fat_g": 10,
                "fiber_g": 0,
                "sodium_mg": 142,
                "sugar_g": 1,
                "category": "protein"
            },
            "tofu": {
                "calories": 76,
                "protein_g": 8,
                "carbs_g": 1.9,
                "fat_g": 4.8,
                "fiber_g": 0.3,
                "sodium_mg": 7,
                "sugar_g": 0.6,
                "category": "protein"
            },
            
            # Carbs
            "brown rice": {
                "calories": 123,
                "protein_g": 2.6,
                "carbs_g": 25.6,
                "fat_g": 1,
                "fiber_g": 1.6,
                "sodium_mg": 1,
                "sugar_g": 0.4,
                "category": "grain"
            },
            "quinoa": {
                "calories": 120,
                "protein_g": 4.4,
                "carbs_g": 21.3,
                "fat_g": 1.9,
                "fiber_g": 2.8,
                "sodium_mg": 7,
                "sugar_g": 0.9,
                "category": "grain"
            },
            "sweet potato": {
                "calories": 86,
                "protein_g": 1.6,
                "carbs_g": 20.1,
                "fat_g": 0.1,
                "fiber_g": 3,
                "sodium_mg": 55,
                "sugar_g": 4.2,
                "category": "vegetable"
            },
            "pasta": {
                "calories": 131,
                "protein_g": 5,
                "carbs_g": 25,
                "fat_g": 1.1,
                "fiber_g": 1.8,
                "sodium_mg": 1,
                "sugar_g": 0.6,
                "category": "grain"
            },
            
            # Vegetables
            "broccoli": {
                "calories": 34,
                "protein_g": 2.8,
                "carbs_g": 7,
                "fat_g": 0.4,
                "fiber_g": 2.6,
                "sodium_mg": 33,
                "sugar_g": 1.7,
                "category": "vegetable"
            },
            "spinach": {
                "calories": 23,
                "protein_g": 2.9,
                "carbs_g": 3.6,
                "fat_g": 0.4,
                "fiber_g": 2.2,
                "sodium_mg": 79,
                "sugar_g": 0.4,
                "category": "vegetable"
            },
            "carrots": {
                "calories": 41,
                "protein_g": 0.9,
                "carbs_g": 9.6,
                "fat_g": 0.2,
                "fiber_g": 2.8,
                "sodium_mg": 69,
                "sugar_g": 4.7,
                "category": "vegetable"
            },
            "tomatoes": {
                "calories": 18,
                "protein_g": 0.9,
                "carbs_g": 3.9,
                "fat_g": 0.2,
                "fiber_g": 1.2,
                "sodium_mg": 5,
                "sugar_g": 2.6,
                "category": "vegetable"
            },
            
            # Fats
            "olive oil": {
                "calories": 884,
                "protein_g": 0,
                "carbs_g": 0,
                "fat_g": 100,
                "fiber_g": 0,
                "sodium_mg": 2,
                "sugar_g": 0,
                "category": "fat"
            },
            "avocado": {
                "calories": 160,
                "protein_g": 2,
                "carbs_g": 8.5,
                "fat_g": 14.7,
                "fiber_g": 6.7,
                "sodium_mg": 7,
                "sugar_g": 0.7,
                "category": "fat"
            },
            "almonds": {
                "calories": 579,
                "protein_g": 21.2,
                "carbs_g": 21.6,
                "fat_g": 49.9,
                "fiber_g": 12.5,
                "sodium_mg": 1,
                "sugar_g": 4.4,
                "category": "fat"
            },
            
            # Dairy
            "milk": {
                "calories": 42,
                "protein_g": 3.4,
                "carbs_g": 5,
                "fat_g": 1,
                "fiber_g": 0,
                "sodium_mg": 44,
                "sugar_g": 5,
                "category": "dairy"
            },
            "greek yogurt": {
                "calories": 59,
                "protein_g": 10,
                "carbs_g": 3.6,
                "fat_g": 0.4,
                "fiber_g": 0,
                "sodium_mg": 36,
                "sugar_g": 3.2,
                "category": "dairy"
            },
            "cheese": {
                "calories": 402,
                "protein_g": 25,
                "carbs_g": 1.3,
                "fat_g": 33,
                "fiber_g": 0,
                "sodium_mg": 621,
                "sugar_g": 0.5,
                "category": "dairy"
            },
        }


# Create a singleton instance for easy import
nutrition_tool = NutritionTool()

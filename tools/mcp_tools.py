"""
MCP Tool Wrappers for CrewAI agents.
Uses @tool decorator for proper CrewAI integration.
"""

from crewai.tools import tool
import httpx
import os


@tool("Nutrition Lookup Tool")
def nutrition_lookup_tool(food_name: str) -> str:
    """
    Look up comprehensive nutrition information for any food item.
    Provides calories, protein, carbohydrates, fats, vitamins, and minerals.
    Uses USDA FoodData Central API with 1.2M+ foods.
    
    Args:
        food_name: Name of the food item (e.g., 'chicken breast', 'banana', 'brown rice')
        
    Returns:
        Formatted nutrition information string
    """
    api_key = os.getenv('USDA_API_KEY') or os.getenv('FDC_API_KEY')
    if not api_key:
        return f"Using basic nutrition estimate for '{food_name}'"
    
    try:
        # USDA FoodData Central search endpoint
        search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        search_params = {
            "api_key": api_key,
            "query": food_name,
            "pageSize": 1,
            "dataType": ["Survey (FNDDS)", "Foundation", "SR Legacy"]
        }
        
        response = httpx.get(search_url, params=search_params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('foods'):
            return f"No nutrition data found for '{food_name}' in USDA database"
        
        # Get first result
        food = data['foods'][0]
        food_description = food.get('description', food_name)
        
        # Extract nutrients
        nutrients = {}
        for nutrient in food.get('foodNutrients', []):
            name = nutrient.get('nutrientName', '').lower()
            value = nutrient.get('value', 0)
            
            if 'energy' in name:
                nutrients['calories'] = value
            elif 'protein' in name:
                nutrients['protein'] = value
            elif 'carbohydrate' in name:
                nutrients['carbs'] = value
            elif 'total lipid' in name or 'fat, total' in name:
                nutrients['fat'] = value
            elif 'fiber' in name:
                nutrients['fiber'] = value
            elif 'sugars, total' in name:
                nutrients['sugar'] = value
            elif 'sodium' in name:
                nutrients['sodium'] = value
        
        # Format output
        result = [
            f"🥗 Nutrition Information for: {food_description}",
            f"Source: USDA FoodData Central",
            "",
            "Per 100g serving:",
            f"  • Calories: {nutrients.get('calories', 'N/A')} kcal",
            f"  • Protein: {nutrients.get('protein', 'N/A')}g",
            f"  • Carbohydrates: {nutrients.get('carbs', 'N/A')}g",
            f"  • Fat: {nutrients.get('fat', 'N/A')}g",
            f"  • Fiber: {nutrients.get('fiber', 'N/A')}g",
            f"  • Sugar: {nutrients.get('sugar', 'N/A')}g",
            f"  • Sodium: {nutrients.get('sodium', 'N/A')}mg",
        ]
        
        return "\n".join(result)
        
    except httpx.HTTPError as e:
        return f"Error fetching nutrition data: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@tool("Recipe Search Tool")
def recipe_search_tool(query: str, dietary_restrictions: str = "") -> str:
    """
    Provides recipe inspiration based on ingredients and dietary requirements.
    Returns ideas that LLM can use to generate creative, detailed recipes.
    
    Args:
        query: Recipe search query (e.g., 'chicken pasta', 'vegan dessert', 'tofu stir-fry')
        dietary_restrictions: Comma-separated restrictions (e.g., 'vegetarian,gluten-free')
        
    Returns:
        Formatted recipe inspiration and guidance
    """
    # Provide recipe guidance based on query and restrictions
    result = [
        f"🍳 Recipe Inspiration for: {query}",
        f"Dietary Requirements: {dietary_restrictions or 'None'}",
        "",
        "Create creative, varied recipes using these guidelines:",
        "",
        "1. Use the available pantry ingredients as the foundation",
        "2. Ensure recipes meet all dietary restrictions",
        "3. Vary cooking methods (grilled, baked, stir-fried, roasted, etc.)",
        "4. Include diverse cuisines (Mediterranean, Asian, Mexican, etc.)",
        "5. Balance proteins, vegetables, and healthy fats",
        "6. Make each recipe unique - no repetition",
        "",
        "Recipe Ideas:",
    ]
    
    # Add specific ideas based on query
    if 'chicken' in query.lower():
        result.extend([
            "• Grilled lemon herb chicken with roasted vegetables",
            "• Asian-style chicken stir-fry with ginger and garlic",
            "• Mediterranean chicken with olives and tomatoes"
        ])
    elif 'tofu' in query.lower() or 'vegan' in dietary_restrictions.lower():
        result.extend([
            "• Crispy baked tofu with Asian glaze",
            "• Tofu scramble with vegetables",
            "• Marinated tofu stir-fry"
        ])
    elif 'fish' in query.lower() or 'salmon' in query.lower():
        result.extend([
            "• Pan-seared salmon with herbs",
            "• Baked fish with lemon and capers",
            "• Grilled fish tacos"
        ])
    else:
        result.extend([
            "• Build recipes around available proteins",
            "• Combine complementary vegetables and grains",
            "• Use herbs and spices for variety"
        ])
    
    result.append("\nGenerate detailed, unique recipes with exact measurements and step-by-step instructions.")
    
    return "\n".join(result)

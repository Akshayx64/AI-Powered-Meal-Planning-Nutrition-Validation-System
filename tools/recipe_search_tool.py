"""
Recipe Search Tool using API Ninjas for recipe database integration.
"""

from crewai.tools import BaseTool
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
import os
import httpx


class RecipeSearchInput(BaseModel):
    """Input schema for Recipe Search Tool."""
    ingredients: List[str] = Field(..., description="List of ingredients to search with")
    dietary_restrictions: List[str] = Field(
        default_factory=list,
        description="Dietary restrictions (vegetarian, vegan, gluten-free, etc.)"
    )
    cuisine_type: str = Field(default="any", description="Preferred cuisine type")
    max_results: int = Field(5, description="Maximum number of results to return")


class RecipeSearchTool(BaseTool):
    """
    Tool for searching recipes based on available ingredients and dietary requirements.
    Connects to recipe databases via MCP.
    """
    
    name: str = "recipe_search"
    description: str = (
        "Searches for recipes based on available ingredients, dietary restrictions, "
        "and cuisine preferences. Returns recipe ideas with ingredient lists and "
        "basic preparation information. Useful for meal planning and recipe discovery."
    )
    args_schema: Type[BaseModel] = RecipeSearchInput

    def _run(
        self,
        ingredients: List[str],
        dietary_restrictions: List[str] = None,
        cuisine_type: str = "any",
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for recipes using web search (Serper API).
        Returns recipe ideas that can be used by LLM for generation.
        
        Falls back to mock data if API fails.
        """
        dietary_restrictions = dietary_restrictions or []
        
        # Try web search first
        web_recipes = self._fetch_from_web_search(", ".join(ingredients[:3]), dietary_restrictions, cuisine_type)
        
        if web_recipes:
            all_recipes = web_recipes + self._get_mock_recipe_database()
        else:
            # Get mock recipe database as fallback
            all_recipes = self._get_mock_recipe_database()
        
        # Filter recipes based on criteria
        filtered_recipes = []
        
        for recipe in all_recipes:
            # Check dietary restrictions
            if dietary_restrictions:
                recipe_tags = [tag.lower() for tag in recipe.get("tags", [])]
                if not all(restriction.lower() in recipe_tags for restriction in dietary_restrictions):
                    continue
            
            # Check cuisine type
            if cuisine_type != "any" and recipe.get("cuisine_type", "").lower() != cuisine_type.lower():
                continue
            
            # Calculate ingredient match percentage
            recipe_ingredients = [ing.lower() for ing in recipe.get("ingredients_list", [])]
            available_ingredients = [ing.lower() for ing in ingredients]
            
            matching_ingredients = sum(
                1 for avail_ing in available_ingredients
                if any(avail_ing in recipe_ing or recipe_ing in avail_ing for recipe_ing in recipe_ingredients)
            )
            
            total_ingredients = len(recipe_ingredients)
            match_percentage = (matching_ingredients / total_ingredients * 100) if total_ingredients > 0 else 0
            
            # Add match info to recipe
            recipe_copy = recipe.copy()
            recipe_copy["match_percentage"] = round(match_percentage, 1)
            recipe_copy["matching_ingredients"] = matching_ingredients
            recipe_copy["total_ingredients"] = total_ingredients
            
            filtered_recipes.append(recipe_copy)
        
        # Sort by match percentage
        filtered_recipes.sort(key=lambda x: x["match_percentage"], reverse=True)
        
        # Return top results
        return filtered_recipes[:max_results]
    
    def _fetch_from_web_search(self, query: str, dietary_restrictions: List[str], cuisine_type: str) -> List[Dict[str, Any]]:
        """
        Fetch recipe ideas from web search using Serper API.
        Returns recipe concepts that LLM can use to generate detailed recipes.
        API Documentation: https://serper.dev/
        """
        api_key = os.getenv('SERPER_API_KEY')
        
        if not api_key:
            return []
        
        try:
            # Build search query
            search_terms = [query]
            if dietary_restrictions:
                search_terms.extend(dietary_restrictions)
            if cuisine_type != "any":
                search_terms.append(cuisine_type)
            search_terms.append("recipe")
            
            search_query = " ".join(search_terms)
            
            # Call Serper API
            url = 'https://google.serper.dev/search'
            headers = {
                'X-API-KEY': api_key,
                'Content-Type': 'application/json'
            }
            payload = {
                'q': search_query,
                'num': 10
            }
            
            response = httpx.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract recipe ideas from search results
                recipes = []
                for result in data.get('organic', [])[:5]:
                    recipes.append({
                        "name": result.get('title', 'Recipe Idea'),
                        "cuisine_type": cuisine_type,
                        "tags": dietary_restrictions,
                        "ingredients_list": [],  # LLM will generate from context
                        "difficulty": "medium",
                        "prep_time_minutes": 20,
                        "cook_time_minutes": 30,
                        "servings": 4,
                        "description": result.get('snippet', 'Web search result'),
                        "instructions": result.get('snippet', 'Use this as inspiration'),
                        "source": "web_search",
                        "url": result.get('link', '')
                    })
                
                return recipes
            
            return []
            
        except Exception as e:
            print(f"Web search error: {str(e)}")
            return []
    
    def _get_mock_recipe_database(self) -> List[Dict[str, Any]]:
        """
        Mock recipe database. In production, this would connect to a real
        recipe API via MCP server.
        """
        return [
            {
                "name": "Grilled Lemon Herb Chicken with Quinoa",
                "cuisine_type": "Mediterranean",
                "tags": ["gluten-free", "high-protein", "healthy"],
                "ingredients_list": ["chicken breast", "lemon", "olive oil", "garlic", "quinoa", "herbs"],
                "difficulty": "easy",
                "prep_time_minutes": 15,
                "cook_time_minutes": 25,
                "servings": 4,
                "description": "Tender grilled chicken breast marinated in lemon and herbs, served with fluffy quinoa."
            },
            {
                "name": "Salmon Teriyaki Bowl",
                "cuisine_type": "Asian",
                "tags": ["gluten-free", "high-protein", "omega-3"],
                "ingredients_list": ["salmon", "brown rice", "broccoli", "soy sauce", "ginger", "sesame oil"],
                "difficulty": "medium",
                "prep_time_minutes": 10,
                "cook_time_minutes": 20,
                "servings": 2,
                "description": "Pan-seared salmon with homemade teriyaki glaze over brown rice and steamed broccoli."
            },
            {
                "name": "Vegetarian Buddha Bowl",
                "cuisine_type": "Asian",
                "tags": ["vegetarian", "vegan", "gluten-free", "high-fiber"],
                "ingredients_list": ["quinoa", "chickpeas", "sweet potato", "spinach", "avocado", "tahini"],
                "difficulty": "easy",
                "prep_time_minutes": 20,
                "cook_time_minutes": 30,
                "servings": 3,
                "description": "Colorful bowl with roasted vegetables, quinoa, and creamy tahini dressing."
            },
            {
                "name": "Mediterranean Pasta Primavera",
                "cuisine_type": "Italian",
                "tags": ["vegetarian", "quick", "light"],
                "ingredients_list": ["pasta", "tomatoes", "zucchini", "bell peppers", "olive oil", "garlic", "basil"],
                "difficulty": "easy",
                "prep_time_minutes": 10,
                "cook_time_minutes": 15,
                "servings": 4,
                "description": "Light pasta dish with fresh vegetables and aromatic herbs."
            },
            {
                "name": "Tofu Stir-Fry with Vegetables",
                "cuisine_type": "Asian",
                "tags": ["vegetarian", "vegan", "high-protein", "quick"],
                "ingredients_list": ["tofu", "broccoli", "carrots", "bell peppers", "soy sauce", "ginger", "brown rice"],
                "difficulty": "easy",
                "prep_time_minutes": 15,
                "cook_time_minutes": 10,
                "servings": 3,
                "description": "Quick and easy stir-fry with crispy tofu and colorful vegetables."
            },
            {
                "name": "Greek Egg Scramble",
                "cuisine_type": "Mediterranean",
                "tags": ["vegetarian", "gluten-free", "high-protein", "quick"],
                "ingredients_list": ["eggs", "spinach", "tomatoes", "feta cheese", "olive oil", "herbs"],
                "difficulty": "easy",
                "prep_time_minutes": 5,
                "cook_time_minutes": 10,
                "servings": 2,
                "description": "Fluffy scrambled eggs with spinach, tomatoes, and tangy feta cheese."
            },
            {
                "name": "Sweet Potato and Black Bean Bowl",
                "cuisine_type": "Mexican",
                "tags": ["vegetarian", "vegan", "gluten-free", "high-fiber"],
                "ingredients_list": ["sweet potato", "black beans", "corn", "avocado", "lime", "cilantro", "quinoa"],
                "difficulty": "easy",
                "prep_time_minutes": 15,
                "cook_time_minutes": 25,
                "servings": 4,
                "description": "Hearty bowl with roasted sweet potato, black beans, and creamy avocado."
            },
            {
                "name": "Chicken and Vegetable Soup",
                "cuisine_type": "American",
                "tags": ["gluten-free", "comfort-food", "high-protein"],
                "ingredients_list": ["chicken breast", "carrots", "celery", "onion", "garlic", "herbs", "chicken broth"],
                "difficulty": "easy",
                "prep_time_minutes": 15,
                "cook_time_minutes": 30,
                "servings": 6,
                "description": "Comforting homemade soup with tender chicken and fresh vegetables."
            },
            {
                "name": "Avocado Toast with Eggs",
                "cuisine_type": "American",
                "tags": ["vegetarian", "quick", "breakfast", "high-protein"],
                "ingredients_list": ["bread", "avocado", "eggs", "tomatoes", "lime", "salt", "pepper"],
                "difficulty": "easy",
                "prep_time_minutes": 5,
                "cook_time_minutes": 5,
                "servings": 2,
                "description": "Classic avocado toast topped with perfectly cooked eggs."
            },
            {
                "name": "Yogurt Parfait with Berries",
                "cuisine_type": "American",
                "tags": ["vegetarian", "gluten-free", "quick", "breakfast", "high-protein"],
                "ingredients_list": ["greek yogurt", "berries", "honey", "granola", "almonds"],
                "difficulty": "easy",
                "prep_time_minutes": 5,
                "cook_time_minutes": 0,
                "servings": 1,
                "description": "Layered parfait with creamy Greek yogurt, fresh berries, and crunchy granola."
            },
            {
                "name": "Baked Salmon with Roasted Vegetables",
                "cuisine_type": "Mediterranean",
                "tags": ["gluten-free", "high-protein", "omega-3", "healthy"],
                "ingredients_list": ["salmon", "broccoli", "carrots", "olive oil", "lemon", "herbs"],
                "difficulty": "easy",
                "prep_time_minutes": 10,
                "cook_time_minutes": 20,
                "servings": 2,
                "description": "Oven-baked salmon fillet with perfectly roasted vegetables."
            },
            {
                "name": "Chickpea Curry",
                "cuisine_type": "Indian",
                "tags": ["vegetarian", "vegan", "gluten-free", "high-fiber"],
                "ingredients_list": ["chickpeas", "tomatoes", "coconut milk", "onion", "garlic", "curry spices", "brown rice"],
                "difficulty": "medium",
                "prep_time_minutes": 15,
                "cook_time_minutes": 25,
                "servings": 4,
                "description": "Creamy and flavorful chickpea curry in coconut milk sauce."
            },
        ]


# Create a singleton instance for easy import
recipe_search_tool = RecipeSearchTool()

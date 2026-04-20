# AI-Powered Personal Diet & Meal Planning Crew

An intelligent multi-agent system that creates personalized meal plans based on your health profile, dietary restrictions, and available ingredients.

## 🎯 Project Overview

This project solves five critical problems:
1. **Decision Fatigue**: Automates daily meal planning decisions
2. **Health Goal Adherence**: Ensures meals align with nutritional targets
3. **Food Waste**: Minimizes waste by using pantry ingredients
4. **Cooking Monotony**: Generates creative, varied recipes
5. **Time Consumption**: Streamlines planning, searching, and shopping

## 🌟 Key Features

- **Deep Personalization**: Tailored to allergies, dietary needs, and preferences
- **Nutritional Precision**: Enforces specific macro and calorie targets
- **Pantry-Aware Planning**: Uses existing ingredients first
- **Creative Recipe Generation**: Novel recipes beyond static databases
- **Automated Shopping Lists**: Smart, categorized lists
- **Holistic Plan Review**: Final validation for coherence and balance

## 🏗️ Architecture

This project implements a hybrid multi-agent architecture using:

- **CrewAI**: Primary framework for meal planning workflow (4 agents)
- **ADK (Agent Development Kit)**: Nutrition verification agent with A2A communication
- **MCP (Model Context Protocol)**: External tool integrations
- **A2A Protocol**: Inter-framework agent communication

### Agent System

```
┌─────────────────────────────────────────────────────────┐
│              CrewAI Meal Planning Crew                  │
├─────────────────────────────────────────────────────────┤
│  1. Pantry Analyzer Agent                               │
│     └─> Analyzes available ingredients                  │
│                                                          │
│  2. Recipe Creator Agent                                 │
│     └─> Generates personalized recipes                  │
│                                                          │
│  3. Meal Plan Coordinator Agent                          │
│     └─> Organizes weekly meal schedule                  │
│                                                          │
│  4. Shopping List Generator Agent                        │
│     └─> Creates categorized shopping list               │
└─────────────────────────────────────────────────────────┘
                       ↓ (A2A Communication)
┌─────────────────────────────────────────────────────────┐
│          ADK Nutrition Verification Agent                │
├─────────────────────────────────────────────────────────┤
│  5. Nutrition Validator Agent (ADK)                      │
│     └─> Validates nutritional compliance                │
└─────────────────────────────────────────────────────────┘
```

## 📋 Requirements Met

### 1. Context Sharing ✅
- Intermediate outputs flow between agents via state management
- Pantry analysis → Recipe creation → Meal planning → Shopping list

### 2. Tool Integration using MCP ✅
- **Nutrition API Tool**: Fetches nutritional data via MCP
- **Recipe Search Tool**: Searches external recipe databases
- Custom tools for pantry management

### 3. Structured Output using Pydantic ✅
- **Type-Safe Outputs**: All tasks return validated Pydantic models
- `PantryAnalysis`: Structured pantry inventory with coverage percentage
- `Recipe`: Detailed recipe with nutrition info and instructions
- `MealPlan`: Complete weekly meal schedule with adherence tracking
- `ShoppingList`: Categorized shopping items with pricing
- `NutritionValidationResult`: Validation results with compliance scores
- **Dual Format**: JSON (structured data) + Markdown (human-readable)
- **Programmatic Access**: Easy data manipulation and API integration

### 4. Task Monitoring & Logging using Callbacks ✅
- Step-by-step task monitoring
- Execution flow tracking
- Error handling and transparency

### 5. Agent-to-Agent Communication using A2A ✅
- CrewAI agents communicate with ADK nutrition validator
- Cross-framework interoperability demonstrated

### 6. Primary Frameworks: CrewAI and ADK ✅
- CrewAI handles main meal planning workflow
- ADK provides specialized nutrition validation
- Both frameworks integrated seamlessly

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip or uv package manager

### Setup

```bash
# Clone the repository
cd diet-meal-planner

# Install dependencies using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the project root:

```env
# LLM API Keys
OPENAI_API_KEY=your_openai_api_key_here
# or
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: MCP Server Keys
NUTRITION_API_KEY=your_nutrition_api_key
RECIPE_API_KEY=your_recipe_api_key

# Optional: Agent Configuration
DEFAULT_LLM=gpt-4o  # or gemini/gemini-2.0-flash-exp
```

## 📖 Usage

### Basic Usage

```python
from crew import DietMealPlannerCrew

# Define user profile
inputs = {
    "dietary_restrictions": "vegetarian, gluten-free",
    "allergies": "nuts, shellfish",
    "health_goals": "weight loss, muscle gain",
    "calorie_target": 2000,
    "protein_target": 150,
    "carb_target": 200,
    "fat_target": 67,
    "pantry_items": ["chicken breast", "rice", "broccoli", "eggs", "olive oil"],
    "meal_count": 7,  # days
    "cuisine_preferences": "Italian, Asian"
}

# Create and run the crew
crew = DietMealPlannerCrew()
result = crew.crew().kickoff(inputs=inputs)

# Output includes:
# - Detailed meal plan (meal_plan.md)
# - Shopping list (shopping_list.md)
# - Nutritional analysis (nutrition_report.md)
```

### Running with CLI

```bash
# Run with default configuration
python main.py

# Run with custom profile
python main.py --profile profiles/keto.json

# Verbose mode for debugging
python main.py --verbose
```

## 📁 Project Structure

```
diet-meal-planner/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── main.py                        # Main execution script
│
├── config/                        # Configuration files
│   ├── agents.yaml               # CrewAI agent configurations
│   ├── tasks.yaml                # CrewAI task definitions
│   └── adk_agent_config.yaml     # ADK agent configuration
│
├── src/                          # Source code
│   ├── __init__.py
│   ├── crew.py                   # CrewAI crew definition
│   ├── adk_agent.py              # ADK nutrition validator
│   ├── models.py                 # Pydantic models
│   ├── callbacks.py              # Monitoring callbacks
│   └── state.py                  # Shared state management
│
├── tools/                        # MCP and custom tools
│   ├── __init__.py
│   ├── nutrition_tool.py         # Nutrition API via MCP
│   ├── recipe_search_tool.py     # Recipe search via MCP
│   └── pantry_tool.py            # Pantry management
│
├── mcp_servers/                  # MCP server implementations
│   ├── nutrition_server.py       # Nutrition API MCP server
│   └── recipe_server.py          # Recipe search MCP server
│
├── output/                       # Generated outputs
│   ├── meal_plan_*.md            # Human-readable meal plans
│   ├── shopping_list_*.md        # Shopping lists
│   ├── meal_prep_guide_*.md      # Meal prep strategies
│   └── structured/               # Structured JSON outputs
│       ├── meal_plan_*.json      # Pydantic MealPlan objects
│       ├── shopping_list_*.json  # Pydantic ShoppingList objects
│       └── pantry_analysis_*.json # Pydantic PantryAnalysis objects
│
├── logs/                         # Execution logs
│   └── agent_execution.log
│
└── tests/                        # Test files
    ├── test_agents.py
    ├── test_tools.py
    └── test_integration.py
```

## 🔧 Configuration

### User Profile

Edit `profiles/default.json` to customize your profile:

```json
{
  "dietary_restrictions": ["vegetarian"],
  "allergies": ["nuts", "dairy"],
  "health_goals": ["weight loss"],
  "calorie_target": 1800,
  "macros": {
    "protein": 120,
    "carbs": 180,
    "fat": 60
  },
  "pantry_items": [
    "chicken breast",
    "brown rice",
    "quinoa",
    "eggs"
  ],
  "preferences": {
    "cuisines": ["Mediterranean", "Asian"],
    "avoid_ingredients": ["mushrooms"],
    "cooking_skill": "intermediate"
  }
}
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Test structured output implementation
python test_structured_outputs.py

# Run system tests
python test_system.py

# Run with coverage
pytest --cov=src tests/
```

### Structured Output Examples

```bash
# See all structured output examples
python example_structured_outputs.py

# Run specific example
python example_structured_outputs.py 1  # Basic usage
python example_structured_outputs.py 3  # Programmatic access
python example_structured_outputs.py 6  # Pretty printing
```

## 📊 Working with Structured Outputs

The system returns validated Pydantic models for programmatic access:

```python
from src.crew import DietMealPlannerCrew
from src.output_handler import extract_task_outputs

# Run crew
crew = DietMealPlannerCrew()
result = crew.crew().kickoff(inputs=inputs)

# Extract structured outputs
outputs = extract_task_outputs(result)

# Access typed data
for name, output in outputs.items():
    if isinstance(output, MealPlan):
        print(f"Total days: {output.total_days}")
        print(f"Avg calories: {output.average_daily_nutrition.calories}")
        
        # Filter high-protein meals
        high_protein = [
            meal for meal in output.meals 
            if meal.recipe.nutrition.protein_g > 40
        ]
```

**See `STRUCTURED_OUTPUT_GUIDE.md` for complete documentation.**

## 📊 Monitoring & Logging

The system provides comprehensive monitoring through:

1. **Task Callbacks**: Track each task's execution
2. **Agent Logs**: Detailed agent decision logs
3. **Execution Flow**: Visual representation of workflow
4. **Error Tracking**: Comprehensive error handling

View logs in `logs/agent_execution.log`

## 🔐 Security Considerations

- Store API keys securely in `.env` (never commit)
- MCP servers validate all inputs
- Sanitize user-provided data
- Follow MCP security best practices

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- CrewAI Framework: https://github.com/joaomdmoura/crewAI
- Google ADK: https://github.com/google/genai-agent-dev-kit
- Model Context Protocol: https://modelcontextprotocol.io/

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check documentation in `docs/`
- Review examples in `examples/`

---

**Built with ❤️ for the Generative AI Agents Course**

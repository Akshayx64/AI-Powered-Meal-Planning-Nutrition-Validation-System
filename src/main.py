#!/usr/bin/env python
"""
Entry point for running the Diet & Meal Planning Crew.
This allows execution via: python -m src.main or crewai run
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crew import DietMealPlannerCrew, load_default_inputs


def main():
    """Main entry point for the crew execution."""
    print("\n" + "="*80)
    print("🍽️  DIET & MEAL PLANNING CREW")
    print("="*80 + "\n")
    
    # Load inputs
    inputs = load_default_inputs()
    
    # Create and run crew
    crew = DietMealPlannerCrew()
    result = crew.crew().kickoff(inputs=inputs)
    
    print("\n" + "="*80)
    print("✅ MEAL PLANNING COMPLETE!")
    print("="*80)
    print("\nCheck outputs in:")
    print("  - output/meal_plan.md")
    print("  - output/shopping_list.md")
    print("  - logs/agent_execution.log")
    print()
    
    return result


def run():
    """Alias for main() - used by crewai run command."""
    return main()


if __name__ == "__main__":
    main()

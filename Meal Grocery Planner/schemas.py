"""Pydantic schemas for structured meal & grocery planning."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class GroceryItem(BaseModel):
    name: str = Field(description="Name of the grocery item")
    quantity: str = Field(description="Quantity needed (e.g. '2 lbs', '1 gallon')")
    estimated_price: str = Field(description="Estimated price (e.g. '$3-5')")
    category: str = Field(description="Store section (e.g. 'Produce', 'Dairy')")


class MealPlan(BaseModel):
    meal_name: str = Field(description="Name of the meal")
    difficulty_level: str = Field(description="'Easy', 'Medium', or 'Hard'")
    servings: int = Field(description="Number of people it serves")
    researched_ingredients: List[str] = Field(
        description="Ingredients found through research"
    )


class ShoppingCategory(BaseModel):
    section_name: str = Field(description="Store section name")
    items: List[GroceryItem] = Field(description="Items in this section")
    estimated_total: str = Field(description="Estimated cost for this section")


class GroceryShoppingPlan(BaseModel):
    total_budget: str = Field(description="Total planned budget")
    meal_plans: List[MealPlan] = Field(description="Planned meals")
    shopping_sections: List[ShoppingCategory] = Field(
        description="Organized by store sections"
    )
    shopping_tips: List[str] = Field(
        description="Money-saving and efficiency tips"
    )

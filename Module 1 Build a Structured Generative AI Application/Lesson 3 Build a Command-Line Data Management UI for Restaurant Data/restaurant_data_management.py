from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
import json
import os
import shutil
import io
import unittest
from unittest.mock import patch

FILEPATH = 'structured_restaurant_data.json'
BACKUP_PATH = 'structured_restaurant_data.json.bak'
EXAMPLE_RESTAURANT_PARAGRAPH = 'Down in **Santa Monica**, **Mar de Cortez** serves as a **sun-drenched**, **casual taqueria** specializing in **Baja-style seafood**. With a **4.2/5** rating, it captures the salt-air energy of the coast through its signature beer-battered snapper tacos and zesty octopus ceviche, making it a premier spot for open-air dining near the pier. Price range:' 

# --- Helper Functions for Database Persistence ---

def load_data(file_path):
    """Loads JSON data from file or returns an empty list if not found."""
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_data(file_path, data):
    """Saves data securely to the target file path."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def show_restaurant_card(res, index):
    """Prints a clean, user-friendly visualization of a restaurant record."""
    print(f"\n--- [RECORD INDEX: {index}] ---")
    print(f"Name:        {res.get('name', 'N/A')}")
    print(f"Location:    {res.get('location', 'N/A')}")
    print(f"Cuisine:     {res.get('cuisine', 'N/A')}")
    print(f"Rating:      {res.get('rating', 'N/A')}/5")
    print(f"Amiance:     {res.get('ambiance', 'N/A')}")
    print(f"Price Range: {res.get('price_range', 'N/A')}")
    print(f"Specialties: {', '.join(res.get('specialties', [])) if isinstance(res.get('specialties'), list) else res.get('specialties', 'N/A')}")
    print("-" * 25)

# --- Core LLM Architecture ---

def restaurant_data_structure_prompt_generation(restaurant_paragraph):
    system_msg = (
        "You are an expert data engineering assistant. Your task is to extract structural details "
        "from a text paragraph describing a restaurant and format the output strictly as a valid JSON object. "
        "The JSON object must contain these fields: 'id' (integer), 'name' (string), 'location' (string), "
        "'cuisine' (string), 'rating' (float), 'specialties' (list of strings), 'ambiance' (string), and 'price_range' (string)."
    )
    
    prompt_txt = (
        f"Extract information from the following paragraph and parse it into the requested JSON schema. "
        f"Do not include any Markdown code blocks, text explanations, or wrapping like ```json. Output ONLY raw JSON.\n\n"
        f"Paragraph:\n{restaurant_paragraph}"
    )
    return system_msg, prompt_txt

def llm_model(system_msg, prompt_txt, params=None):
    # Switch to the exact chat-supported model from the API response
    model_id = 'mistralai/mistral-small-3-1-24b-instruct-2503'
    project_id = "skills-network"
    
    creds = Credentials(url="https://us-south.ml.cloud.ibm.com")
    
    # Use max_tokens instead of max_new_tokens for .chat() compatibility
    if params is None:
        params = {"max_tokens": 512, "temperature": 0.1}
        
    model = ModelInference(
        model_id=model_id,
        credentials=creds,
        project_id=project_id,
        params=params
    )
    
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": prompt_txt}
    ]
    
    response = model.chat(messages=messages)
    return response['choices'][0]['message']['content'].strip()

def JSON_auto_repair_prompts(response, error_message):
    system_msg = (
        "You are a precise JSON repair assistant. Your sole job is to fix syntax errors "
        "(such as missing commas, unmatched quotes, or unescaped characters) in a broken JSON string. "
        "Return ONLY the fixed, fully valid, parseable JSON string. No explanations, no markdown blocks."
    )
    
    prompt_txt = (
        f"The following string failed compilation with this parsing exception:\n{error_message}\n\n"
        f"Broken String:\n{response}\n\n"
        f"Please correct the syntax errors and output the cleaned raw JSON."
    )
    return system_msg, prompt_txt

def new_data_entry_process(paragraph, itemId):
    system_msg, prompt_txt = restaurant_data_structure_prompt_generation(paragraph)
    raw_response = llm_model(system_msg, prompt_txt)
    
    try:
        structured_data = json.loads(raw_response)
    except Exception as initial_err:
        print(f"[Warning] Direct structural extraction parsing failed: {initial_err}. Initiating auto-repair step...")
        repair_system, repair_prompt = JSON_auto_repair_prompts(raw_response, str(initial_err))
        repaired_response = llm_model(repair_system, repair_prompt)
        try:
            structured_data = json.loads(repaired_response)
        except Exception as catastrophic_err:
            print(f"[Critical Error] Auto-repair pipeline failed to reconcile data formatting constraints.")
            raise catastrophic_err

    structured_data["id"] = int(itemId)
    return structured_data

# --- Main Shell Interface Engine ---

def manage_restaurants(file_path=FILEPATH, backup_path=BACKUP_PATH):
    while True:
        data = load_data(file_path)
        print(f"\n🏨 RESTAURANT DATABASE | Records: {len(data)}")
        print("1. Browse All (Names)")
        print("2. View Detailed Record")
        print("3. Add New Restaurant")
        print("4. Edit Restaurant Info")
        print("5. Delete Restaurant")
        print("6. Exit")
        
        choice = input("\nAction: ")

        if choice == '1':
            print("\n--- Current Listings ---")
            for index, record in enumerate(data):
                name = record.get("name", "N/A")
                print(f"[{index}] {name}")
        
        elif choice == '2':
            try:
                idx_input = input("Enter the index of the record you want to view: ")
                index = int(idx_input)
                if 0 <= index < len(data):
                    show_restaurant_card(data[index], index)
                else:
                    print("Invalid index.")
            except ValueError:
                print("Invalid index. Please enter a valid integer.")

        elif choice in ['3', '4', '5']:
            print("\n❗ SECURITY WARNING: You are entering write-mode.")
            print("Changes will be saved to the database immediately.")
            confirm = input("Are you sure? (type 'yes' to proceed): ").lower()
            if confirm != 'yes':
                print("Operation cancelled.")
                continue

            if choice == '3':
                itemId = 1000000 + len(data) + 1
                paragraph = input("\nEnter the new restaurant descriptive paragraph:\n")
                
                print("Processing data extraction via LLM engine...")
                try:
                    new_record = new_data_entry_process(paragraph, itemId)
                    data.append(new_record)
                    save_data(file_path, data)
                    print("✅ Restaurant added.")
                except Exception as e:
                    print(f"❌ Operation Failed. Could not process text representation: {e}")

            elif choice == '4':
                try:
                    idx_input = input("Enter the record index you want to edit: ")
                    index = int(idx_input)
                    
                    if 0 <= index < len(data):
                        current_record = data[index]
                        print(f"\nEditing Record [{index}]: {current_record.get('name', 'N/A')}")
                        print("Press [Enter] to skip a field and keep its existing value.\n")
                        
                        for key in list(current_record.keys()):
                            if key in ['id']:
                                continue
                                
                            current_val = current_record[key]
                            new_val = input(f"Field '{key}' [{current_val}]: ").strip()
                            
                            if new_val != "":
                                if isinstance(current_val, float):
                                    current_record[key] = float(new_val)
                                elif isinstance(current_val, int):
                                    current_record[key] = int(new_val)
                                elif isinstance(current_val, list):
                                    current_record[key] = [item.strip() for item in new_val.split(",")]
                                else:
                                    current_record[key] = new_val
                        
                        save_data(file_path, data)
                        print("✅ Record updated.")
                    else:
                        print("Invalid index.")
                except ValueError:
                    print("Invalid index. Please enter a valid integer.")

            elif choice == '5':
                try:
                    idx_input = input("Enter the record index you want to permanently delete: ")
                    index = int(idx_input)
                    
                    if 0 <= index < len(data):
                        removed_item = data.pop(index)
                        save_data(file_path, data)
                        print(f"✅ Record for '{removed_item.get('name', 'N/A')}' deleted successfully.")
                    else:
                        print("Invalid index.")
                except ValueError:
                    print("Invalid index. Please enter a valid integer.")

        elif choice == '6':
            print("Exiting database shell engine. Goodbye!")
            break
        else:
            print("Invalid input.")

# --- Automated Testing Infrastructure ---

class TestRestaurantDatabase(unittest.TestCase):
    
    def setUp(self):
        """Create a temporary clean database for testing."""
        self.test_file = 'structured_restaurant_data_unit_test.json'
        self.test_file_backup = 'structured_restaurant_data_unit_test.json.bak'
        self.initial_data = [{"name": "Test Cafe", "location": "Test City"}]
        with open(self.test_file, 'w') as f:
            json.dump(self.initial_data, f)

    def tearDown(self):
        """Clean up the test file after tests."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.test_file_backup):
            os.remove(self.test_file_backup)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_add_and_delete_restaurant_success(self, mock_stdout, mock_input):
        mock_restaurant = 'The Copper Sprout is a high-concept, Modern Appalachian farm-to-table destination that blends an industrial-chic aesthetic with rustic forest charm, featuring reclaimed wood and amber lighting to create a sophisticated yet cozy vibe. Priced in the $$ category, the menu celebrates seasonal foraging and local heritage, headlined by signature dishes like Cast-Iron Smoked Trout with pickled fiddlehead ferns and hand-foraged Wild Mushroom Risotto with aged goat cheese. The experience is designed to be intimate and earthy, making it a premier spot for those seeking high-quality, smokehouse-influenced cuisine in a refined, atmospheric setting.'
        mock_input.side_effect = ['3', 'yes', mock_restaurant, '6']
        
        try:
            manage_restaurants(self.test_file, self.test_file_backup)
        except SystemExit:
            pass

        with open(self.test_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 2)
        self.assertIn("✅ Restaurant added.", mock_stdout.getvalue())

        mock_input.side_effect = ['5', 'yes', '1', '6']
        
        try:
            manage_restaurants(self.test_file, self.test_file_backup)
        except SystemExit:
            pass

        with open(self.test_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 1)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_delete_security_cancel(self, mock_stdout, mock_input):
        mock_input.side_effect = ['5', 'no', '6']
        
        manage_restaurants(self.test_file, self.test_file_backup)
        
        with open(self.test_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 1)
        self.assertIn("Operation cancelled.", mock_stdout.getvalue())
        
if __name__ == "__main__":
    unittest.main()
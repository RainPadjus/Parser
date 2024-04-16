import os

from subcategories_parser import SubcategoriesParser
from law_parser import LawParser
import json

NUM_LAWS_TO_PROCESS = 10  # Set to None to process all laws, or specify an integer value

def count_laws(data):
    total_laws = 0
    for category, subcategories in data.items():
        for subcategory, subcategory_data in subcategories.items():
            laws = subcategory_data.get("laws", [])
            total_laws += len(laws)
            for law in laws:
                if "url" in law:
                    total_laws += 1
    return total_laws

def main():
    subcategories_parser = SubcategoriesParser()
    all_data = subcategories_parser.parse_subcategories()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    subcategories_json_path = os.path.join(script_dir, "output_laws_subcategories.json")
    json_data = json.dumps(all_data, indent=4, ensure_ascii=False)
    with open(subcategories_json_path, "w", encoding="utf-8") as f:
        f.write(json_data)

    print(f"\nInitial data with subcategories has been saved to '{subcategories_json_path}'")

    total_laws = count_laws(all_data)
    print(f"\nTotal laws to process: {total_laws}/ Laws to process: {NUM_LAWS_TO_PROCESS}")

    law_parser = LawParser(subcategories_parser.driver)
    law_count = 0

    for category, subcategories in all_data.items():
        for subcategory, subcategory_data in subcategories.items():
            laws = subcategory_data.get("laws", [])
            for law in laws:
                if NUM_LAWS_TO_PROCESS is not None and law_count >= NUM_LAWS_TO_PROCESS:
                    break

                law_url = law.get("url")
                if law_url:
                    law_count += 1
                    print(f"Parsing law: {law_count}/{total_laws}: {law['title']} ({law_url})")

                    try:
                        law_details = law_parser.parse_law_page(law_url)
                        if law_details:
                            law["details"] = law_details
                        else:
                            print(f"Skipping law '{law['title']}' due to an error.")
                    except Exception as e:
                        print(f"Error parsing law '{law['title']}': {e}")

    json_data = json.dumps(all_data, indent=4, ensure_ascii=False)
    with open(os.path.join(script_dir, "output_laws_full.json"), "w", encoding="utf-8") as f:
        f.write(json_data)

    print("\nJSON data has been saved to 'output_laws_full.json'")

    subcategories_parser.driver.quit()

if __name__ == "__main__":
    main()

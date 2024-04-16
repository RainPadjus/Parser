from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SubcategoriesParser:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.url = 'https://www.riigiteataja.ee/jaotused.html?jaotus=S%C3%9CSTJAOT'

    def parse_laws_table(self):
        laws = []
        table_rows = self.driver.find_elements(By.CSS_SELECTOR, "table.data tbody tr")
        for row in table_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells:
                law_data = {
                    "title": cells[0].find_element(By.TAG_NAME, "a").text.strip(),
                    "url": cells[0].find_element(By.TAG_NAME, "a").get_attribute("href"),
                    "publication_note": cells[1].text.strip(),
                    "issuer": cells[2].text.strip(),
                    "type": cells[3].text.strip(),
                    "act_number": cells[4].text.strip(),
                    "validity": cells[5].text.strip()
                }
                laws.append(law_data)
        return laws

    def parse_subcategories(self):
        self.driver.get(self.url)
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.show-system')))
        show_all_button = self.driver.find_element(By.CSS_SELECTOR, 'a.show-system')
        show_all_button.click()

        data = {}
        subcategories = self.driver.find_elements(By.CSS_SELECTOR, "div.sub > a.name, li > a.viimane-nimi")
        total_subcategories = len(subcategories)
        print(f"Total subcategories: {total_subcategories}")

        for index in range(total_subcategories):
            subcat_name = subcategories[index].text.strip()
            print(f"Processing subcategory {index + 1}/{total_subcategories}: {subcat_name}")
            self.driver.execute_script("arguments[0].click();", subcategories[index])

            path_element = self.driver.find_element(By.CSS_SELECTOR, "p.path")
            path = [span.text.strip() for span in path_element.find_elements(By.CSS_SELECTOR, "span, a") if span.text.strip() != "→"]

            current_data = data
            for category in path:
                if category not in current_data:
                    current_data[category] = {}
                current_data = current_data[category]
            current_data["laws"] = self.parse_laws_table()

            self.driver.execute_script("window.history.go(-1)")
            subcategories = self.driver.find_elements(By.CSS_SELECTOR, "div.sub > a.name, li > a.viimane-nimi")

        print("All subcategories processed.")
        return data
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

class LawParser:
    def __init__(self, driver):
        self.driver = driver

    def parse_meta_info(self):
        try:
            meta_table = self.driver.find_element(By.CSS_SELECTOR, "table.meta")
            rows = meta_table.find_elements(By.TAG_NAME, "tr")
            meta_info = {}
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) == 2:
                    meta_info[row.find_element(By.TAG_NAME, "th").text] = cells[1].text
            return meta_info
        except NoSuchElementException:
            return None

    def parse_enactment_details(self):
        try:
            enactment_details = {}
            vv_element = self.driver.find_element(By.CSS_SELECTOR, "p.vv")
            enactment_details['text'] = vv_element.text.replace('\n', ' ')
            enactment_details['link'] = vv_element.find_element(By.TAG_NAME, "a").get_attribute("href")
            return enactment_details
        except NoSuchElementException:
            return None

    def parse_sections(self):
        sections = []
        headers = self.driver.find_elements(By.CSS_SELECTOR, "h2.level2, h3")
        current_section = None
        for header in headers:
            if header.tag_name == "h2":
                current_section = {
                    "title": header.text.strip(),
                    "subsections": []
                }
                sections.append(current_section)
            elif header.tag_name == "h3" and current_section:
                subsection_data = {
                    "title": header.text.strip(),
                    "content": [],
                    "references": []
                }
                next_elements = header.find_elements(By.XPATH, "./following-sibling::*")
                for elem in next_elements:
                    if elem.tag_name.lower() in ["h2", "h3"]:
                        break
                    if elem.tag_name.lower() == "p":
                        content_text = elem.text.strip()
                        content_references = []
                        links = elem.find_elements(By.TAG_NAME, "a")
                        for link in links:
                            link_text = link.text.strip()
                            href = link.get_attribute("href")
                            if link_text or href:
                                content_references.append({
                                    "text": link_text,
                                    "url": href.strip() if href else None
                                })
                        if content_references:
                            subsection_data["content"].append({"text": content_text, "references": content_references})
                        else:
                            subsection_data["content"].append({"text": content_text})
                current_section["subsections"].append(subsection_data)
        return sections

    def parse_amendments_table(self):
        try:
            toggle_element = self.driver.find_element(By.CSS_SELECTOR, 'p#toggle-laws a')
            toggle_element.click()
            wait = WebDriverWait(self.driver, 1)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.wrap > table.data-compact")))
        except NoSuchElementException:
            return None

        try:
            table = self.driver.find_element(By.CSS_SELECTOR, "div.wrap > table.data-compact")
            rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip the header row
            amendments = []
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                amendment_data = {
                    "adoption_date": cols[0].text,
                    "publication": {
                        "text": cols[1].text,
                        "url": cols[1].find_element(By.TAG_NAME, "a").get_attribute("href")
                    },
                    "enforcement_date": cols[2].text
                }
                amendments.append(amendment_data)
            return amendments
        except NoSuchElementException:
            return None

    def parse_law_page(self, url):
        self.driver.get(url)
        wait = WebDriverWait(self.driver, 1)  

        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.fixed")))
        except Exception as e:
            print(f"Error waiting for page to load: {e}")
            return None

        law_data = {
            "title": self.driver.find_element(By.CSS_SELECTOR, "h1.fixed").text,
            "meta_info": self.parse_meta_info(),
            "enactment_details": self.parse_enactment_details(),
            "sections": self.parse_sections(),
            "amendments": self.parse_amendments_table()
        }
        return law_data
import requests
from bs4 import BeautifulSoup as bs
import json
from datetime import datetime
import xlsxwriter
import logging
import os

logger = logging.getLogger(__name__)

class WebsiteScraper:
    """
    A class for scraping circulars from the EPFO website.
    """

    def __init__(self, initial_url='https://www.epfindia.gov.in/site_en/circulars.php',
                 post_url='https://www.epfindia.gov.in/site_en/get_cir_content.php',
                 base_url='https://www.epfindia.gov.in/'):
        self.INITIAL_URL = initial_url
        self.POST_URL = post_url
        self.BASE_URL = base_url
        self.all_circulars = []
        self.headers = []

    def _get_dropdown_values(self, soup):
        """
        Extracts dropdown values from the initial page.
        """
        dropdown = soup.find('select', {'id': 'dd'})
        if dropdown:
            return [option['value'] for option in dropdown.find_all('option') if option['value']]
        return []

    def _parse_rows(self, rows, year=''):
        """
        Parses table rows, extracts data, URLs, and appends year and formatted date.
        """
        parsed_rows = []
        for row in rows:
            cols = row.find_all('td')
            row_data = [col.text.strip() for col in cols]

            # Extract URLs from the 3rd and 4th <td> elements
            hindi_url = cols[2].find('a')['href'] if len(cols) > 2 and cols[2].find('a') else "NA"
            hindi_url = self.BASE_URL + hindi_url if hindi_url != "NA" and not hindi_url.startswith("http") else hindi_url

            english_url = cols[3].find('a')['href'] if len(cols) > 3 and cols[3].find('a') else "NA"
            english_url = self.BASE_URL + english_url if english_url != "NA" and not english_url.startswith("http") else english_url

            # Add URLs to the respective columns in row_data
            if len(row_data) > 2: row_data[2] = hindi_url
            if len(row_data) > 3: row_data[3] = english_url
            
            row_data.append(year)
            
            # Check if the last 10 characters of row_data[1] are in dd/mm/yyyy format
            formatted_date = 'No Date'
            if len(row_data) > 1 and len(row_data[1]) >= 10 and row_data[1][-10:].count('/') == 2:
                try:
                    date_str = row_data[1][-10:]
                    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                    formatted_date = date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    formatted_date = 'Invalid Date'
            row_data.append(formatted_date)

            parsed_rows.append(row_data)

        return parsed_rows

    def _json_to_excel(self, json_data, excel_file):
        """
        Converts JSON data to an Excel file.
        """
        if not json_data:
            logger.warning("No data to write to Excel.")
            return

        try:
            workbook = xlsxwriter.Workbook(excel_file, {'strings_to_numbers': False})
            worksheet = workbook.add_worksheet()
            text_format = workbook.add_format({'num_format': '@'})

            # Write headers
            headers = list(json_data[0].keys())
            for col_num, header in enumerate(headers):
                worksheet.write(0, col_num, header)

            # Write data rows
            for row_num, item in enumerate(json_data, start=1):
                for col_num, header in enumerate(headers):
                    value = item.get(header, "")
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value, ensure_ascii=False)
                    elif not isinstance(value, str):
                        value = "" if value is None else str(value)
                    worksheet.write(row_num, col_num, value, text_format)

            workbook.close()
            logger.info(f"Data successfully written to Excel: {excel_file}")
        except Exception as e:
            logger.error(f"Error writing to Excel file {excel_file}: {e}")

    def scrape_circulars(self):
        """
        Fetches and parses circulars from the EPFO website.
        """
        try:
            # Fetch initial page
            response = requests.get(self.INITIAL_URL)
            response.raise_for_status()
            soup = bs(response.text, 'html.parser')

            # Extract headers and initial table rows
            table = soup.find('table')
            if table:
                self.headers = [header.text.strip() for header in table.find_all('th')]
                self.headers.append('Year')
                self.headers.append('Date')

                initial_rows = [
                    row for row in table.find_all('tr', class_='small_font')
                    if row.find_all('td')
                ]
                self.all_circulars.extend(self._parse_rows(initial_rows))
            else:
                logger.warning("No table found on the initial page.")
                return

            # Get the dropdown values for different years
            dropdown_values = self._get_dropdown_values(soup)

            # Fetch and parse rows for each year in the dropdown
            for value in dropdown_values:
                post_data = {'yr': value}
                try:
                    post_response = requests.post(self.POST_URL, data=post_data)
                    post_response.raise_for_status()
                    soup2 = bs(post_response.text, 'html.parser')
                    year_rows = [
                        row for row in soup2.find_all('tr', class_='small_font')
                        if row.find_all('td')
                    ]
                    circulars = self._parse_rows(year_rows, year=value)
                    self.all_circulars.extend(circulars)
                except requests.RequestException as e:
                    logger.error(f"Error fetching data for year {value}: {e}")
            
            logger.info(f"Scraped {len(self.all_circulars)} circulars.")

        except requests.RequestException as e:
            logger.error(f"Error fetching initial page {self.INITIAL_URL}: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during scraping: {e}")

    def save_data(self, json_file='circulars.json', excel_file='circulars.xlsx'):
        """
        Converts scraped data to dictionary format and saves to JSON and Excel files.
        """
        if not self.all_circulars or not self.headers:
            logger.warning("No circulars data or headers available to save.")
            return

        circulars_dicts = [{self.headers[i]: row[i] for i in range(len(self.headers))} for row in self.all_circulars]

        # Save circulars_dicts as JSON
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(circulars_dicts, f, ensure_ascii=False, indent=4)
            logger.info(f"Data successfully written to JSON: {json_file}")
        except Exception as e:
            logger.error(f"Error writing to JSON file {json_file}: {e}")

        # Write data to Excel
        self._json_to_excel(circulars_dicts, excel_file)

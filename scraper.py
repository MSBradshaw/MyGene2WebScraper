from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pandas as pd
import time

cap = DesiredCapabilities().FIREFOX
cap["marionette"] = True

driver = webdriver.Firefox(capabilities=cap, executable_path='/usr/local/Cellar/geckodriver/0.26.0/bin/geckodriver')

driver.get(
    "https://mygene2.org/MyGene2/genes")

time.sleep(5)
print('Awake!')

buttons = driver.find_element_by_xpath("//*[contains(text(), 'All')]")
buttons.click()

table = driver.find_element_by_id('genestable')
table_info = pd.DataFrame(
        {'gene': [],
         'gene_link': [],
         'number_of_families': [],
         'novel_gene': [],
         'phenotype_class': [],
         'report_link': []})
table_info_count = 0
for row in table.find_elements_by_tag_name('tr'):
    cells = row.find_elements_by_tag_name('td')
    single_gene_info = []
    if len(cells) > 0:
        print(table_info_count)
        # there are 5 cells
        a = cells[0].find_element_by_tag_name('a')
        s = a.find_element_by_tag_name('span')
        single_gene_info.append(s.text)  # 0 name of the gene
        single_gene_info.append(a.get_attribute("href"))  # 1 gene link
        single_gene_info.append(cells[1].text)  # 2 number of families
        single_gene_info.append(cells[2].text)  # 3 Novel Gene
        single_gene_info.append(cells[3].find_element_by_tag_name('small').text)  # 4 Phenotype class
        try:
            single_gene_info.append(cells[4].find_element_by_tag_name('a').get_attribute("href"))  # 5 report link
        except NoSuchElementException:
            print('<a> tag not found')
            single_gene_info.append('')
        table_info.loc[table_info_count] = single_gene_info
        table_info_count += 1

table_info.to_csv('my_gene_2_main_table.csv')

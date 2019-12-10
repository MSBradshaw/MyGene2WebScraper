from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pandas as pd
import time


def clean(string):
    string = string.replace("\\n", "")
    return string.strip()


# search-results-table
cap = DesiredCapabilities().FIREFOX
cap["marionette"] = True

driver = webdriver.Firefox(capabilities=cap, executable_path='/usr/local/Cellar/geckodriver/0.26.0/bin/geckodriver')

main_table = pd.read_csv('my_gene_2_main_table.csv')

gene_urls = main_table.iloc[:,2]
gene_names = main_table.iloc[:,1]
table_info = pd.DataFrame(
        {'gene': [],
         'variant_id': [],
         'variant_link': [],
         'het_group': [],
         'number_of_families': [],
         'inheritance': [],
         'chr:position': [],
         'alleles': [],
         'variant_type': [],
         'transcript': [],
         'cDNA_change': [],
         'protein_change': [],
         'confidence_in_pathogenicity': []})
table_info_count = 0
global_count = 0
for i in range(942, len(gene_urls)):

    url = gene_urls[i]
    name = gene_names[i]
    print(url)
    driver.get(url)
    time.sleep(5)
    pagination = driver.find_elements_by_class_name('pagination')
    try:
        buttons = pagination[1].find_elements_by_tag_name('a')
    except IndexError:
        print('Index error on: ' + url)
        continue
    buttons[2].click()
    time.sleep(5)
    table = driver.find_element_by_id('search-results-table')
    line = 0
    for tr in table.find_elements_by_tag_name('tr'):
        try:
            row = [name]
            cells = tr.find_elements_by_tag_name('td')
            if len(cells) == 0:
                continue
            row.append(cells[0].find_element_by_tag_name('a').get_attribute('innerHTML'))  # variant ID
            row.append(cells[0].find_element_by_tag_name('a').get_attribute('href'))  # variant link
            row.append(cells[1].find_element_by_tag_name('a').get_attribute('innerHTML'))  # het group
            row.append(cells[2].get_attribute('innerHTML'))  # number of families
            # loop over the last 8 columns, they are all formated the same
            for i in range(3, 11):
                row.append(clean(cells[i].find_element_by_tag_name('span').get_attribute('innerHTML')))
            table_info.loc[table_info_count] = row
            table_info_count += 1
            line += 1
        except:
            print('Error on: ' + url + ' line: ' + line)
    print('Competed: ' + str(global_count))
    table_info.to_csv('my_gene_2_variant_tables.csv', mode='a', header=False)
    table_info = pd.DataFrame(
        {'gene': [],
         'variant_id': [],
         'variant_link': [],
         'het_group': [],
         'number_of_families': [],
         'inheritance': [],
         'chr:position': [],
         'alleles': [],
         'variant_type': [],
         'transcript': [],
         'cDNA_change': [],
         'protein_change': [],
         'confidence_in_pathogenicity': []})
    table_info_count = 0
    global_count += 1


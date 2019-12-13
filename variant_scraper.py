from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pandas as pd
import time
import re


def clean(string):
    string = string.replace("\\n", "")
    return string.strip()


def process_item_in_pheno_col(word):
    word = word.strip()
    id_matches = re.findall(r'>HP:\d*<', word)
    hpo_id = 'NONE FOUND'
    if len(id_matches) != 0:
        hpo_id = id_matches[0].replace('>', '')
        hpo_id = hpo_id.replace('<', '')

    name_matches = re.findall(r'^[0-9a-zA-Z ]+ \(', word)
    hpo_name = "None found"
    if len(name_matches) != 0:
        hpo_name = name_matches[0].replace(' (', '')
    return hpo_name, hpo_id


# search-results-table
cap = DesiredCapabilities().FIREFOX
cap["marionette"] = True

driver = webdriver.Firefox(capabilities=cap, executable_path='/usr/local/Cellar/geckodriver/0.26.0/bin/geckodriver')

gene_table = pd.read_csv('my_gene_2_gene_tables.csv')

genes = gene_table.iloc[:, 1]
variant_ids = gene_table.iloc[:, 2]
variant_urls = gene_table.iloc[:, 3]
table_info = pd.DataFrame(
    {'gene': [],
     'variant_id': [],
     'family_id': [],
     'family_url': [],
     'inheritance': [],
     'phenotype_name': [],
     'phenotype_hpo_id': [],
     'confidence_in_pathogenicity': []})
table_info_counter = 0
# set this to where ever you left off
global_count = 0
table_info.to_csv('my_gene_2_variantes_by_family_tables.csv', mode='a', header=True)
for i in range(global_count, len(variant_urls)):
    url = variant_urls[i]
    print(url)
    gene = genes[i]
    id = variant_ids[i]
    driver.get(url)
    time.sleep(5)
    # find the pagination buttons
    pagination = driver.find_elements_by_class_name('pagination')
    try:
        # find the show all button
        buttons = pagination[1].find_elements_by_tag_name('a')
    except IndexError:
        print('Index error on: ' + url)
        continue
    # press the show all button
    buttons[2].click()
    time.sleep(5)
    table = driver.find_element_by_id('search-results-table')
    for tr in table.find_elements_by_tag_name('tr'):
        cells = tr.find_elements_by_tag_name('td')
        if len(cells) == 0:
            # this is not a real row so skip it, porbably the first of each table
            continue
        phenocol = cells[2]
        # find all divs with blue text
        allbutton = phenocol.find_elements_by_class_name('mygene-text-blue')
        # the ... button is the penultimate
        try:
            allbutton[-2].click()
        except ElementNotInteractableException:
            print('All button does not exist')
            continue
        family_id = cells[0].find_element_by_tag_name('a').get_attribute('innerHTML')
        family_url = cells[0].find_element_by_tag_name('a').get_attribute('href')
        inheritance = cells[1].find_element_by_tag_name('span').text
        confidence = cells[3].get_attribute('innerHTML')
        row = [gene, id, family_id, family_url, inheritance]
        for p in phenocol.find_elements_by_class_name('ng-scope'):
            row = [gene, id, family_id, family_url, inheritance]
            messy_text = p.get_attribute('innerHTML')
            name, hpo = process_item_in_pheno_col(messy_text)
            if hpo == 'NONE FOUND':
                continue
            row.append(name)
            row.append(hpo)
            row.append(confidence)
            table_info.loc[table_info_counter] = row
            table_info_counter += 1
    print(global_count)
    global_count += 1
    table_info.to_csv('my_gene_2_variantes_by_family_tables.csv', mode='a', header=False)
    table_info = pd.DataFrame(
        {'gene': [],
         'variant_id': [],
         'family_id': [],
         'family_url': [],
         'inheritance': [],
         'phenotype_name': [],
         'phenotype_hpo_id': [],
         'confidence_in_pathogenicity': []})

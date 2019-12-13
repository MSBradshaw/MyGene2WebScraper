from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pandas as pd
import time
import re


def clean_name(word):
    return word.replace('Name of condition: ','')


def get_omim_id(word):
    print(word)
    id_matches = re.findall(r'>\d*<', word)
    hpo_id = "None"
    if len(id_matches) != 0:
        hpo_id = id_matches[0].replace('>', '')
        hpo_id = hpo_id.replace('<', '')
    print(hpo_id)
    return hpo_id


# search-results-table
cap = DesiredCapabilities().FIREFOX
cap["marionette"] = True

driver = webdriver.Firefox(capabilities=cap, executable_path='/usr/local/Cellar/geckodriver/0.26.0/bin/geckodriver')

variant_table = pd.read_csv('my_gene_2_gene_tables.csv')

# get a unique set of family IDs
family_ids = list(set(variant_table.iloc[:, 2]))
table_info = pd.DataFrame(
    {'family_id': [],
     'name_of_condition': [],
     'omim#': [],
     'omim_url': []})
table_info_counter = 0
global_count = 1101
table_info.to_csv('my_gene_2_family_health_tables.csv', mode='a', header=True)
for i in range(global_count,len(family_ids)):
    family_id = family_ids[i]
    row = [family_id]
    url = 'https://mygene2.org/MyGene2/familyprofile/' + str(family_id) + '/health'
    try:
        driver.get(url)
    except WebDriverException:
        print('404 Error')
        print(url)
    time.sleep(5)
    div = driver.find_elements_by_class_name('omim-nameofcondition')
    global_count += 1
    print(global_count)
    if len(div) == 0:
        print('error in family: ' + str(family_id))
        print(url)
        continue
    h4s = div[0].find_elements_by_tag_name('h4')
    row.append(clean_name(h4s[0].find_element_by_tag_name('span').text))
    row.append(h4s[1].find_element_by_tag_name('a').get_attribute('innerHTML'))
    row.append(h4s[1].find_element_by_tag_name('a').get_attribute('href'))
    if row[2] == '':
        row[2] = 'N/A'
    table_info.loc[table_info_counter] = row
    table_info_counter += 1
    # every 100 familys save progress
    if global_count % 100 == 0:
        table_info.to_csv('my_gene_2_family_health_tables.csv', mode='a', header=False)
        table_info = pd.DataFrame(
            {'family_id': [],
             'name_of_condition': [],
             'omim#': [],
             'omim_url': []})

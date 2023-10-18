from selenium import webdriver
from selenium.webdriver.common.by import By
from time import strptime
import pyperclip
import requests
from threading import Thread


URL = 'https://limitlesstcg.com'


def get_all_tournaments(driver):

    # Initialize list of tournament page links
    links = []

    # Get all tournament links
    elements = driver.find_elements(By.XPATH, '/html/body/main/div/table/tbody/tr/td[3]/a')

    # Append each tournament page link to list
    for e in elements:
        links.append(e.get_attribute('href'))

    return links

def get_tournament_data(driver, t_category, t_id):
    
    row={}

    # Create the id for the tournament
    row['category_tournament'] = t_category
    row['id_tournament'] = t_id
    row['name_tournament'] = driver.find_element(By.CLASS_NAME, 'infobox-heading').text.strip().replace(',','')
    row['country_tournament'] = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[1]/img').get_attribute('data-tooltip')
    row['valid_rotation_at_tournament'] = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[2]/a[1]').get_attribute('href').split('=')[-1]
    t_date = driver.find_element(By.CLASS_NAME, 'infobox-line').text.split('•')[0].strip()
    t_day, t_month, t_year = t_date.split(' ')
    t_day = t_day if len(t_day) == 2 else '0' + t_day
    t_month = str(strptime(t_month[:3],'%b').tm_mon)
    t_month = t_month if len(t_month) == 2 else '0' + t_month
    row['year_tournament'] = t_year
    row['month_tournament'] = t_month
    row['day_tournament'] = t_day

    e_decklist_row = driver.find_elements(By.XPATH, '/html/body/main/div/table/tbody/tr')
    
    for e in e_decklist_row:
        row['ranking_player_tournament'] = e.find_element(By.XPATH, './td[1]').text
        row['country_player'] = e.find_element(By.XPATH, './td[3]/div/img').get_attribute('data-tooltip')
        
        e_player = e.find_element(By.XPATH, './td[2]/div/a[1]')
        row['id_player'] = e_player.get_attribute('href').split('/')[-1]
        row['name_player'] = e_player.text

        row['combo_type_id'] = e.find_element(By.XPATH, './td[4]/a').get_attribute('href').split('/')[-1].split('?')[0]
        row['combo_type_name'] = e.find_element(By.XPATH, './td[4]/a/span').get_attribute('data-tooltip')
        
        decklist_link = e.find_element(By.XPATH, './td[5]/a').get_attribute('href')

        driver.get(URL+e_player.get_attribute('href'))
        row['all_time_score'] = driver.find_element(By.XPATH, '/html/body/main/div/section[2]/div/table[2]/tbody/tr[2]/td[2]').text

        driver.get(URL+decklist_link)
        e_pokemon_cards = driver.find_elements(By.XPATH, '/html/body/main/div/div[1]/div[2]/div[1]/div[1]/div/a[1]')
        e_trainer_cards = driver.find_elements(By.XPATH, '/html/body/main/div/div[1]/div[2]/div[1]/div[2]/div/a[1]')
        card_urls = [element.get_attribute('href') for element in e_pokemon_cards]
        card_urls.extend([element.get_attribute('href') for element in e_trainer_cards])
        card_names = [element.find_element(By.XPATH, './span[2]').text for element in e_pokemon_cards]
        card_names.extend([element.find_element(By.XPATH, './span[2]').text for element in e_trainer_cards])
        card_amounts = [element.find_element(By.XPATH, './span[1]').text for element in e_pokemon_cards]
        card_amounts.extend([element.find_element(By.XPATH, './span[1]').text for element in e_trainer_cards])

        cards_to_iterate = zip(card_urls, card_names, card_amounts)
        for card_url, card_name, card_amount in cards_to_iterate:
            driver.get(URL+card_url)
            e_card = driver.find_element(By.XPATH, '/html/body/main/div/section[1]/div[2]/table/tbody/tr[2]')

            row['name_card'] = card_name
            row['amount_card'] = card_amount
            row['id_card'] = ''.join(e_card.find_element(By.XPATH, './td[1]/a').get_attribute('href').split('/')[-2:])
            row['price_card'] = float(e_card.find_element(By.XPATH, './td[2]/a').text.replace('$',''))
            row['type_card'] = driver.find_element(By.XPATH, '/html/body/main/div/section[1]/div[1]/div[2]/div[1]/div[1]/div[1]/p[2]').text.split('-')[0].strip()
            if row['type_card'] == 'Pokémon':
                row['energy_type_card'] = driver.find_element(By.XPATH, '/html/body/main/div/section[1]/div[1]/div[2]/div[1]/div[1]/div[1]/p[1]').text.split('-')[1].strip()
            else:
                row['energy_type_card'] = 'None'
            write_line(row)
    
def write_line(row):
    # Save tournament data to file
    with open('data/tournaments.csv', 'a') as f:
        f.write(f'{row["id_card"]},{row["name_card"]},{row["amount_card"]},{row["price_card"]},{row["energy_type_card"]},{row["type_card"]},{row["combo_type_id"]},{row["combo_type_name"]},{row["id_player"]},{row["name_player"]},{row["country_player"]},{row["all_time_score"]},{row["ranking_player_tournament"]},{row["id_tournament"]},{row["category_tournament"]},{row["name_tournament"]},{row["country_tournament"]},{row["year_tournament"]},{row["month_tournament"]},{row["day_tournament"]},{row["valid_rotation_at_tournament"]}\n')

import json
import requests
import pandas as pd
from bs4 import BeautifulSoup


def autoevolution_fetch():
    links = []
    s = requests.get('https://autoevolution.com/cars')
    html = s.content
    soup = BeautifulSoup(html, 'lxml')
    manufacturers = soup.find_all(class_='col2width fl bcol-white carman')
    for manufacturer in manufacturers:
        link = manufacturer.find('a')
        links.append(link['href'])
    return(links)


def get_autoevolution_cars():
    for link in autoevolution_fetch():
        cars_dir = {}
        cars_list = []
        s = requests.get(link)
        html = s.content
        soup = BeautifulSoup(html, 'lxml')
        cars = soup.find_all(class_='col2width bcol-white fl')
        for car in cars:
            car_dir = {}
            name = car.find('h4')
            link = car.find('a')
            type_ = car.find('p', class_='body')
            gasoline = car.find('p', class_='eng')
            car_dir['Name'] = name.text
            car_dir['Link'] = link_extracted
            car_dir['Type'] = type_.text
            car_dir['Gasoline'] = gasoline.text
            cars_list.append(car_dir)
        cars_dir['cars'] = cars_list
        return(cars_dir)


def fetch_exact_model_links():
    with open('output.json', 'w') as output_json:
        cars = json.load(get_autoevolution_cars())
        for car in cars['cars']:
            description_links = []
            link = car['Link']
            s = requests.get(link)
            soup = BeautifulSoup(s.content, 'lxml')
            descriptions = soup.find_all(
                'a', class_='txt upcase bold sanscond fsz17')
            for description in descriptions:
                description_link = description["href"]
                description_links.append(description_link)
            print(description_links)
            car['Info'] = description_links
        json.dump(cars, output_json)


def fetch_data():
    with open('deeper cars.json', 'r') as cars_json, open('full_data.json', 'w') as output_json, open('backup.json', 'w') as backup_json:
        cars = json.load(cars_json)
        full_cars = {}
        cars_list = []
        for car in cars['cars']:
            full_car = {
                "name": car['Name'],
                "link": car['Link'],
                "type": car['Type'],
                "gasoline": car['Gasoline'],
            }
            models = []
            for info_link in car['Info']:
                s = requests.get(info_link)
                soup = BeautifulSoup(s.content, 'lxml')
                name = soup.find(class_='padcol2 newstitle innews')
                model = {
                    "name": name.text,
                    "link": info_link,
                }
                tables = soup.find_all(class_='engine-block')
                engines = []
                for table in tables:
                    generals = table.find_all('dl')
                    title = table.find(class_='col-green2').text
                    engine = {
                        "name": title,
                    }
                    for general in generals:
                        values = general.find_all('dd')
                        keys = general.find_all('dt')
                        values_num = []
                        for value in values:
                            values_num.append(value.text)
                        for i in range(len(values)):
                            engine[keys[i].text] = values[i].text
                    engines.append(engine)
                model['engines'] = engines
                models.append(model)
            full_car['models'] = models
            print(full_car['name'])
            cars_list.append(full_car)
            json.dump(full_car, backup_json, indent=4)
        full_cars['cars'] = cars_list
        json.dump(full_cars, output_json, indent=4)


def convert_to_excel(filename):
    with open('cars.json', 'r') as cars_json:
        cars = json.load(cars_json)
        dataframes = []
        cars_list = []
        for car in cars['cars']:
            car_dic = {}
            enginesses = {}
            for model in car['models']:
                for engine in model['engines']:
                    car_dic['name'] = f'{model["name"]} {engine["name"]}'
                    try:
                        car_dic['power'] = int(engine['Power'][engine['Power'].find(
                            'RPM'):].replace('RPM', '').split('HP')[0])
                    except:
                        car_dic['power'] = ''
                    try:
                        car_dic['Top Speed'] = int(engine['Top Speed'].split(
                            '(')[1].split(')')[0].replace(' km/h', ''))
                    except:
                        car_dic['Top Speed'] = ''

                cars_list.append(car_dic)

        topspeeds = []
        for car_item in cars_list:
            try:
                topspeeds.append(int(car_item['Top Speed']))
            except:
                print('')
        table = pd.DataFrame(cars_list)
        table.to_excel(f'{filename}.xlsx')
        print(table)

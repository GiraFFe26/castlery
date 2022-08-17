import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
import os


def collect_data(url):
    retry_strategy = Retry(
        total=10,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    head = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    r = http.get(url, headers={'user-agent': head})
    soup = BeautifulSoup(r.text, 'lxml')
    countries = soup.find('div', class_='eY868y__options').find_all('a', rel='noopener')
    num_cat = 0
    while True:
        start_path = f'/root/castlery/data{num_cat}'
        try:
            os.mkdir(start_path)
            break
        except FileExistsError:
            num_cat += 1
    for a, country in enumerate(countries):
        main_url = 'https://www.castlery.com' + country.get('href')
        path_country = f'{start_path}/country{a}'
        os.mkdir(path_country)
        r = http.get(url, headers={'user-agent': head})
        soup = BeautifulSoup(r.text, 'lxml')
        categories = soup.find_all('ul', class_='Lf-Ohc__menu__newList')
        for b, category in enumerate(categories):
            path_category = f'{path_country}/category{b}'
            os.mkdir(path_category)
            page = 1
            while True:
                url = main_url + category.find('a').get('href')[3:] + f'?p={page}'
                page += 1
                r = http.get(url, headers={'user-agent': head})
                soup = BeautifulSoup(r.text, 'lxml')
                items = soup.find_all('div', class_='feH33N can-hover')
                if len(items) == 0:
                    break
                for item in items:
                    url = 'https://www.castlery.com' + item.find('a').get('href')
                    main_name = url.split('products/')[-1]
                    path_product = f'{path_category}/{main_name}'
                    os.mkdir(path_product)
                    r = http.get(url, headers={'user-agent': head})
                    soup = BeautifulSoup(r.text, 'lxml')
                    models = soup.find_all('div', class_='ixioeN__rectangleItem')
                    d = 0
                    if len(models) != 0:
                        for model in models:
                            m_url = 'https://www.castlery.com' + model.find('a').get('href')
                            r = http.get(m_url, headers={'user-agent': head})
                            soup = BeautifulSoup(r.text, 'lxml')
                            name = m_url.split('products/')[-1]
                            try:
                                soup.find('div', class_='zqPys5').find_all('span')[-2]
                            except AttributeError:
                                continue
                            path_model = f'{path_product}/{name}'
                            os.mkdir(path_model)
                            path_extra = m_url.split(name)[-1]
                            if len(path_extra) == 0:
                                path_extra = f'default{d}'
                                d += 1
                            path_variant = f'{path_model}/{path_extra}'
                            os.mkdir(path_variant)
                            try:
                                images = soup.find('ul', class_='slick-dots').find_all('li')
                            except AttributeError:
                                images = [soup.find('div', class_='EZC25+__baseContainer')]
                            urls = []
                            try:
                                url = soup.find('div', class_='ZPYEqa__dnc__image').find('img').get('data-src')
                                urls.append(url.replace(url.split('w_')[1].split(',')[0], '5000'))
                            except AttributeError:
                                pass
                            for image in images:
                                image_url = image.find('img')
                                url = image_url.get('srcset')
                                if url == None:
                                    url = image_url.get('data-src')
                                else:
                                    url = url.split()[-2]
                                urls.append(url.replace(url.split('w_')[1].split(',')[0], '5000'))
                            for k, url in enumerate(set(urls)):
                                r = http.get(url, headers={'user-agent': head})
                                with open(f'{path_variant}/image{k}.jpg', 'wb') as f:
                                    f.write(r.content)
                            variants = json.loads(soup.find_all('script')[1].contents[0]).get('isRelatedTo')
                            if variants != None:
                                for variant in variants:
                                    url = main_url + variant.get('url')
                                    path_extra = url.split(f'{name}?')[-1]
                                    if len(path_extra) == 0:
                                        path_extra = 'default'
                                    path_variant = f'{path_model}/{path_extra}'
                                    try:
                                        os.mkdir(path_variant)
                                    except FileExistsError:
                                        continue
                                    r = http.get(url, headers={'user-agent': head})
                                    soup = BeautifulSoup(r.text, 'lxml')
                                    try:
                                        images = soup.find('ul', class_='slick-dots').find_all('li')
                                    except AttributeError:
                                        images = [soup.find('div', class_='EZC25+__baseContainer')]
                                    urls = []
                                    try:
                                        url = soup.find('div', class_='ZPYEqa__dnc__image').find('img').get('data-src')
                                        urls.append(url.replace(url.split('w_')[1].split(',')[0], '5000'))
                                    except AttributeError:
                                        pass
                                    for image in images:
                                        image_url = image.find('img')
                                        url = image_url.get('srcset')
                                        if url == None:
                                            url = image_url.get('data-src')
                                        else:
                                            url = url.split()[-2]
                                        urls.append(url.replace(url.split('w_')[1].split(',')[0], '5000'))
                                    for k, url in enumerate(set(urls)):
                                        r = http.get(url, headers={'user-agent': head})
                                        with open(f'{path_variant}/image{k}.jpg', 'wb') as f:
                                            f.write(r.content)
                    else:
                        try:
                            variants = json.loads(soup.find_all('script')[1].contents[0]).get('isRelatedTo')
                        except IndexError:
                            continue
                        path_extra = url.split(main_name)[-1]
                        if len(path_extra) == 0:
                            path_extra = 'default'
                        path_variant = f'{path_product}/{path_extra}'
                        os.mkdir(path_variant)
                        try:
                            images = soup.find('ul', class_='slick-dots').find_all('li')
                        except AttributeError:
                            images = [soup.find('div', class_='EZC25+__baseContainer')]
                        urls = []
                        try:
                            url = soup.find('div', class_='ZPYEqa__dnc__image').find('img').get('data-src')
                            urls.append(url.replace(url.split('w_')[1].split(',')[0], '5000'))
                        except AttributeError:
                            pass
                        for image in images:
                            image_url = image.find('img')
                            url = image_url.get('srcset')
                            if url == None:
                                url = image_url.get('data-src')
                            else:
                                url = url.split()[-2]
                            urls.append(url.replace(url.split('w_')[1].split(',')[0], '5000'))
                        for k, url in enumerate(set(urls)):
                            r = http.get(url, headers={'user-agent': head})
                            with open(f'{path_variant}/image{k}.jpg', 'wb') as f:
                                f.write(r.content)
                        if variants != None:
                            for variant in variants:
                                url = main_url + variant.get('url')
                                path_extra = url.split(f'{main_name}?')[-1]
                                if len(path_extra) == 0:
                                    path_extra = f'default'
                                path_variant = f'{path_product}/{path_extra}'
                                try:
                                    os.mkdir(path_variant)
                                except:
                                    continue
                                r = http.get(url, headers={'user-agent': head})
                                soup = BeautifulSoup(r.text, 'lxml')
                                try:
                                    images = soup.find('ul', class_='slick-dots').find_all('li')
                                except AttributeError:
                                    images = [soup.find('div', class_='EZC25+__baseContainer')]
                                urls = []
                                try:
                                    url = soup.find('div', class_='ZPYEqa__dnc__image').find('img').get('data-src')
                                    urls.append(url.replace(url.split('w_')[1].split(',')[0], '5000'))
                                except AttributeError:
                                    pass
                                for image in images:
                                    image_url = image.find('img')
                                    url = image_url.get('srcset')
                                    if url == None:
                                        url = image_url.get('data-src')
                                    else:
                                        url = url.split()[-2]
                                    urls.append(url.replace(url.split('w_')[1].split(',')[0], '5000'))
                                for k, url in enumerate(set(urls)):
                                    r = http.get(url, headers={'user-agent': head})
                                    with open(f'{path_variant}/image{k}.jpg', 'wb') as f:
                                        f.write(r.content)


def main():
    while True:
        collect_data('https://www.castlery.com/us')
        print('FILE HAS CREATED!')


if __name__ == '__main__':
    main()

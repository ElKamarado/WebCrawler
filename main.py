import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os

all_links = set()
all_search = set()
qnt = 0
qnt2 = 0
def get_all_links():
    global all_links, qnt
    url = input("Введите URL-адрес: ")
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(f"ER: Не удалось получить доступ к сайту: {e}")
        return set()
    if response.status_code != 200:
        print(f"ER: Проверка сайта не удалась: {url}")
        return set()
    page_content = response.content
    charset = response.encoding
    if charset is None:
        print("ER: Не удалось определить кодировку страницы")
        return set()
    if charset.lower() != 'utf-8':
        try:
            page_content = page_content.decode(charset).encode('utf-8')
        except UnicodeDecodeError:
            print(f"ER: Не удалось преобразовать содержимое страницы из кодировки {charset} в utf-8\n")
            print(f"ER: Пробую преобразовать в windows-1251")
            try:
                page_content = page_content.decode('windows-1251').encode('utf-8')
            except UnicodeDecodeError:
                print(f"ER: Не удалось преобразовать содержимое страницы из кодировки {charset} в windows-1251")
                return set()
    if os.path.isfile('links.txt'):
        print("Файл links.txt уже существует.")
        choice = input("Выберите вариант: (r) перезаписать, (a) дополнить, (q) выйти из программы: ")
        while choice not in ('r', 'a', 'q'):
            choice = input("Выберите вариант: (r) перезаписать, (a) дополнить, (q) выйти из программы: ")
        if choice == 'r':
            mode = 'w'
        elif choice == 'a':
            mode = 'a'
        else:
            return set()
    else:
        mode = 'w'
    with open('links.txt', mode) as f:
        f.write(url + '\n')
    soup = BeautifulSoup(page_content, 'html.parser')
    links = soup.find_all('a')
    all_links = set()
    seen_links = set()
    for link in links:
        href = link.get('href')
        if href in seen_links:
            continue
        seen_links.add(href)
        for link in links:
            href = link.get('href')
            if href is not None and not href.startswith(('http://', 'https://')):
                href = urlparse(url).scheme + '://' + urlparse(url).netloc + href
            if href not in seen_links:
                all_links.add(href)
                seen_links.add(href)
                qnt += 1
        base_url = urlparse(url).hostname
        link_url = urlparse(href).hostname
        if link_url != base_url:
            continue
        all_links.add(href)
    return mode
mode = get_all_links()
print(f'Ссылки успешно найденны: {qnt - 1}')
with open('links.txt', mode) as f:
    for link in all_links:
        if link is not None:
            f.write(link + '\n')
def get_text_from_links():
    global qnt2
    itr = 0
    search_text = input("Введите запрос: ")
    with open('links.txt', 'r') as f:
        links = f.readlines()
    all_search = set()
    for good_link in links:
        itr += 1
        good_link = good_link.strip()
        if not good_link.startswith(('http://', 'https://')):
            continue
        try:
            response = requests.get(good_link)
        except (requests.exceptions.HTTPError, requests.exceptions.RequestException, ValueError) as e:
            print(f"{itr} ER: {e} {good_link}")
            continue
        if response.status_code == 200:
            html = response.content
        else:
            print(f"{itr} ER: Не удалось получить HTML контент")
            continue
        try:
            html = html.decode('utf-8')
        except UnicodeDecodeError:
            html = html.decode('windows-1251', errors='ignore')
        if search_text in html:
            print(f'{itr} Текст найден на странице {good_link}')
            all_search.add(good_link)
    qnt2 = len(all_search)
    return all_search
all_search = get_text_from_links()
print(f"Поиск выполнен, текст найден: {qnt2}")
with open('search.txt', 'w') as f:
    for search in all_search:
        if search is not None:
            f.write(search + '\n')
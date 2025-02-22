import phonenumbers
from phonenumbers import geocoder, carrier, number_type
import requests
import re
import os

# База операторов и регионов (можно дополнять)
OPERATOR_REGIONS = {
    "911": "Санкт-Петербург и Ленинградская область",
    "495": "Москва",
    "499": "Москва",
    "812": "Санкт-Петербург",
    "343": "Екатеринбург",
    "846": "Самара",
    "861": "Краснодар",
    "863": "Ростов-на-Дону",
}

KNOWN_NUMBERS = {
    "+74956630920": "Сбербанк",
    "+78005553535": "Тинькофф Банк",
    "+74957888888": "Аэрофлот",
}

def get_phone_info(phone_number):
    """Определяет информацию по номеру телефона"""
    try:
        parsed_number = phonenumbers.parse(phone_number, "RU")
        region = geocoder.description_for_number(parsed_number, "ru")
        operator = carrier.name_for_number(parsed_number, "ru")
        num_type = number_type(parsed_number)

        type_str = "Мобильный" if num_type == phonenumbers.PhoneNumberType.MOBILE else "Стационарный"

        number_str = str(parsed_number.national_number)
        operator_code = number_str[:3]
        approximate_location = OPERATOR_REGIONS.get(operator_code, "Неизвестный регион")

        known_info = KNOWN_NUMBERS.get(phone_number, "Неизвестно")

        return f"""
 [+] Номер: {phone_number}
 [+] Регион: {region}
 [+] Оператор: {operator}
 [+] Тип номера: {type_str}
 [+] Примерное местоположение: {approximate_location}
 [+] Чей номер: {known_info}
"""
    except Exception as e:
        return f"Ошибка при обработке номера: {e}"

def get_ip_info(ip):
    """Определяет полную информацию по IP"""
    url = f"http://ip-api.com/json/{ip}?fields=status,message,query,country,regionName,city,lat,lon,isp,org,timezone,zip"
    response = requests.get(url).json()
    
    if response.get("status") == "fail":
        return "Не удалось получить данные. Возможно, IP некорректен."

    return f"""
[+] IP: {response['query']}
[+] Страна: {response['country']}
[+] Город: {response['city']}
[+] Провайдер: {response['isp']}
[+] Организация: {response.get('org', 'Неизвестно')}
[+] Часовой пояс: {response['timezone']}
[+] Почтовый индекс: {response.get('zip', 'Неизвестно')}
[+] Координаты: {response['lat']}, {response['lon']}
"""

def search_fio(full_name):
    """Ищет ФИО в файлах папки bd"""
    directory = "bd"
    results = []
    
    if not os.path.exists(directory):
        return "Папка 'bd' не найдена!"
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        if os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    for line in file:
                        if full_name.lower() in line.lower():
                            results.append(f"Найдено в {filename}: {line.strip()}")
            except Exception as e:
                return f"Ошибка при чтении {filename}: {e}"
    
    return "\n".join(results) if results else "ФИО не найдено в базе!"

def search_vk(user_id):
    """Поиск информации о пользователе ВКонтакте"""
    url = f"https://api.vk.com/method/users.get?user_ids={user_id}&fields=city,domain&access_token=YOUR_ACCESS_TOKEN&v=5.131"
    response = requests.get(url).json()
    
    if "response" in response:
        user = response["response"][0]
        return f"""
[+] ID: {user['id']}
[+] Имя: {user['first_name']} {user['last_name']}
[+] Город: {user.get('city', {}).get('title', 'Неизвестно')}
[+] Профиль: https://vk.com/{user['domain']}
"""
    else:
        return "Ошибка при получении данных ВКонтакте!"

def search_card(card_number):
    """Поиск информации по номеру банковской карты"""
    url = f"https://lookup.binlist.net/{card_number[:6]}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return "Ошибка: сервер binlist.net недоступен или вернул ошибку"
        
        data = response.json()
        return f"""
[+] Номер карты: {card_number}
[+] Банк: {data.get('bank', {}).get('name', 'Неизвестно')}
[+] Страна: {data.get('country', {}).get('name', 'Неизвестно')}
[+] Тип карты: {data.get('type', 'Неизвестно')}
[+] Уровень карты: {data.get('brand', 'Неизвестно')}
[+] Валюта: {data.get('country', {}).get('currency', 'Неизвестно')}
[+] 3D Secure: {data.get('prepaid', 'Неизвестно')}
[+] Сайт банка: {data.get('bank', {}).get('url', 'Неизвестно')}
[+] Телефон банка: {data.get('bank', {}).get('phone', 'Неизвестно')}
[+] Категория карты: {data.get('scheme', 'Неизвестно')}
"""
    except requests.exceptions.RequestException as e:
        return f"Ошибка сети: {e}"
    except Exception as e:
        return f"Ошибка при обработке данных: {e}"

def main():
    while True:
        print("\n Выберите действие:")
        print("1. Пробить номер телефона")
        print("2. Пробить IP-адрес")
        print("4. Найти информацию по VK")
        print("5. Найти информацию по банковской карте")
        print("6. Выйти")
        
        choice = input("Введите номер действия (1-6): ")
        
        if choice == "1":
            phone = input("Введите номер в формате +7XXXXXXXXXX: ")
            print(get_phone_info(phone))
        elif choice == "2":
            ip = input("Введите IP-адрес: ")
            print(get_ip_info(ip))
        elif choice == "3":
            full_name = input("Введите ФИО для поиска: ")
            print(search_fio(full_name))
        elif choice == "4":
            vk_id = input("Введите ID или короткое имя пользователя VK: ")
            print(search_vk(vk_id))
        elif choice == "5":
            card_number = input("Введите номер банковской карты: ")
            print(search_card(card_number))
        elif choice == "6":
            print(" Выход...")
            break
        else:
            print(" Неверный ввод! Попробуйте снова.")

if __name__ == "__main__":
    main()

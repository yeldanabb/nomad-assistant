"""
Демо скрипт для парсинга законов с adilet.zan.kz, в реальной системе можно было бы запускать для обновления базы знаний.
"""
import requests
from bs4 import BeautifulSoup

url = "https://adilet.zan.kz/rus/docs/Z970000042_"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
text = soup.get_text()
with open("data/laws/adilet_insurance.txt", "w", encoding="utf-8") as f:
    f.write(text)
print("Скачано и сохранено")
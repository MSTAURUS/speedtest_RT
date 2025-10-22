# speedtest_RT
CLI измерения скорости на speedtest.rt.ru

Установка:

Установите зависимости:

~~~bash
pip install -r requirements.txt
~~~

Установите ChromeDriver:

    Скачайте ChromeDriver с https://chromedriver.chromium.org/

  Или установите через менеджер пакетов:

~~~bash

# На Windows (с помощью chocolatey)
choco install chromedriver

# На macOS (с помощью homebrew)
brew install chromedriver

# На Linux
sudo apt-get install chromium-chromedriver
~~~

Запуск:

```
python speedtest.py <OPTION>
```

  -d, --debug - вывод на экран всех запросов
  
  -t, --timeout - установка повторных запросов, по-умолчанию = 0 (один запрос)

  <img width="537" height="356" alt="image" src="https://github.com/user-attachments/assets/14aa8d23-b830-4fc6-b96f-891bcad70ca0" />


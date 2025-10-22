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

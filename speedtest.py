import argparse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import gc
import psutil


class SpeedTestRT:
    def __init__(self, debug=True):
        self.test_start_time = None
        self.driver = None
        self.debug = debug
        self.setup_driver()

    def setup_driver(self):
        """Настройка браузера"""
        chrome_options = Options()
        # Включаем headless-режим
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            print(f"❌ Ошибка запуска Chrome: {e}")
            return False
        return True

    def log(self, message):
        """Логирование сообщений только в режиме отладки"""
        if self.debug:
            print(message)

    def run_test(self):
        """Запуск теста скорости"""
        self.test_start_time = datetime.now()
        self.log("🚀 Запускаем тест скорости Ростелеком...")

        try:
            # Открываем сайт
            self.driver.get("https://speedtest.rt.ru/")
            time.sleep(5)

            stop_buttons = ["//*[contains(text(), 'Прервать')]"]

            button_found = False
            for xpath in stop_buttons:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )

                    self.log("✅ Кнопка отмены теста найдена")
                    button_found = True
                    break
                except:
                    continue

            # Ждем и собираем результаты
            if button_found:
                return self.wait_for_results()

            return None

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None

    def wait_for_results(self):
        """Ожидание результатов теста"""
        self.log("⏳ Измеряем скорость...")

        results = {'download': None, 'upload': None, 'ping': None, 'jitter': None}
        max_wait = 180  # Максимум 3 минуты
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                # Ищем пинг в блоке latency-wrapper
                ping_elements = self.driver.find_elements(By.CSS_SELECTOR, ".latency-wrapper__value")
                if ping_elements:
                    try:
                        results['ping'] = int(ping_elements[0].text)
                        self.log(f"📡 Пинг: {results['ping']} мс")
                    except ValueError:
                        pass

                # Ищем скорости в блоке indicator__text
                speed_elements = self.driver.find_elements(By.CSS_SELECTOR, ".indicator__text")
                speed_values = []

                for element in speed_elements:
                    try:
                        speed = float(element.text.strip())
                        speed_values.append(speed)
                    except ValueError:
                        continue

                # Определяем какие скорости, что означают
                if speed_values:
                    # Первое значение - Загрузка (download)
                    results['download'] = speed_values[0]
                    self.log(f"⬇️  Загрузка: {results['download']} Мбит/с")

                    # Второе значение - Отдача (upload)
                    if len(speed_values) > 1:
                        results['upload'] = speed_values[1]
                        self.log(f"⬆️  Отдача: {results['upload']} Мбит/с")

                    # Третье значение - Джиттер
                    if len(speed_values) > 2:
                        results['jitter'] = speed_values[2]
                        self.log(f"📊 Джиттер: {results['jitter']} мс")

                # Проверяем, завершен ли тест (все значения заполнены)
                if all(results.values()):
                    self.log("✅ Тест завершен")
                    return results

                # Альтернативная проверка завершения теста
                progress_bars = self.driver.find_elements(By.CSS_SELECTOR, ".indicator__progress span")
                if progress_bars and all(
                        "transform: translateX(0%)" in bar.get_attribute("style") for bar in progress_bars):
                    self.log("✅ Прогресс-бары завершены")
                    return results

                time.sleep(2)

            except Exception as e:
                self.log(f"⚠️ Ошибка при ожидании результатов: {e}")
                time.sleep(2)

        self.log("⏰ Время ожидания истекло, возвращаем доступные результаты")
        return results

    def save_to_file(self, results, filename="speedtest_results.txt"):
        """Сохранение результатов в файл"""
        try:
            # Форматируем дату и время
            start_time_str = self.test_start_time.strftime("%d.%m.%Y %H:%M:%S")

            # Подготавливаем строку для записи
            result_line = (
                f"{start_time_str} | "
                f"Загрузка: {results['download'] or 'N/A'} Мбит/с | "
                f"Отдача: {results['upload'] or 'N/A'} Мбит/с | "
                f"Пинг: {results['ping'] or 'N/A'} мс | "
                f"Джиттер: {results['jitter'] or 'N/A'} ms\n"
            )

            # Записываем в конец файла
            with open(filename, "a", encoding="utf-8") as f:
                f.write(result_line)

            self.log(f"💾 Результаты сохранены в файл: {filename}")
            return True

        except Exception as e:
            print(f"❌ Ошибка при сохранении в файл: {e}")
            return False

    def display_results(self, results):
        """Отображение результатов"""
        # Форматируем дату и время запуска теста
        start_time_str = self.test_start_time.strftime("%d.%m.%Y %H:%M:%S")

        print("\n" + "=" * 50)
        print(f"📊 РЕЗУЛЬТАТЫ ТЕСТА СКОРОСТИ ({start_time_str})")
        print("=" * 50)

        if results['download'] is not None:
            print(f"⬇️  Загрузка: {results['download']} Мбит/с")
        else:
            print("⬇️  Загрузка: не измерено")

        if results['upload'] is not None:
            print(f"⬆️  Отдача: {results['upload']} Мбит/с")
        else:
            print("⬆️  Отдача: не измерено")

        if results['ping'] is not None:
            print(f"📡 Пинг: {results['ping']} мс")
        else:
            print("📡 Пинг: не измерен")

        if results['jitter'] is not None:
            print(f"📊 Джиттер: {results['jitter']} ms")
        else:
            print("📊 Джиттер: не измерен")

        print("=" * 50)

        # Сохраняем результаты в файл
        self.save_to_file(results)

    def cleanup(self):
        """Очистка ресурсов"""
        self.log("🧹 Выполняем очистку ресурсов...")

        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self.log("✅ Браузер закрыт")
            except Exception as e:
                self.log(f"⚠️ Ошибка при закрытии браузера: {e}")

        # Принудительный сбор мусора
        gc.collect()
        self.log("✅ Сборка мусора выполнена")

        # Очистка процессов Chrome
        self.kill_chrome_processes()

    def kill_chrome_processes(self):
        """Убивает процессы Chrome"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'chrome' in proc.info['name'].lower():
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            self.log("✅ Процессы Chrome завершены")
        except Exception as e:
            self.log(f"⚠️ Ошибка при завершении процессов Chrome: {e}")


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description='Тестер скорости Ростелеком')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Включить режим отладки')
    parser.add_argument('-t', '--timeout', type=int, default=0,
                        help='Таймаут между проверками в минутах (по умолчанию: 0)')

    return parser.parse_args()

def main():
    """Основная функция"""
    print("🌐 Тестер скорости Ростелеком")

    # Парсим аргументы командной строки
    args = parse_arguments()

    debug_mode = args.debug
    timeout_minutes = args.timeout
    run_count = 0


    print(f"⏰ Таймаут между проверками: {timeout_minutes} минут")
    print("🔄 Запускаем периодическую проверку...")
    print("Для остановки нажмите Ctrl+C\n")

    try:
        while True:
            run_count += 1
            current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            print(f"\n🌀 Запуск #{run_count} - {current_time}")

            # Создаем новый экземпляр для каждого теста
            test = SpeedTestRT(debug=debug_mode)

            if not test.driver:
                print("❌ Не удалось запустить браузер")
                break

            try:
                results = test.run_test()
                if results:
                    test.display_results(results)
                else:
                    print("❌ Не удалось выполнить тест")
            except Exception as e:
                print(f"❌ Ошибка при выполнении теста: {e}")
            finally:
                # Всегда выполняем очистку
                test.cleanup()
                del test
                gc.collect()

            # Ожидание до следующего запуска
            if debug_mode:
                print(f"\n⏳ Ожидание {timeout_minutes} минут до следующей проверки...")

            if timeout_minutes == 0:
                break

            # Ожидание с возможностью прерывания
            for i in range(timeout_minutes * 60):
                time.sleep(1)
                # Каждую минуту выводим прогресс в режиме отладки
                if debug_mode and i % 60 == 0 and i > 0:
                    minutes_passed = i // 60
                    print(f"⏰ Прошло {minutes_passed} минут...")

    except KeyboardInterrupt:
        print("\n\n⏹️  Программа остановлена пользователем")
        print(f"📊 Всего выполнено проверок: {run_count}")
        print("👋 До свидания!")


if __name__ == "__main__":
    main()

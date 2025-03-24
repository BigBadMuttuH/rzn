import requests
import pandas as pd

API_URL = "https://roszdravnadzor.gov.ru/ajax/services/misearch"
SEARCH_URL = "https://roszdravnadzor.gov.ru/services/misearch"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
    "Referer": "https://roszdravnadzor.gov.ru/services/misearch",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://roszdravnadzor.gov.ru",
}


def get_medical_data(query):
    """Получает данные по медицинскому изделию, эмулируя браузер."""

    session = requests.Session()
    session.get(SEARCH_URL, headers=HEADERS)  # Получаем cookies

    data = {
        "q_mi_label_application": query,
        "draw": "1",
        "start": "0",
        "length": "10",
    }

    response = session.post(API_URL, data=data, headers=HEADERS)

    if response.status_code != 200:
        print(f"⚠ Ошибка {response.status_code} для {query}")
        return None

    try:
        json_data = response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"⚠ Ошибка декодирования JSON для {query}")
        return None

    if not json_data.get("data"):
        print(f"⚠ Нет данных по запросу {query}")
        return None

    records = json_data["data"]
    parsed_data = []

    for record in records:
        parsed_data.append({
            "Запрос": query,
            "Уникальный номер": record.get("col1", {}).get("label", ""),
            "Рег. номер": record.get("col2", {}).get("label", ""),
            "Дата регистрации": record.get("col3", {}).get("label", ""),
            "Срок действия": record.get("col4", {}).get("label", ""),
            "Наименование": record.get("col5", {}).get("title", ""),
            "Заявитель": record.get("col6", {}).get("label", ""),
            "Держатель регистрационного удостоверения": record.get("col7", {}).get("title", ""),
            "Юридический адрес держателя": record.get("col8", {}).get("title", ""),
            "Производитель": record.get("col9", {}).get("label", ""),
            "Адрес места производства": record.get("col10", {}).get("title", ""),
            "Адрес места деятельности (производства)": record.get("col11", {}).get("title", ""),
            "Код вида номенклатурной классификации медицинских изделий": record.get("col12", {}).get("label", ""),
            "Класс потенциального риска применения": record.get("col13", {}).get("label", ""),
            "Вид медицинского изделия в соответствии с номенклатурной классификацией": record.get("col14", {}).get(
                "label", ""),
            "Номер регистрационного удостоверения медизделия (РУ)": record.get("col15", {}).get("label", ""),
            "Наименование организации-производителя": record.get("col16", {}).get("title", ""),
            "Адрес организации-производителя": record.get("col17", {}).get("label", ""),
            "PDF": record.get("col18", {}).get("label", ""),
        })

    return parsed_data


def process_csv(input_file, output_file):
    """Читает CSV-файл с номерами РУ и сохраняет результаты."""

    df = pd.read_csv(input_file)
    queries = df["Рег_номер"].astype(str).tolist()  # Берём колонку с номерами

    all_results = []

    for query in queries:
        print(f"🔍 Обрабатываю: {query}")
        data = get_medical_data(query)
        if data:
            all_results.extend(data)

    if all_results:
        result_df = pd.DataFrame(all_results)
        result_df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"✅ Данные сохранены в {output_file}")
    else:
        print("⚠ Нет данных для сохранения!")


# 📌 Параметры
INPUT_CSV = "queries.csv"  # Файл с номерами для поиска
OUTPUT_CSV = "medical_data.csv"  # Куда сохранять результат

# 🏁 Запуск
process_csv(INPUT_CSV, OUTPUT_CSV)

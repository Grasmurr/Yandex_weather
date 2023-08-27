import requests
import datetime
import pandas as pd

API_KEY = "797bc70d-5a99-4130-a448-c40fd9abb912"
BASE_URL = "https://api.weather.yandex.ru/v2/forecast"

CITY_COORDINATES = {
    "москва": [55.75396, 37.620393],
    "санкт-петербург": [59.939095, 30.315868]
}

DAYS_OF_WEEK = {
    "пн": 0,
    "вт": 1,
    "ср": 2,
    "чт": 3,
    "пт": 4,
    "сб": 5,
    "вс": 6
}


def get_user_input(prompt, valid_inputs):
    user_input = ""
    while user_input not in valid_inputs:
        user_input = input(prompt).lower()
    return user_input



def get_weather_forecast(city, day, part):
    params = {
        "lat": CITY_COORDINATES[city][0],
        "lon": CITY_COORDINATES[city][1],
        "lang": "ru_RU",
        'limit': 7,
    }

    headers = {
        "X-Yandex-API-Key": API_KEY
    }

    response = requests.get(BASE_URL, params=params, headers=headers)
    print(response)
    response.raise_for_status()

    if response.status_code == 200:
        forecast = response.json()
    else:
        print(f"Ошибка при выполнении запроса: {response.content}")
        return None
    forecast_dict = {}
    for day_forecast in forecast['forecasts']:
        forecast_date = datetime.datetime.strptime(day_forecast['date'], "%Y-%m-%d").date()
        forecast_data = {
            'morning': day_forecast['parts']['morning']['temp_avg'],
            'day': day_forecast['parts']['day']['temp_avg'],
            'evening': day_forecast['parts']['evening']['temp_avg'],
            'night': day_forecast['parts']['night']['temp_avg']
        }

        forecast_dict[forecast_date] = forecast_data
        if forecast_date == day:
            if part == 'утро':
                part_forecast = day_forecast['parts']['morning']
            elif part == 'день':
                part_forecast = day_forecast['parts']['day']
            elif part == 'вечер':
                part_forecast = day_forecast['parts']['evening']
            elif part == 'ночь':
                part_forecast = day_forecast['parts']['night']

    df = pd.DataFrame.from_dict(forecast_dict, orient='index', columns=['morning', 'day', 'evening', 'night'])
    df.index.name = 'Date'
    df.to_csv('forecast.csv', index=True)

    forecast_str = f"Прогноз на {part} {day}:\n"
    forecast_str += f"Температура: мин {part_forecast['temp_min']}, " \
                    f"средняя {part_forecast['temp_avg']}, макс {part_forecast['temp_max']}\n"
    forecast_str += f"Давление: {part_forecast['pressure_mm']} мм рт. ст., " \
                    f"{part_forecast['pressure_pa']} Па\n"

    return forecast_str


def main():
    print("Добро пожаловать в программу прогноза погоды!")
    print("Программа использует данные Яндекс.Погоды и позволяет получить "
          "прогноз на выбранный день недели и время суток.")

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    print(f"Обратите внимание, что наша программа может выдавать результаты только "
          f"на неделю вперед. "
          f"\nНапример, если сегодня {today.strftime('%A')}, "
          f"то вы сможете посмотреть прогноз вплоть до {yesterday.strftime('%A')}")

    city = get_user_input(prompt="Для какого города вы хотите узнать прогноз погоды? "
                          "(москва/санкт-петербург): ", valid_inputs=CITY_COORDINATES.keys())
    day_of_week = get_user_input("На какой день недели вы хотите узнать прогноз погоды? "
                                 "(пн/вт/ср/чт/пт/сб/вс): ", DAYS_OF_WEEK.keys())
    part_of_day = get_user_input("На какую часть дня вы хотите узнать прогноз погоды?"
                                 " (утро/день/вечер/ночь): ", ['утро', 'день', 'вечер', 'ночь'])

    day = today + datetime.timedelta(days=(DAYS_OF_WEEK[day_of_week] - today.weekday() + 7) % 7)

    try:
        forecast = get_weather_forecast(city, day, part_of_day)
        print(forecast)
    except Exception as E:
        print(f'Прогноз погоды недоступен, причина: {E}')


main()


df = pd.read_csv('forecast.csv', index_col='Date')  # Загрузка CSV файла в DataFrame
average_temps = df.mean()
print('Cредние температуры за каждый день по частям дня:')
print(average_temps)

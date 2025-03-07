import requests

city_code = '101210404'

r = requests.get(
    f"http://t.weather.itboy.net/api/weather/city/{city_code}"
)

result2 = r.text

print(result2)

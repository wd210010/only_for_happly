
import requests, json

# 城市code 自己城市的code https://fastly.jsdelivr.net/gh/Oreomeow/checkinpanel@master/city.json 这个网址查看
city_code = '101210404'



r = requests.get(
    f"http://t.weather.itboy.net/api/weather/city/{city_code}"
)
d = json.loads(r.text)
result2 = json.loads(r.text)['cityInfo']

#参数更新 删除parent
msg = (
    f' 城市：{d["cityInfo"]["city"]}\n'
    f' 日期：{d["data"]["forecast"][0]["ymd"]} {d["data"]["forecast"][0]["week"]}\n'
    f' 天气：{d["data"]["forecast"][0]["type"]}\n'
    f' 温度：{d["data"]["forecast"][0]["high"]} {d["data"]["forecast"][0]["low"]}\n'
    f' 湿度：{d["data"]["shidu"]}\n'
    f' 空气质量：{d["data"]["quality"]}\n'
    f' PM2.5：{d["data"]["pm25"]}\n'
    f' PM10：{d["data"]["pm10"]}\n'
    f' 风力风向 {d["data"]["forecast"][0]["fx"]} {d["data"]["forecast"][0]["fl"]}\n'
    f' 感冒指数：{d["data"]["ganmao"]}\n'
    f' 温馨提示：{d["data"]["forecast"][0]["notice"]}\n'
    f' 更新时间：{d["time"]}'
)
print(msg)

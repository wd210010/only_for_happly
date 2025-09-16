import requests
import random
import os
import json
from collections import Counter
from notification import Push

# --- Constants ---
MAX_RED_BALL = 33
MAX_BLUE_BALL = 16
NUM_LOW_FREQ_RED_CANDIDATES = 10
NUM_LOW_FREQ_BLUE_CANDIDATES = 5
NUM_SELECTED_RED_BALLS = 6
NUM_SELECTED_BLUE_BALLS = 1
NUM_GENERATED_LOTTERIES = 2

API_URL = 'https://ms.zhcw.com/proxy/lottery-chart-center/history/SSQ'

def get_lottery_history():
    """获取双色球历史数据"""
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
    }
    data = {
        "limit": 200,
        "page": 1,
        "params": {}
    }

    try:
        resp = requests.post(API_URL, headers=headers, data=json.dumps(data))
        resp.raise_for_status()  # 检查HTTP状态码，如果不是200，则抛出异常
        json_data = resp.json()
        history_data = json_data.get('datas')

        if history_data is None:
            print("API响应中缺少 'datas' 键。")
            return None, None

        red_ball_history = []
        blue_ball_history = []
        for entry in history_data:
            red_ball_history.append(entry['winningFrontNum'].split(' '))
            blue_ball_history.append(entry['winningBackNum'])
        return red_ball_history, blue_ball_history

    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {e}")
        return None, None
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return None, None
    except KeyError as e:
        print(f"API响应缺少关键字段: {e}")
        return None, None

def find_all_indices(lst, target):
    """查找列表中所有目标值的索引"""
    indices = []
    for i, value in enumerate(lst):
        if value == target:
            indices.append(i)
    return indices

def generate_lottery_numbers(red_ball_history, blue_ball_history):
    """根据历史数据生成双色球号码"""
    # 统计红球出现次数
    all_red_balls_flat = [int(num) for sublist in red_ball_history for num in sublist]
    red_ball_counts = Counter(all_red_balls_flat)

    # 统计蓝球出现次数
    blue_ball_counts = Counter([int(num) for num in blue_ball_history])

    # 获取出现次数最少的红球号码作为候选
    sorted_red_counts = sorted(red_ball_counts.items(), key=lambda item: item[1])
    candidate_red_balls = []
    for i in range(min(NUM_LOW_FREQ_RED_CANDIDATES, len(sorted_red_counts))):
        candidate_red_balls.append(sorted_red_counts[i][0])
    # 确保候选红球数量足够，如果不够则补充
    if len(candidate_red_balls) < NUM_SELECTED_RED_BALLS:
        # 从所有红球中随机补充
        remaining_red_balls = list(set(range(1, MAX_RED_BALL + 1)) - set(candidate_red_balls))
        candidate_red_balls.extend(random.sample(remaining_red_balls, NUM_SELECTED_RED_BALLS - len(candidate_red_balls)))

    # 获取出现次数最少的蓝球号码作为候选
    sorted_blue_counts = sorted(blue_ball_counts.items(), key=lambda item: item[1])
    candidate_blue_balls = []
    for i in range(min(NUM_LOW_FREQ_BLUE_CANDIDATES, len(sorted_blue_counts))):
        candidate_blue_balls.append(sorted_blue_counts[i][0])
    # 确保候选蓝球数量足够，如果不够则补充
    if len(candidate_blue_balls) < NUM_SELECTED_BLUE_BALLS:
        # 从所有蓝球中随机补充
        remaining_blue_balls = list(set(range(1, MAX_BLUE_BALL + 1)) - set(candidate_blue_balls))
        candidate_blue_balls.extend(random.sample(remaining_blue_balls, NUM_SELECTED_BLUE_BALLS - len(candidate_blue_balls)))

    selected_red_balls = sorted(random.sample(list(set(candidate_red_balls)), NUM_SELECTED_RED_BALLS))
    selected_blue_ball = sorted(random.sample(list(set(candidate_blue_balls)), NUM_SELECTED_BLUE_BALLS))[0]

    return selected_red_balls, selected_blue_ball

def main():
    red_history, blue_history = get_lottery_history()
    if not red_history or not blue_history:
        print("未能获取历史数据，退出。")
        return

    messages = []
    print(f"为你生成{NUM_GENERATED_LOTTERIES}注双色球号码如下")
    for _ in range(NUM_GENERATED_LOTTERIES):
        red_balls, blue_ball = generate_lottery_numbers(red_history, blue_history)
        messages.append(f"{red_balls} - {blue_ball}")

    formatted_message = "\n".join(messages)
    print(formatted_message)
    Push(title='双色球2注', contents=formatted_message)

if __name__ == '__main__':
    main()



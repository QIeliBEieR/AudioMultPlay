import sounddevice as sd
import json

# 定义需要排除的关键词
exclude_keywords = [
    "Microsoft Sound Mapper",
    "主声音驱动程序",
    "SST",
    "High Definition Audio",
    "Output",
    "Hands-Free AG Audio",
    "房间扬声器 ()",
    "耳机 ()",
]

# 列出所有音频设备
devices = sd.query_devices()

# 筛选出所有可播放的设备，并排除特定关键词的设备
output_devices = [
    (i, d['name'])
    for i, d in enumerate(devices)
    if d['max_output_channels'] > 0
    and not any(keyword in d['name'] for keyword in exclude_keywords)
]

# 使用集合去除重复设备（只保留第一个出现的设备）
seen = set()
unique_devices = []
for index, name in output_devices:
    if name not in seen:
        seen.add(name)
        unique_devices.append((index, name))

# 保存设备信息到 JSON 文件，供 MultPlay.py 使用
with open("devices.json", "w", encoding="utf-8") as f:
    json.dump(unique_devices, f, ensure_ascii=False, indent=4)

print("可播放的音频设备已保存到 devices.json")

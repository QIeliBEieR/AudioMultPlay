import json
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import time
import pandas as pd

# 文件路径
DEVICES_JSON = "devices.json"
LATENCY_XLSX = "delay.xlsx"
# AUDIO_FILE = "在这座城市遗失了你 - 李佳薇 .wav"
AUDIO_FILE = "W.mp3"


# 读取设备列表
def load_devices():
    """ 从 devices.json 读取设备索引和名称 """
    try:
        with open(DEVICES_JSON, "r", encoding="utf-8") as f:
            devices = json.load(f)
        if not isinstance(devices, list) or not devices:
            raise ValueError("设备列表为空或格式不正确")
        return {device[0]: device[1] for device in devices if isinstance(device, list) and len(device) == 2}
    except Exception as e:
        print(f"⚠️ 读取设备列表失败: {e}")
        return {}


# 读取设备延迟时间
def load_latency():
    """ 从 Excel 读取设备索引和相对输出延迟时间 """
    try:
        df = pd.read_excel(LATENCY_XLSX)
        if "设备索引" not in df.columns or "相对输出延迟 (秒)" not in df.columns:
            raise ValueError("Excel 文件格式错误，缺少必要列")
        return {int(row["设备索引"]): row["相对输出延迟 (秒)"] for _, row in df.iterrows()}
    except Exception as e:
        print(f"⚠️ 读取设备延迟时间失败: {e}")
        return {}


# 读取主音频文件
def load_audio(filename):
    """ 读取音频文件，并处理通道信息 """
    try:
        data, samplerate = sf.read(filename, dtype="float32")
        if len(data.shape) == 1:
            data = np.column_stack((data, data))  # 单通道转双通道
        return data, samplerate
    except Exception as e:
        print(f"❌ 读取音频文件失败: {e}")
        return None, None


# 在指定设备播放音频
def play_audio_on_device(device_index, device_name, audio_data, samplerate, delay):
    """ 在指定设备播放音频，并控制同步 """
    if delay > 0:
        print(f"⏳ 设备 {device_index} {device_name} 等待 {delay:.3f} 秒后播放...")
        time.sleep(delay)
    else:
        print(f"▶ 设备 {device_index} {device_name} 立即播放...")

    try:
        with sd.OutputStream(device=device_index, samplerate=samplerate, channels=2) as stream:
            stream.write(audio_data)
        print(f"✅ 设备 {device_index} {device_name} 播放完成")
    except Exception as e:
        print(f"⚠️ 设备 {device_index} {device_name} 播放失败: {e}")


# 主程序
def main():
    devices = load_devices()
    if not devices:
        print("⚠️ 没有找到可用的设备，程序终止")
        return

    latency_data = load_latency()

    audio_data, samplerate = load_audio(AUDIO_FILE)
    if audio_data is None:
        return

    print("\n🎵 开始播放音频...")
    threads = []
    for device_index, device_name in devices.items():
        delay = latency_data.get(device_index, 0)
        thread = threading.Thread(target=play_audio_on_device,
                                  args=(device_index, device_name, audio_data, samplerate, delay))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("\n🎶 所有设备同步播放完成！")


if __name__ == "__main__":
    main()
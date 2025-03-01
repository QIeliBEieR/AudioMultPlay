import json
import time
import numpy as np
import sounddevice as sd
import soundfile as sf
import pandas as pd

DEVICE_CONFIG = "devices.json"  # 设备列表文件
TEST_WAV = "audio_test.wav"  # 测试音频文件
OUTPUT_EXCEL = "delay.xlsx"  # 导出的 Excel 文件


# 读取设备列表
def load_devices():
    """ 从 devices.json 读取设备列表 """
    try:
        with open(DEVICE_CONFIG, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("JSON 格式错误，应该是一个列表")

        devices = [(item[0], item[1]) for item in data if isinstance(item, list) and len(item) == 2]

        return devices
    except Exception as e:
        print(f"⚠️ 读取设备列表失败: {e}")
        return []


# 测试输出设备的延迟
def test_output_latency(device_index):
    """ 播放音频并测量输出设备的延迟 """
    try:
        data, samplerate = sf.read(TEST_WAV, dtype="int16")
        CHANNELS = data.shape[1] if len(data.shape) > 1 else 1

        start_time = None

        def callback(outdata, frames, time_info, status):
            nonlocal start_time
            if start_time is None:
                start_time = time.time()
            outdata[:] = np.zeros((frames, CHANNELS))  # 先填充静音，避免溢出

        # 播放音频
        with sd.OutputStream(device=device_index, samplerate=samplerate, channels=CHANNELS, callback=callback):
            print(f"🔊 测试设备 {device_index} 输出延迟...")
            sd.play(data, samplerate, device=device_index)
            sd.wait()

        latency = time.time() - start_time if start_time else None
        return latency
    except Exception as e:
        print(f"❌ 设备 {device_index} 输出测试失败: {e}")
        return None


# 运行延迟测试
def run_latency_tests():
    """ 读取设备列表并测试输出延迟 """
    devices = load_devices()
    if not devices:
        print("⚠️ 没有可用的音频设备！")
        return

    results = []
    max_latency = None

    for device_index, device_name in devices:
        # 测试输出延迟
        output_latency = test_output_latency(device_index)

        # 设定最大延迟
        if output_latency is not None:
            if max_latency is None or output_latency > max_latency:
                max_latency = output_latency

        results.append([
            device_index,
            device_name,
            output_latency
        ])

        print(
            f"🎧 {device_name} 输出延迟: {output_latency:.6f} 秒" if output_latency is not None else f"🎧 {device_name} 输出测试失败")

    # 计算相对延迟
    for result in results:
        result.append(max_latency - result[2] if result[2] is not None else None)

    # 保存到 Excel
    df = pd.DataFrame(results, columns=["设备索引", "设备名称", "输出延迟 (秒)", "相对输出延迟 (秒)"])
    df.to_excel(OUTPUT_EXCEL, index=False)
    print(f"📂 测试结果已导出到 {OUTPUT_EXCEL}")


# 运行程序
if __name__ == "__main__":
    run_latency_tests()
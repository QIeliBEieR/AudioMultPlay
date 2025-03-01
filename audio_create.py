import numpy as np
import soundfile as sf

samplerate = 44100  # 采样率
duration = 3  # 3秒
frequency = 440.0  # 440Hz 正弦波（A4音）

t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)  # 生成正弦波

sf.write("audio_test.wav", audio_data, samplerate)
print("已生成 audio_test.wav")

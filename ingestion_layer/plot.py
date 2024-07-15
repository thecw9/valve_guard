import librosa
import numpy as np
import matplotlib.pyplot as plt

audio_file = "./11-53_ch0.wav"

y, sr = librosa.load(audio_file)

fig, ax = plt.subplots()
# ax.xaxis.set_visible(False)
# ax.yaxis.set_visible(False)
# plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# 隐藏底部和左侧的轴线，但保留刻度
ax.spines["bottom"].set_visible(False)
ax.spines["left"].set_visible(False)

# 保留刻度和刻度标签
ax.xaxis.set_ticks_position("bottom")
ax.yaxis.set_ticks_position("left")

# 设置刻度线和刻度标签的颜色为白色
ax.tick_params(axis="x", colors="white")
ax.tick_params(axis="y", colors="white")


# plot waveform
plt.plot(y)
plt.ylim(-0.01, 0.01)
plt.show()

import numpy as np
import librosa
import scipy.signal as signal
import matplotlib.pyplot as plt


def average_amplitude(y):
    """
    平均幅值
    """
    return np.mean(np.abs(y))


def rms_amplitude(y):
    """
    均方根幅值
    """
    return np.sqrt(np.mean(y**2))


def kurtosis(y):
    """
    计算数据的峰度
    """
    # 计算均值
    mean = np.mean(y)
    # 计算方差
    variance = np.var(y)
    # 计算标准差
    std_dev = np.sqrt(variance)
    # 计算四阶中心矩
    n = len(y)
    fourth_moment = np.sum(((y - mean) / std_dev) ** 4) / n
    # 计算峰度
    kurt = fourth_moment - 3  # 通常减去3以使正态分布的峰度为0
    return kurt


def peak_factor(y):
    """
    峰值因子
    """
    # 计算峰值（绝对值的最大值）
    peak_value = np.max(np.abs(y))
    # 计算RMS值（均方根值）
    rms_value = np.sqrt(np.mean(y**2))
    # 计算峰值因子
    peak_factor = peak_value / rms_value
    return peak_factor


def impulse_factor(y):
    """
    冲击因子
    """
    # 计算峰值（绝对值的最大值）
    peak_value = np.max(np.abs(y))
    # 计算绝对值之和
    sum_abs = np.sum(np.abs(y))
    # 计算冲击因子
    impulse_factor = peak_value / sum_abs
    return impulse_factor


def skewness(y):
    """
    偏度
    """
    # 计算均值
    mean = np.mean(y)
    # 计算标准差
    std_dev = np.std(y)
    # 计算三阶中心矩
    n = len(y)
    third_moment = np.sum(((y - mean) / std_dev) ** 3) / n
    # 计算偏度
    skew = third_moment
    return skew


def energy(y):
    """
    能量
    """
    return np.sum(y**2) / len(y)


def frequency_entropy(y, sr, frame_length=2048, frame_step=512):
    # 计算短时傅里叶变换（STFT）
    D = librosa.stft(y=y, n_fft=frame_length, hop_length=frame_step)

    # 计算幅度谱（功率谱的平方根）
    amplitudes = np.abs(D)

    # 对幅度谱进行平方，得到功率谱
    power_spectrum = amplitudes**2

    # 转换为分贝单位（可选，不是计算熵所必需的）
    # power_db = librosa.amplitude_to_db(power_spectrum)

    # 对功率谱进行归一化，使其成为概率分布
    # 忽略低于某个阈值的频率成分（可选，以减少噪音影响）
    power_spectrum = power_spectrum / np.sum(power_spectrum, axis=0, keepdims=True)
    power_spectrum = power_spectrum[power_spectrum > 1e-10]  # 忽略非常小的值
    power_spectrum /= np.sum(power_spectrum)  # 重新归一化

    # 计算频率熵
    # 注意：这里我们假设power_spectrum是一个二维数组，其中每列代表一个时间帧的功率谱
    # 我们对每个时间帧的功率谱计算熵
    entropy_per_frame = -np.sum(
        power_spectrum * np.log2(power_spectrum + 1e-15), axis=0
    )

    # 返回所有帧的频率熵的平均值
    return np.mean(entropy_per_frame)


def zero_crossing_rate(y):
    """
    过零率
    """
    return len(np.where(np.diff(np.sign(y)))[0]) / len(y)


if __name__ == "__main__":
    # file_path = "../store_service/data/2024-06-26_15-43-36_ch0.wav"
    # y, sr = librosa.load(file_path, sr=None)

    y = np.random.rand(16000, 8)
    sr = 44100

    avg_amp = average_amplitude(y)
    print("平均幅值：", avg_amp)

    rms_amp = rms_amplitude(y)
    print("均方根幅值：", rms_amp)

    kurt = kurtosis(y)
    print("峰度：", kurt)

    pf = peak_factor(y)
    print("峰值因子：", pf)

    ifac = impulse_factor(y)
    print("冲击因子：", ifac)

    skew = skewness(y)
    print("偏度：", skew)

    en = energy(y)
    print("能量：", en)

    fe = frequency_entropy(y, sr)
    print("频率熵：", fe)

    zcr = zero_crossing_rate(y)
    print("过零率：", zcr)

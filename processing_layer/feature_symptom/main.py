import sys
import os

# add current path to PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from io import BytesIO
import librosa
import os
from datetime import datetime, timedelta
from minio import Minio
from minio.error import S3Error
import numpy as np
import feature
from utils import create_sympton, store_sympton


minio_endpoint = "127.0.0.1:9000"
minio_access_key = "minioadmin"
minio_secret_key = "minioadmin"
bucket_name = "valve-guard"

minio_client = Minio(
    minio_endpoint,
    access_key=minio_access_key,
    secret_key=minio_secret_key,
    secure=False,
)


current_time = datetime.now() - timedelta(minutes=1)

data = []
try:
    for i in range(7):
        file_name = (
            "audio/" + current_time.strftime("%Y-%m-%d/%H-%M") + f"_ch{i}" + ".wav"
        )
        wav_data = minio_client.get_object(bucket_name, file_name)
        io_data = BytesIO(wav_data.read())
        audio_data, sample_rate = librosa.load(io_data, sr=None)
        data.append(audio_data)
except S3Error as e:
    raise e

data = np.array(data).T

current_time = current_time.isoformat()
average_amplitude = [feature.average_amplitude(data[:, i]) for i in range(7)]
results = [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.AverageAmplitude",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/平均幅值",
        "value": float(average_amplitude[i]),
    }
    for i in range(7)
]
results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.AverageAmplitudeDeviation",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/相对平均幅值偏差",
        "value": float(
            (average_amplitude[i] - np.mean(average_amplitude))
            / np.mean(average_amplitude)
        ),
    }
    for i in range(7)
]

rms_amplitude = [feature.rms_amplitude(data[:, i]) for i in range(7)]

results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.RMSAmplitude",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/均方根幅值",
        "value": float(rms_amplitude[i]),
    }
    for i in range(7)
]
results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.RMSAmplitudeDeviation",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/相对均方根幅值偏差",
        "value": float(
            (rms_amplitude[i] - np.mean(rms_amplitude)) / np.mean(rms_amplitude)
        ),
    }
    for i in range(7)
]

kurtosis = [feature.kurtosis(data[:, i]) for i in range(7)]
results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.Kurtosis",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/峰度",
        "value": float(kurtosis[i]),
    }
    for i in range(7)
]
results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.KurtosisDeviation",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/相对峰度偏差",
        "value": float((kurtosis[i] - np.mean(kurtosis)) / np.mean(kurtosis)),
    }
    for i in range(7)
]

skewness = [feature.skewness(data[:, i]) for i in range(7)]
results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.Skewness",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/偏度",
        "value": float(skewness[i]),
    }
    for i in range(7)
]
results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.SkewnessDeviation",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/相对偏度偏差",
        "value": float((skewness[i] - np.mean(skewness)) / np.mean(skewness)),
    }
    for i in range(7)
]

peak_factor = [feature.peak_factor(data[:, i]) for i in range(7)]
results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.PeakFactor",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/峰值因数",
        "value": float(peak_factor[i]),
    }
    for i in range(7)
]
results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.PeakFactorDeviation",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/相对峰值因数偏差",
        "value": float((peak_factor[i] - np.mean(peak_factor)) / np.mean(peak_factor)),
    }
    for i in range(7)
]

impulse_factor = [feature.impulse_factor(data[:, i]) for i in range(7)]
results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.ImpulseFactor",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/冲击因子",
        "value": float(impulse_factor[i]),
    }
    for i in range(7)
]
results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.ImpulseFactorDeviation",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/相对冲击因子偏差",
        "value": float(
            (impulse_factor[i] - np.mean(impulse_factor)) / np.mean(impulse_factor)
        ),
    }
    for i in range(7)
]

energy = [feature.energy(data[:, i]) for i in range(7)]
results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.Energy",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/能量",
        "value": float(energy[i]),
    }
    for i in range(7)
]
results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.EnergyDeviation",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/相对能量偏差",
        "value": float((energy[i] - np.mean(energy)) / np.mean(energy)),
    }
    for i in range(7)
]

frequency_entropy = [
    feature.frequency_entropy(data[:, i], sample_rate) for i in range(7)
]
results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.FrequencyEntropy",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/频率熵",
        "value": float(frequency_entropy[i]),
    }
    for i in range(7)
]
results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.FrequencyEntropyDeviation",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/相对频率熵偏差",
        "value": float(
            (frequency_entropy[i] - np.mean(frequency_entropy))
            / np.mean(frequency_entropy)
        ),
    }
    for i in range(7)
]

zero_crossing_rate = [feature.zero_crossing_rate(data[:, i]) for i in range(7)]
results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.ZeroCrossingRate",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/过零率",
        "value": float(zero_crossing_rate[i]),
    }
    for i in range(7)
]
results += [
    {
        "key": f"ShaoShang.Pole1Low.Sound.Channel{i}.ZeroCrossingRateDeviation",
        "timestamp": current_time,
        "path": f"/韶山站/极1低/声音/通道{i}/相对过零率偏差",
        "value": float(
            (zero_crossing_rate[i] - np.mean(zero_crossing_rate))
            / np.mean(zero_crossing_rate)
        ),
    }
    for i in range(7)
]


create_sympton(server="127.0.0.1:8050", data=results)
store_sympton(server="127.0.0.1:8050", data=results)

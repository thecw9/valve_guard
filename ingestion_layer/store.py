import socket
import time
import matplotlib.pyplot as plt
import librosa
from io import BytesIO
import os
from datetime import datetime
import scipy
import numpy as np
from minio import Minio
from minio.error import S3Error
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

max_tries = 60 * 24
wait_seconds = 60


def is_running_in_docker():
    # Check if the /proc/1/cgroup file exists
    return (
        os.path.exists("/.dockerenv")
        or os.path.isfile("/proc/1/cgroup")
        and any("docker" in line for line in open("/proc/1/cgroup"))
    )


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
)
def connect_to_server(server_ip, server_port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        print(f"Connected to the server at {server_ip}:{server_port}")
        return client_socket
    except Exception as e:
        print(f"Failed to connect to the server: {e}")
        raise


def recvall(sock, count):
    data = bytearray()
    while len(data) < count:
        packet = sock.recv(count - len(data))
        if not packet:
            raise Exception("Socket closed")
        data.extend(packet)
    return data


def save_to_minio(minio_client, bucket_name, file_name, data, content_type):
    try:
        minio_client.put_object(
            bucket_name,
            file_name,
            data,
            data.getbuffer().nbytes,
            content_type=content_type,
        )
        print(f"File {file_name} is successfully saved to MinIO.")
    except S3Error as err:
        print(f"Failed to save file to MinIO: {err}")


def main():
    server_ip = "10.126.233.202"  # 服务端的IP地址，如在不同的机器上运行，请修改此处
    server_port = 8080  # 服务端监听的端口号，需要与服务端设置一致
    if is_running_in_docker():
        minio_endpoint = "host.docker.internal:9000"
    else:
        minio_endpoint = "127.0.0.1:9000"
    access_key = "minioadmin"
    secret_key = "minioadmin"
    bucket_name = "valve-guard"

    # 连接到服务器
    client_socket = connect_to_server(server_ip, server_port)

    minio_client = Minio(
        minio_endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=False,
    )

    # 创建MinIO bucket
    found = minio_client.bucket_exists(bucket_name)
    if not found:
        try:
            minio_client.make_bucket(bucket_name)
            print(f"Successfully created the bucket: {bucket_name}")
        except S3Error as e:
            print(f"Error occurred while creating the bucket: {e}")

    try:
        buffer_size = (
            16000 * 60 * 8 * 8
        )  # 数据接收缓冲区的大小, 样本数 * 通道数 * 8字节(一个double类型数据的大小)
        while True:
            # 接收数据
            # data = recvall(client_socket, buffer_size)
            data = bytearray()
            while len(data) < buffer_size:
                try:
                    packet = client_socket.recv(buffer_size - len(data))
                    if not packet:
                        raise Exception("Socket closed")
                    data.extend(packet)
                except Exception as e:
                    client_socket.close()
                    client_socket = connect_to_server(server_ip, server_port)

            if not data:
                print("No more data from server. Closing connection.")
                break
            # 解析接收到的数据
            data = np.frombuffer(data, dtype=np.float64).reshape(-1, 8)
            # data = data.reshape(800, -1, 8)
            # data = data - np.mean(data, axis=0)
            # data = data.reshape(-1, 8)
            data = data / 10
            # data = data.astype(np.float32)
            # data = (data / np.max(np.abs(data)) * 32767).astype(np.int16)
            print(data)

            # 将数据存储到MinIO
            now = datetime.now()

            for i in range(8):
                wav_io = BytesIO()
                audio_data = (data[:, i] * 32767).astype(np.int16)
                scipy.io.wavfile.write(wav_io, 16000, audio_data)
                wav_io.seek(0)
                object_name = (
                    "audio/" + now.strftime("%Y-%m-%d/%H-%M") + f"_ch{i}" + ".wav"
                )
                save_to_minio(
                    minio_client=minio_client,
                    bucket_name=bucket_name,
                    file_name=object_name,
                    data=wav_io,
                    content_type="audio/wav",
                )

                # 波形图
                fig, ax = plt.subplots(figsize=(8, 4))
                # 隐藏顶部和右侧的轴线
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)

                # 隐藏底部和左侧的轴线
                ax.spines["bottom"].set_visible(False)
                ax.spines["left"].set_visible(False)

                # 隐藏X轴刻度
                ax.xaxis.set_ticks([])

                # 设置Y轴刻度和刻度标签的颜色为白色（可根据背景颜色调整）
                ax.tick_params(axis="y", colors="white")
                plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
                plt.ylim(-0.01, 0.01)
                plt.plot(data[:, i])
                plt.tight_layout()

                wave_img_io = BytesIO()
                plt.savefig(wave_img_io, transparent=True, format="png")
                wave_img_io.seek(0)
                plt.close()
                waveform_object_name = (
                    "waveform/" + now.strftime("%Y-%m-%d/%H-%M") + f"_ch{i}" + ".png"
                )
                save_to_minio(
                    minio_client=minio_client,
                    bucket_name=bucket_name,
                    file_name=waveform_object_name,
                    data=wave_img_io,
                    content_type="image/png",
                )

                # FFT图
                fft = np.fft.rfft(data[:, i])
                freqs = np.fft.rfftfreq(len(data[:, i]), 1 / 16000)
                fig, ax = plt.subplots(figsize=(8, 4))
                # 隐藏顶部和右侧的轴线
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
                plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
                plt.ylim(0, 1000)
                freq_lenght = len(freqs)
                plt.plot(
                    freqs[10 : int(freq_lenght / 4)],
                    np.abs(fft[10 : int(freq_lenght / 4)]),
                )
                plt.tight_layout()

                fft_img_io = BytesIO()
                plt.savefig(fft_img_io, transparent=True, format="png")
                fft_img_io.seek(0)
                plt.close()

                fft_object_name = (
                    "fft/" + now.strftime("%Y-%m-%d/%H-%M") + f"_ch{i}" + ".png"
                )
                save_to_minio(
                    minio_client=minio_client,
                    bucket_name=bucket_name,
                    file_name=fft_object_name,
                    data=fft_img_io,
                    content_type="image/png",
                )

                # 梅尔频谱
                mel_spectrogram = librosa.feature.melspectrogram(
                    y=data[:, i], sr=16000, n_mels=128
                )
                mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max)

                fig, ax = plt.subplots(figsize=(8, 4))
                ax.xaxis.set_visible(False)
                ax.yaxis.set_visible(False)
                plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
                plt.imshow(mel_spectrogram, cmap="viridis", aspect="auto")

                mel_img_io = BytesIO()
                plt.savefig(mel_img_io, transparent=True, format="png")
                mel_img_io.seek(0)
                plt.close()

                img_object_name = (
                    "mel/" + now.strftime("%Y-%m-%d/%H-%M") + f"_ch{i}" + ".png"
                )
                save_to_minio(
                    minio_client=minio_client,
                    bucket_name=bucket_name,
                    file_name=img_object_name,
                    data=mel_img_io,
                    content_type="image/png",
                )
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()

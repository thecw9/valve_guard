import socket
import numpy as np


def recvall(sock, count):
    data = bytearray()
    while len(data) < count:
        packet = sock.recv(count - len(data))
        if not packet:
            raise Exception("Socket closed")
        data.extend(packet)
    return data


def main():
    server_ip = "10.126.233.202"  # 服务端的IP地址，如在不同的机器上运行，请修改此处
    server_port = 8080  # 服务端监听的端口号，需要与服务端设置一致
    buffer_size = (
        1024 * 8 * 8
    )  # 数据接收缓冲区的大小, 样本数 * 通道数 * 8字节(一个double类型数据的大小)

    # 创建socket对象
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 连接到服务器
    try:
        client_socket.connect((server_ip, server_port))
        print("Connected to the server at {}:{}".format(server_ip, server_port))
    except Exception as e:
        print(f"Failed to connect to the server: {e}")
        client_socket.close()
        return

    try:
        while True:
            # 接收数据
            data = recvall(client_socket, buffer_size)
            print(len(data))
            if not data:
                print("No more data from server. Closing connection.")
                break
            # 输出接收到的数据
            data = np.frombuffer(data, dtype=np.float64).reshape(-1, 8)
            print(f"Received data: {data}")
    except Exception as e:
        print(f"Error receiving data: {e}")
    finally:
        # 关闭连接
        client_socket.close()
        print("Connection closed.")


if __name__ == "__main__":
    main()

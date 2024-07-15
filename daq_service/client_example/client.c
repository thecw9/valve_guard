#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#define SERVER_IP "10.126.233.202"
#define SERVER_PORT 8080
#define BUFFER_SIZE 1024 * 8 // 8192 bytes

int main() {
  int sock = 0;
  struct sockaddr_in serv_addr;
  char buffer[BUFFER_SIZE] = {0};
  int totalBytesRead = 0, bytesRead;

  // 创建套接字
  if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
    printf("Socket creation error\n");
    return -1;
  }

  serv_addr.sin_family = AF_INET;
  serv_addr.sin_port = htons(SERVER_PORT);

  // 将IPv4和IPv6地址从文本转换为二进制形式
  if (inet_pton(AF_INET, SERVER_IP, &serv_addr.sin_addr) <= 0) {
    printf("Invalid address / Address not supported\n");
    return -1;
  }

  // 连接到服务器
  if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
    printf("Connection Failed\n");
    return -1;
  }

  printf("Connected to server at %s:%d\n", SERVER_IP, SERVER_PORT);

  // 接收数据直到接收到完整的8192字节
  while (totalBytesRead < BUFFER_SIZE) {
    bytesRead =
        recv(sock, buffer + totalBytesRead, BUFFER_SIZE - totalBytesRead, 0);
    if (bytesRead > 0) {
      totalBytesRead += bytesRead;
      printf("Received %d bytes, Total received: %d bytes\n", bytesRead,
             totalBytesRead);
    } else if (bytesRead == 0) {
      printf("Server closed the connection\n");
      break;
    } else {
      perror("recv error");
      break;
    }
  }

  close(sock);
  return 0;
}


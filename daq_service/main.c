// 本程序演示AI连续采样原码数据过程

#include <arpa/inet.h>
#include <fcntl.h>
#include <math.h>
#include <netinet/in.h>
#include <pthread.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

#include <stdlib.h>

#include "./lib/ACTS3100.h" // 驱动程序头文件，在您的工程代码中包含此文件即可使用驱动函数

#define PORT 8080
#define BUFFER_SIZE 1024 * 8
#define MAX_CLIENTS 100
#define CH_PERCHAN 1024
F64 fVoltArray[ACTS3100_AI_MAX_CHANNELS * CH_PERCHAN];

void signal_handler(int signal) { printf("Received signal %d\n", signal); }

typedef struct {
  int clients[MAX_CLIENTS];
  int client_count;
  pthread_mutex_t mutex;
} ClientList;

typedef struct {
  HANDLE hDevice;
  ACTS3100_AI_PARAM *AIParam;
} SendDataArgs;

ClientList client_list = {.client_count = 0,
                          .mutex = PTHREAD_MUTEX_INITIALIZER};

void *send_data(void *args) {
  while (1) {
    SendDataArgs *send_data_args = (SendDataArgs *)args;
    HANDLE hDevice = send_data_args->hDevice;
    ACTS3100_AI_PARAM *AIParam = send_data_args->AIParam;

    U32 nReadSampsPerChan = CH_PERCHAN; // 每通道读取点数
    U32 nSampsPerChanRead = 0;
    F64 fTimeout = 1.0; // 1秒钟超时
    U32 nReadableSamps = 0;

    if (!ACTS3100_AI_ReadAnalog(hDevice, fVoltArray, nReadSampsPerChan,
                                &nSampsPerChanRead, &nReadableSamps,
                                fTimeout)) {
      printf("Timeout nSampsPerChanRead=%d\n", nSampsPerChanRead);
    }

    // 发送数据
    // fVoltArray * 1000
    // for (int i = 0; i < nSampsPerChanRead * AIParam->nSampChanCount; i++) {
    //   fVoltArray[i] *= 1000;
    // }
    pthread_mutex_lock(&client_list.mutex);
    for (int i = 0; i < client_list.client_count; i++) {
      int client_socket = client_list.clients[i];
      if (send(client_socket, fVoltArray,
               sizeof(F64) * nSampsPerChanRead * AIParam->nSampChanCount,
               0) < 0) {
        printf("Failed to send data to client\n");
        printf("--> Client disconnected\n");
        close(client_socket);
        client_list.clients[i] =
            client_list.clients[client_list.client_count - 1];
        client_list.client_count--;
        i--;
      }
    }
    pthread_mutex_unlock(&client_list.mutex);
  }

  return NULL;
}

void *accept_clients(void *args) {
  int server_socket = *((int *)args);
  struct sockaddr_in client_addr;
  socklen_t addr_len = sizeof(client_addr);

  while (1) {
    int client_socket =
        accept(server_socket, (struct sockaddr *)&client_addr, &addr_len);
    if (client_socket < 0) {
      printf("Failed to accept client\n");
      continue;
    }
    printf("--> Client connected\n");

    pthread_mutex_lock(&client_list.mutex);
    if (client_list.client_count < MAX_CLIENTS) {
      client_list.clients[client_list.client_count++] = client_socket;
    } else {
      close(client_socket);
    }
    pthread_mutex_unlock(&client_list.mutex);
  }

  return NULL;
}

int main(int argc, char *argv[]) {
  signal(SIGPIPE, signal_handler);

  ACTS3100_AI_PARAM AIParam;
  U32 nReadSampsPerChan = CH_PERCHAN; // 每通道读取点数
  U32 nSampsPerChanRead = 0;
  F64 fTimeout = 1.0; // 1秒钟超时
  U32 nReadableSamps = 0;
  HANDLE hDevice = NULL;
  ACTS3100_MAIN_INFO MainInfo;
  U32 nChannel = 0;

  // 第一步 创建设备对象
  hDevice = ACTS3100_DEV_Create(0, 0);
  if (hDevice == NULL) {
    printf("DEV_Create Error\n");
    getc(stdin);
    return 0;
  }

  ACTS3100_GetMainInfo(hDevice, &MainInfo); // DDR2的长度(单位：MB)
  switch (MainInfo.nDeviceType >> 16) {
  case 0x2012:
    printf("PXIE%04X\n", MainInfo.nDeviceType & 0xFFFF);
    break;
  case 0x2011:
    printf("PCIE%04X\n", MainInfo.nDeviceType & 0xFFFF);
    break;
  default:
    printf("ACTS3100-%04X\n", MainInfo.nDeviceType);
  }

  memset(&AIParam, 0, sizeof(ACTS3100_AI_PARAM));

  // 通道参数
  AIParam.nSampChanCount = 8;
  for (nChannel = 0; nChannel < MainInfo.nAIChannelCount; nChannel++) {
    AIParam.CHParam[nChannel].bChannelEn = 1;
    AIParam.CHParam[nChannel].nSampleRange = ACTS3100_AI_SAMPRANGE_N10_P10V;
    AIParam.CHParam[nChannel].nRefGround = ACTS3100_AI_REFGND_RSE;
    AIParam.CHParam[nChannel].nReserved0 = 0;
    AIParam.CHParam[nChannel].nReserved1 = 0;
    AIParam.CHParam[nChannel].nReserved2 = 0;
  }
  AIParam.nSampleSignal = 0; // ACTS3100_AI_SAMPSIGNAL_0V

  // 时钟参数
  AIParam.fSampleRate = 16000.0;
  AIParam.nSampleMode = ACTS3100_AI_SAMPMODE_CONTINUOUS;
  AIParam.nSampsPerChan = 1024;
  AIParam.nSampClkSource = ACTS3100_AIO_SAMPCLKSRC_LOCAL;
  AIParam.nClockOutput = ACTS3100_AIO_CLKOUT_DISABLE;
  AIParam.StartTrig.nSyncTSOut = ACTS3100_AIO_STSO_DISABLE;

  // 触发参数
  AIParam.StartTrig.nTriggerType = ACTS3100_AI_START_TRIGTYPE_NONE;
  AIParam.StartTrig.nTriggerSource = ACTS3100_AI_TRIG_SRC_FIRST;
  AIParam.StartTrig.nTriggerDir = ACTS3100_AI_TRIGDIR_FALLING;
  AIParam.StartTrig.fTriggerLevelTop = 1.0;
  AIParam.StartTrig.fTriggerLevelBtm = 0.0;
  AIParam.StartTrig.nTriggerSens = 0;
  AIParam.StartTrig.nDelaySamps = 0;
  AIParam.StartTrig.nReTrigger = 0;

  AIParam.PauseTrig.nTriggerType = ACTS3100_AI_START_TRIGTYPE_NONE;
  AIParam.PauseTrig.nTriggerSource = ACTS3100_AI_TRIG_SRC_FIRST;
  AIParam.PauseTrig.nTriggerDir = ACTS3100_AI_TRIGDIR_FALLING;
  AIParam.PauseTrig.fTriggerLevelTop = 1.0;
  AIParam.PauseTrig.fTriggerLevelBtm = 0.0;
  AIParam.PauseTrig.nTriggerSens = 0;

  // 其他参数
  AIParam.nReserved1 = 0;
  AIParam.nReserved2 = 0;
  AIParam.nReserved3 = 0;

  if (!ACTS3100_AI_VerifyParam(hDevice, &AIParam)) {
    printf("Wrong parameter, it has been adjusted to legal value，Please check "
           "the log file acts3100.log and press any key to continue...\n");
    getc(stdin);
  }

  // 第二步 初始化AI采集任务
  if (!ACTS3100_AI_InitTask(hDevice, &AIParam)) {
    printf("AI_InitTask Error,Please refer to log file\n");
    getc(stdin);
    ACTS3100_DEV_Release(hDevice);
    return 0;
  }

  // 第三步 开始AI采集任务
  if (!ACTS3100_AI_StartTask(hDevice)) {
    printf("AI_StartTask Error\n");
    getc(stdin);
  }

  // 第四步 发送软件触发事件(硬件外触发时不需要)
  if (!ACTS3100_AI_SendSoftTrig(hDevice)) {
    printf("AI_SendSoftTrig Error\n");
    getc(stdin);
  }

  // 创建服务器
  int server_socket = socket(AF_INET, SOCK_STREAM, 0);
  if (server_socket < 0) {
    printf("Failed to create server socket\n");
    exit(EXIT_FAILURE);
  }
  // int opt = 1;
  // if (setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT,
  // &opt,
  //                sizeof(opt))) {
  //   printf("Failed to set socket options\n");
  //   exit(EXIT_FAILURE);
  // }

  // 设置服务器地址
  struct sockaddr_in server_addr;
  server_addr.sin_family = AF_INET;
  server_addr.sin_addr.s_addr = INADDR_ANY;
  server_addr.sin_port = htons(PORT);

  // 绑定服务器地址
  if (bind(server_socket, (struct sockaddr *)&server_addr,
           sizeof(server_addr)) < 0) {
    printf("Failed to bind server address\n");
    exit(EXIT_FAILURE);
  }

  // 监听
  if (listen(server_socket, 3) < 0) {
    printf("Failed to listen\n");
    exit(EXIT_FAILURE);
  } else {
    printf("Listening on port %d\n", PORT);
  }

  // 创建线程
  pthread_t accept_clients_thread, send_data_thread;
  if (pthread_create(&accept_clients_thread, NULL, accept_clients,
                     &server_socket) != 0) {
    printf("Failed to create accept clients thread\n");
    exit(EXIT_FAILURE);
  }
  if (pthread_create(
          &send_data_thread, NULL, send_data,
          &(SendDataArgs){.hDevice = hDevice, .AIParam = &AIParam}) != 0) {
    printf("Failed to create send data thread\n");
    exit(EXIT_FAILURE);
  }

  pthread_join(accept_clients_thread, NULL);
  pthread_join(send_data_thread, NULL);

  // 第六步 停止AI采集任务
  if (!ACTS3100_AI_StopTask(hDevice)) {
    printf("AI_StopTask Error\n");
    getc(stdin);
  }

  // 第七步 释放AI采集任务
  if (!ACTS3100_AI_ReleaseTask(hDevice)) {
    printf("AI_ReleaseTask Error\n");
    getc(stdin);
  }

  // 第八步 释放设备对象
  if (!ACTS3100_DEV_Release(hDevice)) {
    printf("DEV_Release Error\n");
    getc(stdin);
  }

  close(server_socket);

  return 0;
}

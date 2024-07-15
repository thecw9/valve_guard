import axios from "@/utils/csustRequest";

// 通过时间获取历史数据
export function getDeviceHistoryAlarm(
  startTime = null,
  endTime = null,
  page = null,
  size = null,
) {
  const data = {
    start_time: startTime,
    end_time: endTime,
    page: page,
    size: size,
  };
  return axios.post("/alarm-service/device/history", data, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
}

// 通过时间获取测点告警历史数据
export function getMeasureHistoryAlarm(
  startTime = null,
  endTime = null,
  page = null,
  size = null,
) {
  const data = {
    start_time: startTime,
    end_time: endTime,
    page: page,
    size: size,
  };
  return axios.post("/alarm-service/measure/history", data, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
}

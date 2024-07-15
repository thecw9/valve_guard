import axios from "@/utils/csustRequest";

export function getTrainLogsList(
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
  return axios.post("train-logs-service/list", data, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
}

export function deleteAllTrainLogs() {
  return axios.post("train-logs-service/delete-all", null, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
}

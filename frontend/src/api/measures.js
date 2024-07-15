import axios from "@/utils/symptonRequest";

export function getMeasuresInfo(include, exclude = null) {
  const params = {
    include: include,
    exclude: exclude,
  };

  return axios.post("/sympton/", params, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
}

export function getMeasuresInfoByKey(key) {
  return axios.post(
    "/measures-service/info/detail",
    {
      key: key,
    },
    {
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    },
  );
}

export function getDataByKeys(keys) {
  return axios.post(
    "/measures-service/realtime",
    {
      keys: keys,
    },
    {
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    },
  );
}

// 通过时间获取历史数据
export function getHistoryDataByTime(
  key,
  startTime = null,
  endTime = null,
  page = null,
  size = null,
) {
  const data = {
    key: key,
    start_time: startTime,
    end_time: endTime,
    page: page,
    size: size,
  };
  return axios.post(
    "/sympton/history/",
    {
      key: key,
      start_time: startTime,
      end_time: endTime,
      page: page,
      size: size,
    },
    {
      headers: {
        accept: "application/json",
        "Content-Type": "application/json",
      },
    },
  );
}

// 获取最新n条历史数据
export function getLatestHistoryData(keys, limit) {
  return axios.post(
    "/measures-service/history/latest",
    {
      keys: keys,
      limit: limit,
    },
    {
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    },
  );
}

async function getKeysData(include, exclude) {
  const res = await getMeasuresInfo(include, exclude);
  const keys = res.data.map((item) => {
    return item.key;
  });
  return keys;
}

export async function getDataByKeywords(include, exclude) {
  const keys = await getKeysData(include, exclude);
  const res = await getDataByKeys(keys);
  return res;
}

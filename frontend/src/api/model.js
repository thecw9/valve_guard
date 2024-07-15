import axios from "@/utils/modelRequest";

export function trainModel(key, name, start_time, end_time) {
  return axios.post("/model/train/", {
    key: key,
    name: name,
    start_time: start_time,
    end_time: end_time,
  });
}

// predict
export function modelPredict(data) {
  return axios.post("/model-service/predict", data, {
    headers: {
      "Content-Type": "application/json",
    },
  });
}

export function getModelInfo(include, exclude) {
  const data = {
    include: include,
    exclude: exclude,
  };
  return axios.post("/model/info", data, {
    headers: {
      "Content-Type": "application/json",
    },
  });
}

// get model info by id
export function getModelInfoById(id) {
  return axios.get(`/model/info/${id}`);
}

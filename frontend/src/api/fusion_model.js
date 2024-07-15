import axios from "@/utils/csustRequest";

export function trainFusionModel(keys, startTrain, endTrain) {
  const data = {
    keys: keys,
    start_time: startTrain,
    end_time: endTrain,
  };
  return axios.post("/fusion-model-service/train", data, {
    headers: {
      "Content-Type": "application/json",
    },
  });
}

// predict
export function modelFusionPredict(keys) {
  const data = {
    keys: keys,
  };
  return axios.post("/fusion-model-service/predict", data, {
    headers: {
      "Content-Type": "application/json",
    },
  });
}

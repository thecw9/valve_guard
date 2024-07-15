import axios from "@/utils/request";

export function getRealTimeSound(num_samples) {
  const params = {
    num_samples: num_samples,
  };
  return axios.post("/v1/sound-service/sound", null, {
    params: params,
  });
}

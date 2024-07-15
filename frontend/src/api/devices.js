import axios from "@/utils/csustRequest";

export function getDevicesInfo(include, exclude = "") {
  const url = "devices-service/info";
  const data = {
    include: include,
    exclude: exclude,
  };

  return axios.post(url, data, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
}

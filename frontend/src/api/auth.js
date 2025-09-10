import axios from "./axiosInstance";

export const signup = async ({ username, password }) => {
  const { data } = await axios.post("/signup", { username, password });
  return data; 
};

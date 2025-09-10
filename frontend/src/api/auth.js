import axios from "./axiosInstance";

export const signup = async ({ username, password }) => {
  const { data } = await axios.post("/signup", { username, password });
  return data; 
};

export const signin = async ({ username, password }) => {
    console.log(username, password);   
  const { data } = await axios.post("/signin", { username, password });
  return data; 
};

export const signout = async () => {
  return await axios.post("/signout"); 
};

import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: API_URL });

export const login = (payload) => api.post("/auth/login", payload).then(r => r.data);
export const triggerSimSwap = (payload) => api.post("/demo/trigger-sim-swap", payload).then(r => r.data);
export const resetDemo = (phone) => api.post(`/demo/reset?phone_number=${phone}`).then(r => r.data);
export const getLogs = (userId) => api.get(`/trust/logs/${userId}`).then(r => r.data);
export const getDNA = (userId) => api.get(`/trust/dna/${userId}`).then(r => r.data);
import axios from "axios";

// 用 127.0.0.1 而不是 localhost，防止代理工具拦截
const BASE_URL = "http://127.0.0.1:8000/api/v1";

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000, // 首次搜索需要加载 5000 支股票，给足时间
});

export interface StockSearchResult {
  code: string;
  name: string;
}

export interface PlotState {
  slot_index: number;
  plot_id?: string;
  stock_code?: string;
  stock_name?: string;
  buy_price?: number;
  current_price?: number;
  return_pct?: number;
  status: string;
  stage_index: number;
  is_harvestable?: boolean;
  planted_at?: string;
}

export interface FarmResponse {
  farm_id: string;
  name: string;
  plots: PlotState[];
}

export const stockApi = {
  search: (q: string) =>
    api.get<{ results: StockSearchResult[] }>("/stocks/search", { params: { q } }),
  quote: (code: string) =>
    api.get(`/stocks/quote/${code}`),
};

export const farmApi = {
  get: (deviceId: string) =>
    api.get<FarmResponse>(`/farm/${deviceId}`),
  plant: (deviceId: string, stock_code: string, stock_name: string, slot_index: number) =>
    api.post(`/farm/${deviceId}/plant`, { stock_code, stock_name, slot_index }),
  harvest: (deviceId: string, plotId: string) =>
    api.post(`/farm/${deviceId}/harvest/${plotId}`),
  remove: (deviceId: string, plotId: string) =>
    api.delete(`/farm/${deviceId}/remove/${plotId}`),
};

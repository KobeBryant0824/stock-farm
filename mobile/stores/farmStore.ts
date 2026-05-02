import { create } from "zustand";
import { PlotState } from "../services/api";

interface FarmStore {
  deviceId: string;
  farmName: string;
  plots: PlotState[];
  setFarm: (name: string, plots: PlotState[]) => void;
  updatePlot: (slotIndex: number, update: Partial<PlotState>) => void;
}

function getOrCreateDeviceId(): string {
  try {
    const stored = localStorage.getItem("stock_farm_device_id");
    if (stored) return stored;
    const newId = `user_${Math.random().toString(36).slice(2)}_${Date.now()}`;
    localStorage.setItem("stock_farm_device_id", newId);
    return newId;
  } catch {
    // SSR 或非浏览器环境兜底
    return `user_fallback_${Date.now()}`;
  }
}

const DEVICE_ID = getOrCreateDeviceId();

export const useFarmStore = create<FarmStore>((set) => ({
  deviceId: DEVICE_ID,
  farmName: "我的农场",
  plots: [],
  setFarm: (name, plots) => set({ farmName: name, plots }),
  updatePlot: (slotIndex, update) =>
    set((state) => ({
      plots: state.plots.map((p) =>
        p.slot_index === slotIndex ? { ...p, ...update } : p
      ),
    })),
}));

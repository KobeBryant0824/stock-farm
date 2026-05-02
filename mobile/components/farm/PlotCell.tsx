import React from "react";
import { View, Text, TouchableOpacity, StyleSheet, Alert } from "react-native";
import { PlotState, farmApi } from "../../services/api";
import { useFarmStore } from "../../stores/farmStore";
import { GrowthStages } from "../plant/GrowthStages";
import { PlantStatus } from "../../constants/growthMapping";

interface Props {
  plot: PlotState;
  onAddSeed: (slotIndex: number) => void;
  onRefresh: () => void;
}

export function PlotCell({ plot, onAddSeed, onRefresh }: Props) {
  const { deviceId } = useFarmStore();

  async function handleHarvest() {
    if (!plot.plot_id) return;
    try {
      const res = await farmApi.harvest(deviceId, plot.plot_id);
      Alert.alert("收获成功！", `涨幅 +${res.data.return_pct}%，果实已入库！`);
      onRefresh();
    } catch (e: any) {
      Alert.alert("收获失败", e.response?.data?.detail ?? "请稍后再试");
    }
  }

  async function handleRemove() {
    if (!plot.plot_id) return;
    Alert.alert("确认铲除", `要把 ${plot.stock_name} 铲掉吗？`, [
      { text: "取消", style: "cancel" },
      {
        text: "铲掉",
        style: "destructive",
        onPress: async () => {
          await farmApi.remove(deviceId, plot.plot_id!);
          onRefresh();
        },
      },
    ]);
  }

  if (plot.status === "empty") {
    return (
      <TouchableOpacity style={styles.emptyPlot} onPress={() => onAddSeed(plot.slot_index)}>
        <Text style={styles.plusIcon}>+</Text>
        <Text style={styles.emptyLabel}>种下股票</Text>
      </TouchableOpacity>
    );
  }

  const isUnderwater = plot.status === "seed";

  return (
    <View style={[styles.plot, isUnderwater && styles.plotUnderwater]}>
      {/* 植物画面 */}
      <GrowthStages
        status={plot.status as PlantStatus}
        returnPct={plot.return_pct}
      />

      {/* 股票名称 */}
      <Text style={styles.stockName} numberOfLines={1}>
        {plot.stock_name}
      </Text>
      <Text style={styles.stockCode}>{plot.stock_code}</Text>

      {/* 被套提示 */}
      {isUnderwater && (
        <Text style={styles.underwaterLabel}>😴 被套了，等待解套...</Text>
      )}

      {/* 操作按钮 */}
      <View style={styles.actions}>
        {plot.is_harvestable && (
          <TouchableOpacity style={styles.harvestBtn} onPress={handleHarvest}>
            <Text style={styles.harvestBtnText}>收获</Text>
          </TouchableOpacity>
        )}
        <TouchableOpacity style={styles.removeBtn} onPress={handleRemove}>
          <Text style={styles.removeBtnText}>铲除</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  plot: {
    width: "47%",
    margin: "1.5%",
    backgroundColor: "#e8f5e9",
    borderRadius: 12,
    padding: 10,
    minHeight: 160,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#a5d6a7",
  },
  plotUnderwater: {
    backgroundColor: "#fce4ec",
    borderColor: "#ef9a9a",
  },
  emptyPlot: {
    width: "47%",
    margin: "1.5%",
    backgroundColor: "#f5f5f5",
    borderRadius: 12,
    padding: 10,
    minHeight: 160,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 2,
    borderColor: "#e0e0e0",
    borderStyle: "dashed",
  },
  plusIcon: {
    fontSize: 32,
    color: "#bdbdbd",
  },
  emptyLabel: {
    fontSize: 12,
    color: "#9e9e9e",
    marginTop: 4,
  },
  stockName: {
    fontSize: 13,
    fontWeight: "bold",
    color: "#333",
    marginTop: 4,
  },
  stockCode: {
    fontSize: 11,
    color: "#888",
  },
  underwaterLabel: {
    fontSize: 10,
    color: "#c62828",
    marginTop: 4,
    textAlign: "center",
  },
  actions: {
    flexDirection: "row",
    marginTop: 8,
    gap: 6,
  },
  harvestBtn: {
    backgroundColor: "#ff6f00",
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 20,
  },
  harvestBtnText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "bold",
  },
  removeBtn: {
    backgroundColor: "#eeeeee",
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 20,
  },
  removeBtnText: {
    color: "#666",
    fontSize: 12,
  },
});

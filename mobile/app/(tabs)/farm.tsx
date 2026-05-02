import React, { useCallback } from "react";
import { View, ActivityIndicator, Text, StyleSheet } from "react-native";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter, useFocusEffect } from "expo-router";
import { farmApi } from "../../services/api";
import { useFarmStore } from "../../stores/farmStore";
import { FarmGrid } from "../../components/farm/FarmGrid";

export default function FarmScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { deviceId, setFarm } = useFarmStore();

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["farm", deviceId],
    queryFn: async () => {
      const res = await farmApi.get(deviceId);
      setFarm(res.data.name, res.data.plots);
      return res.data;
    },
    refetchInterval: 5 * 60 * 1000,
  });

  // 每次从选股页返回时自动刷新农场
  useFocusEffect(
    useCallback(() => {
      queryClient.invalidateQueries({ queryKey: ["farm", deviceId] });
    }, [deviceId, queryClient])
  );

  const handleAddSeed = useCallback(
    (slotIndex: number) => {
      router.push({ pathname: "/(tabs)/market", params: { slotIndex } });
    },
    [router]
  );

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#2e7d32" />
        <Text style={styles.loadingText}>加载农场中...</Text>
      </View>
    );
  }

  if (isError) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>无法连接服务器，请检查网络</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FarmGrid
        plots={data?.plots ?? []}
        onAddSeed={handleAddSeed}
        onRefresh={refetch}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f1f8e9" },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#f1f8e9",
  },
  loadingText: { marginTop: 12, color: "#666" },
  errorText: { color: "#c62828", fontSize: 14 },
});

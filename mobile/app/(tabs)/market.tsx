import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { stockApi, farmApi, StockSearchResult } from "../../services/api";
import { useFarmStore } from "../../stores/farmStore";

export default function MarketScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ slotIndex?: string }>();
  const slotIndex = params.slotIndex !== undefined ? parseInt(params.slotIndex as string) : null;
  const { deviceId } = useFarmStore();

  const [query, setQuery] = useState("");
  const [results, setResults] = useState<StockSearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [planting, setPlanting] = useState<string | null>(null);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const searchTimer = React.useRef<ReturnType<typeof setTimeout> | null>(null);

  function handleSearch(text: string) {
    setQuery(text);
    setSearchError(null);
    if (searchTimer.current) clearTimeout(searchTimer.current);
    if (text.length < 1) {
      setResults([]);
      return;
    }
    // 防抖：停止输入 400ms 后再请求
    searchTimer.current = setTimeout(async () => {
      setSearching(true);
      try {
        const res = await stockApi.search(text);
        setResults(res.data.results);
        if (res.data.results.length === 0) {
          setSearchError("没有找到匹配的股票，试试输入代码如 000001");
        }
      } catch (e: any) {
        setResults([]);
        const msg = e.code === "ECONNABORTED"
          ? "请求超时，后端正在加载股票列表，请稍等几秒再试"
          : `搜索失败：${e.message ?? "无法连接后端"}`;
        setSearchError(msg);
      } finally {
        setSearching(false);
      }
    }, 400);
  }

  async function handleSelect(stock: StockSearchResult) {
    if (slotIndex === null) {
      setToast({ msg: "请先回到农场，点击空地块再来选股", ok: false });
      return;
    }
    setPlanting(stock.code);
    setToast(null);
    try {
      await farmApi.plant(deviceId, stock.code, stock.name, slotIndex);
      setToast({ msg: `${stock.name} 已种下！正在返回农场...`, ok: true });
      // 1 秒后自动返回，农场页 useFocusEffect 会刷新数据
      setTimeout(() => router.back(), 1000);
    } catch (e: any) {
      const detail = e.response?.data?.detail ?? "请稍后重试";
      setToast({ msg: `种植失败：${detail}`, ok: false });
    } finally {
      setPlanting(null);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🔍 选一支股票种下</Text>
      {slotIndex !== null && (
        <Text style={styles.subtitle}>将种入第 {slotIndex + 1} 块地</Text>
      )}

      {/* 提示条 */}
      {toast && (
        <View style={[styles.toast, toast.ok ? styles.toastOk : styles.toastErr]}>
          <Text style={styles.toastText}>{toast.msg}</Text>
        </View>
      )}

      <TextInput
        style={styles.input}
        placeholder="输入股票代码或名称，如 000001 或 平安"
        value={query}
        onChangeText={handleSearch}
        autoFocus
      />

      {searching && (
        <View style={styles.searchingRow}>
          <ActivityIndicator color="#2e7d32" />
          <Text style={styles.searchingText}>搜索中...</Text>
        </View>
      )}

      {searchError && (
        <View style={styles.errorBox}>
          <Text style={styles.errorText}>⚠️ {searchError}</Text>
        </View>
      )}

      <FlatList
        data={results}
        keyExtractor={(item) => item.code}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.resultItem}
            onPress={() => handleSelect(item)}
            disabled={!!planting}
          >
            <View>
              <Text style={styles.stockName}>{item.name}</Text>
              <Text style={styles.stockCode}>{item.code}</Text>
            </View>
            {planting === item.code ? (
              <ActivityIndicator color="#2e7d32" />
            ) : (
              <Text style={styles.plantBtn}>种下 →</Text>
            )}
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff", padding: 16 },
  title: { fontSize: 20, fontWeight: "bold", color: "#2e7d32", marginBottom: 4 },
  subtitle: { fontSize: 13, color: "#888", marginBottom: 8 },
  toast: {
    borderRadius: 8,
    padding: 10,
    marginBottom: 10,
  },
  toastOk: { backgroundColor: "#e8f5e9" },
  toastErr: { backgroundColor: "#fce4ec" },
  toastText: { fontSize: 13, color: "#333", textAlign: "center" },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 10,
    padding: 10,
    fontSize: 14,
    marginBottom: 8,
    backgroundColor: "#fafafa",
  },
  resultItem: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },
  stockName: { fontSize: 15, fontWeight: "600", color: "#333" },
  stockCode: { fontSize: 12, color: "#999", marginTop: 2 },
  plantBtn: { fontSize: 14, color: "#2e7d32", fontWeight: "bold" },
  empty: { textAlign: "center", color: "#aaa", marginTop: 24 },
  searchingRow: { flexDirection: "row", alignItems: "center", marginTop: 12, gap: 8 },
  searchingText: { color: "#888", fontSize: 13 },
  errorBox: { backgroundColor: "#fff3e0", borderRadius: 8, padding: 10, marginTop: 8 },
  errorText: { color: "#e65100", fontSize: 13 },
});

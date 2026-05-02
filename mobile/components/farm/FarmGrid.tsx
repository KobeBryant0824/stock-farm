import React from "react";
import { View, StyleSheet, ScrollView, Text } from "react-native";
import { PlotState } from "../../services/api";
import { PlotCell } from "./PlotCell";

interface Props {
  plots: PlotState[];
  onAddSeed: (slotIndex: number) => void;
  onRefresh: () => void;
}

export function FarmGrid({ plots, onAddSeed, onRefresh }: Props) {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>🌾 我的农场</Text>
      <View style={styles.grid}>
        {plots.map((plot) => (
          <PlotCell
            key={plot.slot_index}
            plot={plot}
            onAddSeed={onAddSeed}
            onRefresh={onRefresh}
          />
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 12,
    paddingBottom: 40,
  },
  title: {
    fontSize: 22,
    fontWeight: "bold",
    color: "#2e7d32",
    marginBottom: 12,
    textAlign: "center",
  },
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "flex-start",
  },
});

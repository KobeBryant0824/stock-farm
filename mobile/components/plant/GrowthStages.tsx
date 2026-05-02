import React from "react";
import { View, Text, StyleSheet } from "react-native";
import Animated, {
  useAnimatedStyle,
  withSpring,
  withSequence,
  withTiming,
} from "react-native-reanimated";
import { PlantStatus, GROWTH_STAGES, STAGE_HEIGHT } from "../../constants/growthMapping";

interface Props {
  status: PlantStatus;
  returnPct?: number;
}

export function GrowthStages({ status, returnPct }: Props) {
  const stage = GROWTH_STAGES.find((s) => s.status === status) ?? GROWTH_STAGES[0];
  const targetHeight = STAGE_HEIGHT[status];

  const animStyle = useAnimatedStyle(() => ({
    height: withSpring(targetHeight, { damping: 8, stiffness: 100 }),
    opacity: withTiming(status === "empty" ? 0 : 1, { duration: 300 }),
  }));

  // 收获时给一个弹跳动画
  const scaleStyle = useAnimatedStyle(() => {
    if (status === "full_tree") {
      return {
        transform: [
          {
            scale: withSequence(
              withTiming(1.15, { duration: 400 }),
              withSpring(1.0)
            ),
          },
        ],
      };
    }
    return { transform: [{ scale: 1 }] };
  });

  if (status === "empty") return null;

  return (
    <View style={styles.container}>
      <Animated.View style={[styles.plantWrapper, animStyle, scaleStyle]}>
        <Text style={[styles.emoji, { fontSize: targetHeight * 0.6 + 12 }]}>
          {stage.emoji}
        </Text>
      </Animated.View>
      {returnPct !== undefined && status !== "seed" && (
        <Text style={[styles.returnLabel, { color: returnPct >= 0 ? "#e74c3c" : "#27ae60" }]}>
          {returnPct >= 0 ? "+" : ""}{returnPct.toFixed(2)}%
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    justifyContent: "flex-end",
    flex: 1,
  },
  plantWrapper: {
    alignItems: "center",
    justifyContent: "flex-end",
    overflow: "hidden",
  },
  emoji: {
    lineHeight: undefined,
  },
  returnLabel: {
    fontSize: 10,
    fontWeight: "bold",
    marginTop: 2,
  },
});

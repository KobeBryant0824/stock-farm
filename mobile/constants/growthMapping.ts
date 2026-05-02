export type PlantStatus =
  | "empty"
  | "seed"
  | "sprout"
  | "seedling"
  | "sapling"
  | "tree"
  | "full_tree";

export interface GrowthStage {
  status: PlantStatus;
  label: string;
  emoji: string;        // 占位符，正式版换成图片资源
  minReturnPct: number; // 达到此状态所需最低涨幅
}

export const GROWTH_STAGES: GrowthStage[] = [
  { status: "seed",      label: "种子",     emoji: "🌰", minReturnPct: -Infinity },
  { status: "sprout",    label: "发芽了",   emoji: "🌱", minReturnPct: 0 },
  { status: "seedling",  label: "小树苗",   emoji: "🌿", minReturnPct: 2 },
  { status: "sapling",   label: "树苗",     emoji: "🌳", minReturnPct: 5 },
  { status: "tree",      label: "大树",     emoji: "🌲", minReturnPct: 10 },
  { status: "full_tree", label: "参天大树", emoji: "🎋", minReturnPct: 20 },
];

export const STAGE_INDEX: Record<PlantStatus, number> = {
  empty:     -1,
  seed:       0,
  sprout:     1,
  seedling:   2,
  sapling:    3,
  tree:       4,
  full_tree:  5,
};

/** 植物高度（px），供动画插值用 */
export const STAGE_HEIGHT: Record<PlantStatus, number> = {
  empty:      0,
  seed:       8,
  sprout:     24,
  seedling:   48,
  sapling:    72,
  tree:       96,
  full_tree: 120,
};

export const HARVEST_THRESHOLD_PCT = 20;

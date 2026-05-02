import { Tabs } from "expo-router";

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: "#2e7d32",
        headerShown: false,
      }}
    >
      <Tabs.Screen
        name="farm"
        options={{ title: "农场", tabBarIcon: () => null }}
      />
      <Tabs.Screen
        name="market"
        options={{ title: "选股", tabBarIcon: () => null }}
      />
    </Tabs>
  );
}

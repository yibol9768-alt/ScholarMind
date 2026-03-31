import { Stack } from "expo-router";

export default function TaskLayout() {
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="index" />
      <Stack.Screen name="logs" />
      <Stack.Screen name="review" />
    </Stack>
  );
}

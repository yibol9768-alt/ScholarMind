import { useEffect, useCallback, useState } from "react";
import {
  Text,
  View,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";
import { useTaskContext } from "@/lib/task-store";
import type { LogEntry, ModuleId } from "@/lib/types";
import { MODULE_NAMES } from "@/lib/types";

const LEVEL_CONFIG = {
  info: { color: "#3b82f6", bgColor: "#eff6ff", icon: "info-outline" },
  warn: { color: "#f59e0b", bgColor: "#fffbeb", icon: "warning-amber" },
  error: { color: "#ef4444", bgColor: "#fef2f2", icon: "error-outline" },
};

const MODULE_COLORS: Record<string, string> = {
  M1: "#10a37f", M2: "#6366f1", M3: "#f59e0b", M4: "#3b82f6",
  M5: "#ec4899", M6: "#8b5cf6", M7: "#06b6d4", M8: "#22c55e",
  M9: "#ef4444", system: "#94a3b8",
};

function LogItem({ entry }: { entry: LogEntry }) {
  const colors = useColors();
  const levelConfig = LEVEL_CONFIG[entry.level];
  const moduleColor = MODULE_COLORS[entry.module_id] || "#94a3b8";
  const time = new Date(entry.timestamp).toLocaleTimeString("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

  return (
    <View style={[styles.logItem, { borderLeftColor: levelConfig.color }]}>
      <View style={styles.logHeader}>
        <View style={[styles.moduleTag, { backgroundColor: moduleColor + "20" }]}>
          <Text style={[styles.moduleTagText, { color: moduleColor }]}>
            {entry.module_id === "system"
              ? "SYS"
              : `${entry.module_id} ${MODULE_NAMES[entry.module_id as ModuleId] || ""}`}
          </Text>
        </View>
        <View style={[styles.levelBadge, { backgroundColor: levelConfig.bgColor }]}>
          <MaterialIcons name={levelConfig.icon as any} size={11} color={levelConfig.color} />
          <Text style={[styles.levelText, { color: levelConfig.color }]}>
            {entry.level.toUpperCase()}
          </Text>
        </View>
        <Text style={[styles.timeText, { color: colors.muted }]}>{time}</Text>
      </View>
      <Text style={[styles.logMessage, { color: colors.foreground }]}>{entry.message}</Text>
    </View>
  );
}

export default function LogsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const colors = useColors();
  const { state, fetchLogs } = useTaskContext();
  const [filter, setFilter] = useState<"all" | "info" | "warn" | "error">("all");
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (id) fetchLogs(id);
  }, [id, fetchLogs]);

  const onRefresh = useCallback(async () => {
    if (!id) return;
    setRefreshing(true);
    await fetchLogs(id);
    setRefreshing(false);
  }, [id, fetchLogs]);

  const filteredLogs =
    filter === "all" ? state.logs : state.logs.filter((l) => l.level === filter);

  const renderItem = useCallback(
    ({ item }: { item: LogEntry }) => <LogItem entry={item} />,
    []
  );

  return (
    <ScreenContainer>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <MaterialIcons name="arrow-back" size={22} color={colors.foreground} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: colors.foreground }]}>执行日志</Text>
        <View style={{ width: 36 }} />
      </View>

      {/* Filter Bar */}
      <View style={styles.filterBar}>
        {(["all", "info", "warn", "error"] as const).map((lvl) => {
          const count = lvl === "all" ? state.logs.length : state.logs.filter((l) => l.level === lvl).length;
          const isActive = filter === lvl;
          const color = lvl === "all" ? "#10a37f" : LEVEL_CONFIG[lvl]?.color || "#10a37f";
          return (
            <TouchableOpacity
              key={lvl}
              onPress={() => setFilter(lvl)}
              style={[
                styles.filterChip,
                isActive
                  ? { backgroundColor: color, borderColor: color }
                  : { backgroundColor: colors.surface, borderColor: colors.border },
              ]}
            >
              <Text style={[styles.filterChipText, { color: isActive ? "#fff" : colors.muted }]}>
                {lvl === "all" ? "全部" : lvl.toUpperCase()}
                {count > 0 ? ` ${count}` : ""}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {state.loading && state.logs.length === 0 ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#10a37f" />
        </View>
      ) : filteredLogs.length === 0 ? (
        <View style={styles.centerContainer}>
          <MaterialIcons name="article" size={48} color={colors.border} />
          <Text style={[styles.emptyText, { color: colors.muted }]}>暂无日志记录</Text>
        </View>
      ) : (
        <FlatList
          data={filteredLogs}
          renderItem={renderItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
          onRefresh={onRefresh}
          refreshing={refreshing}
          ListHeaderComponent={
            <Text style={[styles.logCount, { color: colors.muted }]}>
              共 {filteredLogs.length} 条日志
            </Text>
          }
        />
      )}
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  backButton: {
    width: 36,
    height: 36,
    alignItems: "center",
    justifyContent: "center",
  },
  headerTitle: {
    fontSize: 17,
    fontWeight: "600",
  },
  filterBar: {
    flexDirection: "row",
    paddingHorizontal: 16,
    paddingBottom: 12,
    gap: 8,
  },
  filterChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
  },
  filterChipText: {
    fontSize: 12,
    fontWeight: "500",
  },
  centerContainer: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
  },
  emptyText: {
    fontSize: 14,
  },
  listContent: {
    paddingHorizontal: 16,
    paddingBottom: 32,
  },
  logCount: {
    fontSize: 12,
    marginBottom: 8,
  },
  logItem: {
    borderLeftWidth: 3,
    paddingLeft: 10,
    paddingVertical: 8,
    marginBottom: 6,
    gap: 4,
  },
  logHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    flexWrap: "wrap",
  },
  moduleTag: {
    paddingHorizontal: 7,
    paddingVertical: 2,
    borderRadius: 6,
  },
  moduleTagText: {
    fontSize: 10,
    fontWeight: "600",
  },
  levelBadge: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 6,
    gap: 3,
  },
  levelText: {
    fontSize: 10,
    fontWeight: "700",
  },
  timeText: {
    fontSize: 10,
    marginLeft: "auto",
  },
  logMessage: {
    fontSize: 13,
    lineHeight: 18,
  },
});

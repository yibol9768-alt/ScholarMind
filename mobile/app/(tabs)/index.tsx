import { useEffect, useState, useCallback, useMemo } from "react";
import {
  Text,
  View,
  FlatList,
  TextInput,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  StyleSheet,
  Platform,
} from "react-native";
import { useRouter } from "expo-router";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import { LinearGradient } from "expo-linear-gradient";
import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";
import { useTaskContext } from "@/lib/task-store";
import { isDemoMode } from "@/lib/api";
import type { Task, TaskStatus, ModuleId } from "@/lib/types";
import { MODULE_NAMES } from "@/lib/types";

const STATUS_CONFIG: Record<
  TaskStatus,
  { label: string; color: string; bgColor: string; icon: string }
> = {
  pending: { label: "等待中", color: "#94a3b8", bgColor: "#f1f5f9", icon: "schedule" },
  running: { label: "运行中", color: "#10a37f", bgColor: "#ecfdf5", icon: "play-circle-filled" },
  paused: { label: "已暂停", color: "#f59e0b", bgColor: "#fffbeb", icon: "pause-circle-filled" },
  review: { label: "待审阅", color: "#6366f1", bgColor: "#eef2ff", icon: "rate-review" },
  completed: { label: "已完成", color: "#22c55e", bgColor: "#f0fdf4", icon: "check-circle" },
  failed: { label: "已失败", color: "#ef4444", bgColor: "#fef2f2", icon: "error" },
  aborted: { label: "已终止", color: "#94a3b8", bgColor: "#f8fafc", icon: "cancel" },
};

const FILTER_OPTIONS: { key: string; label: string; icon: string }[] = [
  { key: "all", label: "全部", icon: "apps" },
  { key: "running", label: "运行中", icon: "play-arrow" },
  { key: "completed", label: "已完成", icon: "check" },
  { key: "failed", label: "失败", icon: "close" },
];

function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: string;
  label: string;
  value: number;
  color: string;
}) {
  return (
    <View style={styles.statCard}>
      <View style={[styles.statIconWrap, { backgroundColor: color + "20" }]}>
        <MaterialIcons name={icon as any} size={16} color={color} />
      </View>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

function TaskCard({ task, onPress }: { task: Task; onPress: () => void }) {
  const colors = useColors();
  const completedModules = task.modules.filter(
    (m) => m.status === "completed"
  ).length;
  const totalModules = task.modules.length;
  const progress = totalModules > 0 ? completedModules / totalModules : 0;
  const currentModule = task.modules.find((m) => m.status === "running");
  const statusConfig = STATUS_CONFIG[task.status] || STATUS_CONFIG.pending;

  return (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={0.65}
      style={[styles.taskCard, { backgroundColor: colors.surface, borderColor: colors.border }]}
    >
      <View style={[styles.cardAccent, { backgroundColor: statusConfig.color }]} />
      <View style={styles.taskCardInner}>
        <View style={styles.taskCardHeader}>
          <View style={[styles.taskIconWrap, { backgroundColor: statusConfig.bgColor }]}>
            <MaterialIcons
              name={statusConfig.icon as any}
              size={18}
              color={statusConfig.color}
            />
          </View>
          <View style={styles.taskCardTitleArea}>
            <Text
              style={[styles.taskTitle, { color: colors.foreground }]}
              numberOfLines={1}
            >
              {task.title}
            </Text>
            <View
              style={[styles.statusBadge, { backgroundColor: statusConfig.bgColor }]}
            >
              <View style={[styles.statusDot, { backgroundColor: statusConfig.color }]} />
              <Text style={[styles.statusText, { color: statusConfig.color }]}>
                {statusConfig.label}
              </Text>
            </View>
          </View>
        </View>

        <Text
          style={[styles.taskTopic, { color: colors.muted }]}
          numberOfLines={2}
        >
          {task.topic}
        </Text>

        {task.status === "running" && currentModule && (
          <View style={styles.runningInfo}>
            <View style={styles.progressRow}>
              <Text style={[styles.progressLabel, { color: colors.muted }]}>
                {MODULE_NAMES[currentModule.module_id as ModuleId]}
              </Text>
              <Text style={styles.progressPercent}>{currentModule.percent}%</Text>
            </View>
            <View style={[styles.progressBarBg, { backgroundColor: colors.border + "60" }]}>
              <LinearGradient
                colors={["#10a37f", "#34d399"]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={[styles.progressBarFill, { width: `${progress * 100}%` as any }]}
              />
            </View>
          </View>
        )}

        {task.status === "completed" && (
          <View style={styles.completedInfo}>
            <View style={styles.completedBadge}>
              <MaterialIcons name="check-circle" size={13} color="#22c55e" />
              <Text style={styles.completedText}>
                {completedModules}/{totalModules} 模块完成
              </Text>
            </View>
          </View>
        )}

        <View style={[styles.taskCardFooter, { borderTopColor: colors.border + "40" }]}>
          <View style={styles.footerLeft}>
            <MaterialIcons name="schedule" size={12} color={colors.muted} />
            <Text style={[styles.timeText, { color: colors.muted }]}>
              {new Date(task.created_at).toLocaleDateString("zh-CN", {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </Text>
          </View>
          <View style={styles.viewBtn}>
            <Text style={styles.viewBtnText}>查看详情</Text>
            <MaterialIcons name="arrow-forward" size={12} color="#10a37f" />
          </View>
        </View>
      </View>
    </TouchableOpacity>
  );
}

export default function HomeScreen() {
  const colors = useColors();
  const router = useRouter();
  const { state, fetchTasks } = useTaskContext();
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchTasks();
    setRefreshing(false);
  }, [fetchTasks]);

  const filteredTasks = useMemo(() => {
    let list = state.tasks;
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (t) =>
          t.title.toLowerCase().includes(q) ||
          t.topic.toLowerCase().includes(q)
      );
    }
    if (filter !== "all") {
      list = list.filter((t) => t.status === filter);
    }
    return list;
  }, [state.tasks, search, filter]);

  const stats = useMemo(() => {
    const tasks = state.tasks;
    return {
      total: tasks.length,
      running: tasks.filter((t) => t.status === "running").length,
      completed: tasks.filter((t) => t.status === "completed").length,
    };
  }, [state.tasks]);

  const renderItem = useCallback(
    ({ item }: { item: Task }) => (
      <TaskCard
        task={item}
        onPress={() => router.push(`/task/${item.id}` as any)}
      />
    ),
    [router]
  );

  if (state.loading && state.tasks.length === 0) {
    return (
      <ScreenContainer>
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#10a37f" />
          <Text style={[styles.loadingText, { color: colors.muted }]}>
            加载中...
          </Text>
        </View>
      </ScreenContainer>
    );
  }

  return (
    <ScreenContainer>
      <FlatList
        data={filteredTasks}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor="#10a37f"
          />
        }
        ListHeaderComponent={
          <View style={styles.listHeader}>
            {/* Hero Section */}
            <LinearGradient
              colors={["#10a37f", "#0d8c6d", "#086b54"]}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={styles.heroBg}
            >
              <View style={styles.heroContent}>
                <View style={styles.heroTextArea}>
                  <Text style={styles.heroGreeting}>ScholarMind</Text>
                  <Text style={styles.heroSubtitle}>AI 驱动的自动化科研助手</Text>
                </View>
                {isDemoMode() && (
                  <View style={styles.demoBadge}>
                    <MaterialIcons name="science" size={12} color="#fff" />
                    <Text style={styles.demoBadgeText}>演示</Text>
                  </View>
                )}
              </View>
              <View style={styles.statsRow}>
                <StatCard icon="science" label="总任务" value={stats.total} color="#3b82f6" />
                <StatCard icon="play-circle-filled" label="运行中" value={stats.running} color="#10a37f" />
                <StatCard icon="check-circle" label="已完成" value={stats.completed} color="#22c55e" />
              </View>
            </LinearGradient>

            {/* Search */}
            <View style={styles.searchSection}>
              <View
                style={[styles.searchBar, { backgroundColor: colors.surface, borderColor: colors.border }]}
              >
                <MaterialIcons name="search" size={20} color={colors.muted} />
                <TextInput
                  style={[styles.searchInput, { color: colors.foreground }]}
                  placeholder="搜索研究任务..."
                  placeholderTextColor={colors.muted}
                  value={search}
                  onChangeText={setSearch}
                  returnKeyType="done"
                />
                {search.length > 0 && (
                  <TouchableOpacity onPress={() => setSearch("")} style={styles.clearBtn}>
                    <MaterialIcons name="close" size={16} color={colors.muted} />
                  </TouchableOpacity>
                )}
              </View>
            </View>

            {/* Filter */}
            <View style={styles.filterRow}>
              {FILTER_OPTIONS.map((opt) => (
                <TouchableOpacity
                  key={opt.key}
                  onPress={() => setFilter(opt.key)}
                  style={[
                    styles.filterChip,
                    filter === opt.key
                      ? { backgroundColor: "#10a37f", borderColor: "#10a37f" }
                      : { backgroundColor: colors.surface, borderColor: colors.border },
                  ]}
                >
                  <MaterialIcons
                    name={opt.icon as any}
                    size={13}
                    color={filter === opt.key ? "#fff" : colors.muted}
                  />
                  <Text
                    style={[
                      styles.filterChipText,
                      filter === opt.key ? { color: "#fff" } : { color: colors.muted },
                    ]}
                  >
                    {opt.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            {filteredTasks.length === 0 && !state.loading && (
              <View style={styles.emptyState}>
                <MaterialIcons name="science" size={48} color={colors.border} />
                <Text style={[styles.emptyTitle, { color: colors.foreground }]}>
                  暂无研究任务
                </Text>
                <Text style={[styles.emptyDesc, { color: colors.muted }]}>
                  {search ? "没有匹配的任务" : "点击「新建」开始你的第一个研究任务"}
                </Text>
              </View>
            )}
          </View>
        }
        contentContainerStyle={styles.listContent}
      />
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  centerContainer: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
  },
  loadingText: {
    fontSize: 14,
  },
  listHeader: {
    gap: 0,
  },
  listContent: {
    paddingBottom: 24,
  },
  heroBg: {
    paddingTop: 20,
    paddingBottom: 24,
    paddingHorizontal: 16,
  },
  heroContent: {
    flexDirection: "row",
    alignItems: "flex-start",
    justifyContent: "space-between",
    marginBottom: 16,
  },
  heroTextArea: {
    flex: 1,
  },
  heroGreeting: {
    fontSize: 26,
    fontWeight: "800",
    color: "#fff",
    letterSpacing: -0.5,
  },
  heroSubtitle: {
    fontSize: 13,
    color: "rgba(255,255,255,0.8)",
    marginTop: 2,
  },
  demoBadge: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "rgba(255,255,255,0.2)",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 20,
    gap: 4,
  },
  demoBadgeText: {
    fontSize: 11,
    fontWeight: "600",
    color: "#fff",
  },
  statsRow: {
    flexDirection: "row",
    gap: 10,
  },
  statCard: {
    flex: 1,
    backgroundColor: "rgba(255,255,255,0.15)",
    borderRadius: 12,
    padding: 10,
    alignItems: "center",
    gap: 4,
  },
  statIconWrap: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
  },
  statValue: {
    fontSize: 20,
    fontWeight: "700",
    color: "#fff",
  },
  statLabel: {
    fontSize: 11,
    color: "rgba(255,255,255,0.8)",
  },
  searchSection: {
    paddingHorizontal: 16,
    paddingTop: 14,
    paddingBottom: 8,
  },
  searchBar: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 12,
    borderWidth: 1,
    gap: 8,
  },
  searchInput: {
    flex: 1,
    fontSize: 14,
    paddingVertical: 0,
  },
  clearBtn: {
    padding: 2,
  },
  filterRow: {
    flexDirection: "row",
    paddingHorizontal: 16,
    paddingBottom: 12,
    gap: 8,
  },
  filterChip: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
    gap: 4,
  },
  filterChipText: {
    fontSize: 12,
    fontWeight: "500",
  },
  emptyState: {
    alignItems: "center",
    paddingVertical: 48,
    paddingHorizontal: 32,
    gap: 8,
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: "600",
    marginTop: 8,
  },
  emptyDesc: {
    fontSize: 13,
    textAlign: "center",
    lineHeight: 18,
  },
  taskCard: {
    marginHorizontal: 16,
    marginBottom: 12,
    borderRadius: 16,
    borderWidth: 1,
    overflow: "hidden",
    flexDirection: "row",
  },
  cardAccent: {
    width: 4,
  },
  taskCardInner: {
    flex: 1,
    padding: 14,
    gap: 8,
  },
  taskCardHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  taskIconWrap: {
    width: 36,
    height: 36,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
  },
  taskCardTitleArea: {
    flex: 1,
    gap: 4,
  },
  taskTitle: {
    fontSize: 15,
    fontWeight: "600",
    lineHeight: 20,
  },
  statusBadge: {
    flexDirection: "row",
    alignItems: "center",
    alignSelf: "flex-start",
    paddingHorizontal: 7,
    paddingVertical: 2,
    borderRadius: 10,
    gap: 4,
  },
  statusDot: {
    width: 5,
    height: 5,
    borderRadius: 2.5,
  },
  statusText: {
    fontSize: 11,
    fontWeight: "500",
  },
  taskTopic: {
    fontSize: 13,
    lineHeight: 18,
  },
  runningInfo: {
    gap: 4,
  },
  progressRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  progressLabel: {
    fontSize: 11,
  },
  progressPercent: {
    fontSize: 11,
    fontWeight: "600",
    color: "#10a37f",
  },
  progressBarBg: {
    height: 4,
    borderRadius: 2,
    overflow: "hidden",
  },
  progressBarFill: {
    height: "100%",
    borderRadius: 2,
  },
  completedInfo: {
    flexDirection: "row",
  },
  completedBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  completedText: {
    fontSize: 12,
    color: "#22c55e",
    fontWeight: "500",
  },
  taskCardFooter: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingTop: 8,
    borderTopWidth: 0.5,
  },
  footerLeft: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  timeText: {
    fontSize: 11,
  },
  viewBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 2,
  },
  viewBtnText: {
    fontSize: 12,
    fontWeight: "500",
    color: "#10a37f",
  },
});

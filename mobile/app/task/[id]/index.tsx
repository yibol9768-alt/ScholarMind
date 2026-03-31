import { useEffect, useState, useCallback } from "react";
import {
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  StyleSheet,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import { LinearGradient } from "expo-linear-gradient";
import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";
import { useTaskContext } from "@/lib/task-store";
import { DEMO_MODULE_IO } from "@/lib/mock-data";
import type { ModuleId, ModuleStatus, TaskStatus } from "@/lib/types";
import { MODULE_NAMES } from "@/lib/types";

const STATUS_CONFIG: Record<TaskStatus, { label: string; color: string; bgColor: string; icon: string }> = {
  pending: { label: "等待中", color: "#94a3b8", bgColor: "#f1f5f9", icon: "schedule" },
  running: { label: "运行中", color: "#10a37f", bgColor: "#ecfdf5", icon: "play-circle-filled" },
  paused: { label: "已暂停", color: "#f59e0b", bgColor: "#fffbeb", icon: "pause-circle-filled" },
  review: { label: "待审阅", color: "#6366f1", bgColor: "#eef2ff", icon: "rate-review" },
  completed: { label: "已完成", color: "#22c55e", bgColor: "#f0fdf4", icon: "check-circle" },
  failed: { label: "已失败", color: "#ef4444", bgColor: "#fef2f2", icon: "error" },
  aborted: { label: "已终止", color: "#94a3b8", bgColor: "#f8fafc", icon: "cancel" },
};

const MODULE_STATUS_CONFIG: Record<ModuleStatus, { color: string; bgColor: string; icon: string }> = {
  waiting: { color: "#94a3b8", bgColor: "#f1f5f9", icon: "radio-button-unchecked" },
  running: { color: "#10a37f", bgColor: "#ecfdf5", icon: "play-circle-outline" },
  completed: { color: "#22c55e", bgColor: "#f0fdf4", icon: "check-circle-outline" },
  failed: { color: "#ef4444", bgColor: "#fef2f2", icon: "error-outline" },
  skipped: { color: "#94a3b8", bgColor: "#f8fafc", icon: "remove-circle-outline" },
};

export default function TaskDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const colors = useColors();
  const { state, fetchTask, pauseTask, resumeTask, abortTask } = useTaskContext();
  const [expandedModules, setExpandedModules] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (id) fetchTask(id);
  }, [id, fetchTask]);

  const task = state.currentTask;

  const toggleModule = useCallback((moduleId: string) => {
    setExpandedModules((prev) => {
      const next = new Set(prev);
      if (next.has(moduleId)) {
        next.delete(moduleId);
      } else {
        next.add(moduleId);
      }
      return next;
    });
  }, []);

  const handlePause = useCallback(async () => {
    if (!task) return;
    try {
      await pauseTask(task.id);
    } catch {
      Alert.alert("操作失败", "暂停任务时出错");
    }
  }, [task, pauseTask]);

  const handleResume = useCallback(async () => {
    if (!task) return;
    try {
      await resumeTask(task.id);
    } catch {
      Alert.alert("操作失败", "恢复任务时出错");
    }
  }, [task, resumeTask]);

  const handleAbort = useCallback(() => {
    if (!task) return;
    Alert.alert(
      "终止任务",
      "确定要终止这个研究任务吗？此操作不可撤销。",
      [
        { text: "取消", style: "cancel" },
        {
          text: "终止",
          style: "destructive",
          onPress: async () => {
            try {
              await abortTask(task.id);
            } catch {
              Alert.alert("操作失败", "终止任务时出错");
            }
          },
        },
      ]
    );
  }, [task, abortTask]);

  if (state.loading && !task) {
    return (
      <ScreenContainer>
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#10a37f" />
          <Text style={[styles.loadingText, { color: colors.muted }]}>加载中...</Text>
        </View>
      </ScreenContainer>
    );
  }

  if (!task) {
    return (
      <ScreenContainer>
        <View style={styles.centerContainer}>
          <MaterialIcons name="error-outline" size={48} color={colors.border} />
          <Text style={[styles.errorText, { color: colors.foreground }]}>任务不存在</Text>
          <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
            <Text style={styles.backBtnText}>返回</Text>
          </TouchableOpacity>
        </View>
      </ScreenContainer>
    );
  }

  const statusConfig = STATUS_CONFIG[task.status] || STATUS_CONFIG.pending;
  const completedModules = task.modules.filter((m) => m.status === "completed").length;
  const totalModules = task.modules.length;
  const overallProgress = totalModules > 0 ? completedModules / totalModules : 0;

  return (
    <ScreenContainer>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <MaterialIcons name="arrow-back" size={22} color={colors.foreground} />
          </TouchableOpacity>
          <Text style={[styles.headerTitle, { color: colors.foreground }]} numberOfLines={1}>
            任务详情
          </Text>
          <View style={{ width: 36 }} />
        </View>

        {/* Task Info Card */}
        <View style={[styles.taskInfoCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <View style={styles.taskInfoHeader}>
            <View style={[styles.taskStatusIcon, { backgroundColor: statusConfig.bgColor }]}>
              <MaterialIcons name={statusConfig.icon as any} size={22} color={statusConfig.color} />
            </View>
            <View style={styles.taskInfoText}>
              <Text style={[styles.taskTitle, { color: colors.foreground }]} numberOfLines={2}>
                {task.title}
              </Text>
              <View style={[styles.statusBadge, { backgroundColor: statusConfig.bgColor }]}>
                <View style={[styles.statusDot, { backgroundColor: statusConfig.color }]} />
                <Text style={[styles.statusLabel, { color: statusConfig.color }]}>
                  {statusConfig.label}
                </Text>
              </View>
            </View>
          </View>

          <Text style={[styles.taskTopic, { color: colors.muted }]}>{task.topic}</Text>

          {task.description && (
            <Text style={[styles.taskDesc, { color: colors.muted }]}>{task.description}</Text>
          )}

          {/* Progress Bar */}
          <View style={styles.progressSection}>
            <View style={styles.progressHeader}>
              <Text style={[styles.progressLabel, { color: colors.muted }]}>
                总进度 {completedModules}/{totalModules} 模块
              </Text>
              <Text style={[styles.progressPercent, { color: "#10a37f" }]}>
                {Math.round(overallProgress * 100)}%
              </Text>
            </View>
            <View style={[styles.progressBarBg, { backgroundColor: colors.border + "60" }]}>
              <LinearGradient
                colors={["#10a37f", "#34d399"]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={[styles.progressBarFill, { width: `${overallProgress * 100}%` as any }]}
              />
            </View>
          </View>

          <View style={styles.taskMeta}>
            <MaterialIcons name="schedule" size={13} color={colors.muted} />
            <Text style={[styles.taskMetaText, { color: colors.muted }]}>
              创建于 {new Date(task.created_at).toLocaleString("zh-CN")}
            </Text>
          </View>
        </View>

        {/* Action Buttons */}
        {(task.status === "running" || task.status === "paused") && (
          <View style={styles.actionRow}>
            {task.status === "running" ? (
              <TouchableOpacity onPress={handlePause} style={[styles.actionBtn, styles.pauseBtn]}>
                <MaterialIcons name="pause" size={18} color="#f59e0b" />
                <Text style={[styles.actionBtnText, { color: "#f59e0b" }]}>暂停</Text>
              </TouchableOpacity>
            ) : (
              <TouchableOpacity onPress={handleResume} style={[styles.actionBtn, styles.resumeBtn]}>
                <MaterialIcons name="play-arrow" size={18} color="#10a37f" />
                <Text style={[styles.actionBtnText, { color: "#10a37f" }]}>恢复</Text>
              </TouchableOpacity>
            )}
            <TouchableOpacity onPress={handleAbort} style={[styles.actionBtn, styles.abortBtn]}>
              <MaterialIcons name="stop" size={18} color="#ef4444" />
              <Text style={[styles.actionBtnText, { color: "#ef4444" }]}>终止</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Quick Links */}
        <View style={styles.quickLinks}>
          <TouchableOpacity
            onPress={() => router.push(`/task/${task.id}/logs` as any)}
            style={[styles.quickLinkCard, { backgroundColor: colors.surface, borderColor: colors.border }]}
          >
            <View style={[styles.quickLinkIcon, { backgroundColor: "#3b82f615" }]}>
              <MaterialIcons name="article" size={20} color="#3b82f6" />
            </View>
            <View style={styles.quickLinkText}>
              <Text style={[styles.quickLinkTitle, { color: colors.foreground }]}>查看日志</Text>
              <Text style={[styles.quickLinkDesc, { color: colors.muted }]}>追溯每个模块的执行日志</Text>
            </View>
            <MaterialIcons name="chevron-right" size={20} color={colors.muted} />
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => router.push(`/task/${task.id}/review` as any)}
            style={[styles.quickLinkCard, { backgroundColor: colors.surface, borderColor: colors.border }]}
          >
            <View style={[styles.quickLinkIcon, { backgroundColor: "#6366f115" }]}>
              <MaterialIcons name="rate-review" size={20} color="#6366f1" />
            </View>
            <View style={styles.quickLinkText}>
              <Text style={[styles.quickLinkTitle, { color: colors.foreground }]}>评审结果</Text>
              <Text style={[styles.quickLinkDesc, { color: colors.muted }]}>NeurIPS 风格学术评审报告</Text>
            </View>
            <MaterialIcons name="chevron-right" size={20} color={colors.muted} />
          </TouchableOpacity>
        </View>

        {/* Pipeline */}
        <View style={styles.pipelineSection}>
          <Text style={[styles.pipelineTitle, { color: colors.foreground }]}>研究流水线</Text>
          <Text style={[styles.pipelineSubtitle, { color: colors.muted }]}>
            点击模块查看详细信息
          </Text>

          <View style={styles.pipeline}>
            {task.modules.map((mod, idx) => {
              const mConfig = MODULE_STATUS_CONFIG[mod.status];
              const isExpanded = expandedModules.has(mod.module_id);
              const ioDetail = DEMO_MODULE_IO.find((d) => d.moduleId === mod.module_id);

              return (
                <View key={mod.module_id}>
                  <TouchableOpacity
                    onPress={() => toggleModule(mod.module_id)}
                    style={[
                      styles.moduleRow,
                      { backgroundColor: colors.surface, borderColor: colors.border },
                      mod.status === "running" && { borderColor: "#10a37f" },
                    ]}
                    activeOpacity={0.7}
                  >
                    {/* Timeline connector */}
                    {idx < task.modules.length - 1 && (
                      <View
                        style={[
                          styles.connector,
                          { backgroundColor: mod.status === "completed" ? "#10a37f" : colors.border },
                        ]}
                      />
                    )}

                    <View style={[styles.moduleIcon, { backgroundColor: mConfig.bgColor }]}>
                      <MaterialIcons name={mConfig.icon as any} size={18} color={mConfig.color} />
                    </View>

                    <View style={styles.moduleInfo}>
                      <View style={styles.moduleHeader}>
                        <Text style={[styles.moduleId, { color: mConfig.color }]}>
                          {mod.module_id}
                        </Text>
                        <Text style={[styles.moduleName, { color: colors.foreground }]}>
                          {MODULE_NAMES[mod.module_id as ModuleId]}
                        </Text>
                      </View>
                      <Text style={[styles.moduleMessage, { color: colors.muted }]} numberOfLines={1}>
                        {mod.message}
                      </Text>
                      {mod.status === "running" && (
                        <View style={styles.moduleProgressRow}>
                          <View style={[styles.moduleProgressBg, { backgroundColor: colors.border + "60" }]}>
                            <View
                              style={[
                                styles.moduleProgressFill,
                                { width: `${mod.percent}%` as any, backgroundColor: "#10a37f" },
                              ]}
                            />
                          </View>
                          <Text style={styles.modulePercent}>{mod.percent}%</Text>
                        </View>
                      )}
                    </View>

                    <MaterialIcons
                      name={isExpanded ? "expand-less" : "expand-more"}
                      size={18}
                      color={colors.muted}
                    />
                  </TouchableOpacity>

                  {/* Expanded Detail */}
                  {isExpanded && ioDetail && (
                    <View style={[styles.moduleDetail, { backgroundColor: colors.background, borderColor: colors.border }]}>
                      <View style={styles.detailRow}>
                        <Text style={[styles.detailLabel, { color: colors.muted }]}>输入</Text>
                        <Text style={[styles.detailValue, { color: colors.foreground }]}>{ioDetail.input}</Text>
                      </View>
                      <View style={[styles.detailDivider, { backgroundColor: colors.border }]} />
                      <View style={styles.detailRow}>
                        <Text style={[styles.detailLabel, { color: colors.muted }]}>输出</Text>
                        <Text style={[styles.detailValue, { color: colors.foreground }]}>{ioDetail.output}</Text>
                      </View>
                      {ioDetail.keyFindings && ioDetail.keyFindings.length > 0 && (
                        <>
                          <View style={[styles.detailDivider, { backgroundColor: colors.border }]} />
                          <View style={styles.detailRow}>
                            <Text style={[styles.detailLabel, { color: colors.muted }]}>关键发现</Text>
                            <View style={styles.findingsList}>
                              {ioDetail.keyFindings.map((f, i) => (
                                <View key={i} style={styles.findingItem}>
                                  <View style={[styles.findingDot, { backgroundColor: "#10a37f" }]} />
                                  <Text style={[styles.findingText, { color: colors.foreground }]}>{f}</Text>
                                </View>
                              ))}
                            </View>
                          </View>
                        </>
                      )}
                      <View style={[styles.detailDivider, { backgroundColor: colors.border }]} />
                      <View style={styles.detailRow}>
                        <Text style={[styles.detailLabel, { color: colors.muted }]}>预计耗时</Text>
                        <Text style={[styles.detailValue, { color: colors.foreground }]}>{ioDetail.duration}</Text>
                      </View>
                    </View>
                  )}
                </View>
              );
            })}
          </View>
        </View>
      </ScrollView>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  scrollContent: {
    paddingBottom: 40,
  },
  centerContainer: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
  },
  loadingText: {
    fontSize: 14,
  },
  errorText: {
    fontSize: 16,
    fontWeight: "600",
  },
  backBtn: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    backgroundColor: "#10a37f",
    borderRadius: 12,
  },
  backBtnText: {
    color: "#fff",
    fontWeight: "600",
  },
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
  taskInfoCard: {
    marginHorizontal: 16,
    borderRadius: 16,
    borderWidth: 1,
    padding: 16,
    gap: 10,
    marginBottom: 12,
  },
  taskInfoHeader: {
    flexDirection: "row",
    gap: 12,
    alignItems: "flex-start",
  },
  taskStatusIcon: {
    width: 44,
    height: 44,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
  },
  taskInfoText: {
    flex: 1,
    gap: 6,
  },
  taskTitle: {
    fontSize: 17,
    fontWeight: "700",
    lineHeight: 22,
  },
  statusBadge: {
    flexDirection: "row",
    alignItems: "center",
    alignSelf: "flex-start",
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10,
    gap: 4,
  },
  statusDot: {
    width: 5,
    height: 5,
    borderRadius: 2.5,
  },
  statusLabel: {
    fontSize: 12,
    fontWeight: "500",
  },
  taskTopic: {
    fontSize: 14,
    lineHeight: 20,
  },
  taskDesc: {
    fontSize: 12,
    lineHeight: 17,
  },
  progressSection: {
    gap: 6,
  },
  progressHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  progressLabel: {
    fontSize: 12,
  },
  progressPercent: {
    fontSize: 12,
    fontWeight: "600",
  },
  progressBarBg: {
    height: 6,
    borderRadius: 3,
    overflow: "hidden",
  },
  progressBarFill: {
    height: "100%",
    borderRadius: 3,
  },
  taskMeta: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  taskMetaText: {
    fontSize: 12,
  },
  actionRow: {
    flexDirection: "row",
    marginHorizontal: 16,
    gap: 10,
    marginBottom: 12,
  },
  actionBtn: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 10,
    borderRadius: 12,
    borderWidth: 1.5,
    gap: 6,
  },
  pauseBtn: {
    borderColor: "#f59e0b",
    backgroundColor: "#fffbeb",
  },
  resumeBtn: {
    borderColor: "#10a37f",
    backgroundColor: "#ecfdf5",
  },
  abortBtn: {
    borderColor: "#ef4444",
    backgroundColor: "#fef2f2",
  },
  actionBtnText: {
    fontSize: 14,
    fontWeight: "600",
  },
  quickLinks: {
    marginHorizontal: 16,
    gap: 8,
    marginBottom: 20,
  },
  quickLinkCard: {
    flexDirection: "row",
    alignItems: "center",
    padding: 14,
    borderRadius: 14,
    borderWidth: 1,
    gap: 12,
  },
  quickLinkIcon: {
    width: 40,
    height: 40,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
  },
  quickLinkText: {
    flex: 1,
    gap: 2,
  },
  quickLinkTitle: {
    fontSize: 14,
    fontWeight: "600",
  },
  quickLinkDesc: {
    fontSize: 12,
  },
  pipelineSection: {
    paddingHorizontal: 16,
  },
  pipelineTitle: {
    fontSize: 17,
    fontWeight: "700",
    marginBottom: 2,
  },
  pipelineSubtitle: {
    fontSize: 12,
    marginBottom: 14,
  },
  pipeline: {
    gap: 0,
  },
  moduleRow: {
    flexDirection: "row",
    alignItems: "center",
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 8,
    gap: 10,
    position: "relative",
  },
  connector: {
    position: "absolute",
    left: 24,
    bottom: -8,
    width: 2,
    height: 8,
    zIndex: 1,
  },
  moduleIcon: {
    width: 36,
    height: 36,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
  },
  moduleInfo: {
    flex: 1,
    gap: 3,
  },
  moduleHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  moduleId: {
    fontSize: 12,
    fontWeight: "700",
  },
  moduleName: {
    fontSize: 14,
    fontWeight: "600",
  },
  moduleMessage: {
    fontSize: 12,
    lineHeight: 16,
  },
  moduleProgressRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginTop: 2,
  },
  moduleProgressBg: {
    flex: 1,
    height: 3,
    borderRadius: 1.5,
    overflow: "hidden",
  },
  moduleProgressFill: {
    height: "100%",
    borderRadius: 1.5,
  },
  modulePercent: {
    fontSize: 11,
    fontWeight: "600",
    color: "#10a37f",
    width: 28,
    textAlign: "right",
  },
  moduleDetail: {
    borderRadius: 10,
    borderWidth: 1,
    padding: 12,
    marginTop: -4,
    marginBottom: 8,
    gap: 0,
  },
  detailRow: {
    flexDirection: "row",
    gap: 10,
    paddingVertical: 8,
  },
  detailLabel: {
    fontSize: 12,
    fontWeight: "500",
    width: 56,
    flexShrink: 0,
    paddingTop: 1,
  },
  detailValue: {
    fontSize: 13,
    flex: 1,
    lineHeight: 18,
  },
  detailDivider: {
    height: 0.5,
  },
  findingsList: {
    flex: 1,
    gap: 4,
  },
  findingItem: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 6,
  },
  findingDot: {
    width: 5,
    height: 5,
    borderRadius: 2.5,
    marginTop: 5,
    flexShrink: 0,
  },
  findingText: {
    fontSize: 12,
    flex: 1,
    lineHeight: 17,
  },
});

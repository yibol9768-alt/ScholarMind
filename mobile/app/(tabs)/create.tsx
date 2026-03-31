import { useState, useCallback } from "react";
import {
  Text,
  View,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Modal,
  StyleSheet,
} from "react-native";
import { useRouter } from "expo-router";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";
import { useTaskContext } from "@/lib/task-store";
import { MODULE_NAMES } from "@/lib/types";
import type { ModuleId } from "@/lib/types";

const RESEARCH_FIELDS = [
  "NLP / 自然语言处理",
  "CV / 计算机视觉",
  "ML / 机器学习理论",
  "多模态学习",
  "强化学习",
  "图神经网络",
  "生物信息学",
  "其他",
];

const TARGET_VENUES = [
  "ICLR", "NeurIPS", "ICML", "ACL", "EMNLP", "CVPR", "AAAI",
];

const SCENARIO_EXAMPLES = [
  {
    icon: "auto-stories",
    title: "全流程：LLM科学发现",
    desc: "从文献调研到论文写作的完整演示",
    topic: "请帮我对大语言模型在科学发现中的应用进行全面研究",
    mode: "full" as const,
    color: "#10a37f",
  },
  {
    icon: "lightbulb",
    title: "全流程：多模态创新",
    desc: "自动识别研究空白并生成创新 Idea",
    topic: "帮我在多模态学习领域寻找研究空白并提出创新想法",
    mode: "full" as const,
    color: "#f59e0b",
  },
  {
    icon: "code",
    title: "部分流程：实验复现",
    desc: "已有 Idea，只需代码生成 + 实验运行",
    topic: "帮我复现 Transformer 架构在时间序列预测上的实验",
    mode: "partial" as const,
    modules: ["M4", "M5", "M6", "M7"] as ModuleId[],
    color: "#6366f1",
  },
  {
    icon: "description",
    title: "部分流程：论文写作",
    desc: "已有实验结果，只需撰写论文",
    topic: "基于我的实验结果，帮我撰写一篇关于图神经网络的学术论文",
    mode: "partial" as const,
    modules: ["M8", "M9"] as ModuleId[],
    color: "#ec4899",
  },
];

const ALL_MODULES: ModuleId[] = ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"];

export default function CreateScreen() {
  const colors = useColors();
  const router = useRouter();
  const { createTask } = useTaskContext();

  const [input, setInput] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [selectedField, setSelectedField] = useState("");
  const [selectedVenue, setSelectedVenue] = useState("");
  const [selectedMode, setSelectedMode] = useState<"full" | "partial">("full");
  const [selectedModules, setSelectedModules] = useState<ModuleId[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const activeModules = selectedMode === "full" ? ALL_MODULES : selectedModules;
  const estimate = {
    timeMin: activeModules.length * 3,
    timeMax: activeModules.length * 8,
    papers: activeModules.includes("M1") ? "30-80" : "0",
  };

  const toggleModule = (m: ModuleId) => {
    setSelectedModules((prev) =>
      prev.includes(m) ? prev.filter((x) => x !== m) : [...prev, m].sort()
    );
  };

  const handleSubmit = useCallback(async () => {
    const topic = input.trim();
    if (!topic) return;
    setShowConfirm(false);
    setSubmitting(true);

    let desc = "";
    if (selectedField) desc += `研究领域: ${selectedField}\n`;
    if (selectedVenue) desc += `目标会议/期刊: ${selectedVenue}\n`;
    if (selectedMode === "partial" && selectedModules.length > 0) {
      desc += `运行模块: ${selectedModules.join(", ")}\n`;
    }

    try {
      const task = await createTask(topic, desc || undefined);
      setInput("");
      setShowAdvanced(false);
      setSelectedField("");
      setSelectedVenue("");
      setSelectedMode("full");
      setSelectedModules([]);
      router.push(`/task/${task.id}` as any);
    } catch {
      Alert.alert("创建失败", "请检查后端连接");
    } finally {
      setSubmitting(false);
    }
  }, [input, selectedField, selectedVenue, selectedMode, selectedModules, createTask, router]);

  const handleSuggestion = (example: (typeof SCENARIO_EXAMPLES)[0]) => {
    setInput(example.topic);
    setSelectedMode(example.mode);
    if (example.mode === "partial" && "modules" in example && example.modules) {
      setSelectedModules(example.modules);
    } else {
      setSelectedModules([]);
    }
    setShowAdvanced(true);
  };

  return (
    <ScreenContainer>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        {/* Header */}
        <View style={styles.heroSection}>
          <Text style={[styles.heroTitle, { color: colors.foreground }]}>
            想要研究什么？
          </Text>
          <Text style={[styles.heroSubtitle, { color: colors.muted }]}>
            输入研究主题，AI Agent 将自动完成全流程
          </Text>
        </View>

        {/* Input Area */}
        <View
          style={[styles.inputContainer, { backgroundColor: colors.surface, borderColor: colors.border }]}
        >
          <TextInput
            style={[styles.textInput, { color: colors.foreground }]}
            placeholder="描述你的研究主题..."
            placeholderTextColor={colors.muted}
            value={input}
            onChangeText={setInput}
            multiline
            numberOfLines={3}
            textAlignVertical="top"
          />
          <View style={styles.inputFooter}>
            <Text style={[styles.charCount, { color: colors.muted }]}>
              {input.length > 0 ? `${input.length} 字` : ""}
            </Text>
            <View style={styles.inputActions}>
              <TouchableOpacity
                onPress={() => setShowAdvanced(!showAdvanced)}
                style={[styles.advancedBtn, { backgroundColor: colors.border + "40" }]}
              >
                <Text style={[styles.advancedBtnText, { color: colors.muted }]}>
                  高级选项
                </Text>
                <MaterialIcons
                  name={showAdvanced ? "expand-less" : "expand-more"}
                  size={16}
                  color={colors.muted}
                />
              </TouchableOpacity>
              <TouchableOpacity
                onPress={() => {
                  if (input.trim()) setShowConfirm(true);
                }}
                disabled={!input.trim() || submitting}
                style={[
                  styles.sendBtn,
                  input.trim() && !submitting
                    ? { backgroundColor: "#10a37f" }
                    : { backgroundColor: colors.border },
                ]}
              >
                {submitting ? (
                  <ActivityIndicator size="small" color="#fff" />
                ) : (
                  <MaterialIcons name="arrow-upward" size={18} color="#fff" />
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>

        <Text style={[styles.inputHint, { color: colors.muted }]}>
          建议 50-200 字，描述清楚研究方向和关注点
        </Text>

        {/* Advanced Options */}
        {showAdvanced && (
          <View style={[styles.advancedPanel, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            {/* Mode Selection */}
            <Text style={[styles.sectionLabel, { color: colors.muted }]}>运行模式</Text>
            <View style={styles.modeRow}>
              <TouchableOpacity
                onPress={() => { setSelectedMode("full"); setSelectedModules([]); }}
                style={[
                  styles.modeCard,
                  selectedMode === "full"
                    ? { borderColor: "#10a37f", backgroundColor: "#10a37f10" }
                    : { borderColor: colors.border },
                ]}
              >
                <MaterialIcons name="flash-on" size={18} color="#10a37f" />
                <Text style={[styles.modeTitle, { color: colors.foreground }]}>完整流程</Text>
                <Text style={[styles.modeDesc, { color: colors.muted }]}>M1→M9 全自动</Text>
              </TouchableOpacity>
              <TouchableOpacity
                onPress={() => setSelectedMode("partial")}
                style={[
                  styles.modeCard,
                  selectedMode === "partial"
                    ? { borderColor: "#6366f1", backgroundColor: "#6366f110" }
                    : { borderColor: colors.border },
                ]}
              >
                <MaterialIcons name="tune" size={18} color="#6366f1" />
                <Text style={[styles.modeTitle, { color: colors.foreground }]}>部分流程</Text>
                <Text style={[styles.modeDesc, { color: colors.muted }]}>选定模块运行</Text>
              </TouchableOpacity>
            </View>

            {/* Module Selection */}
            {selectedMode === "partial" && (
              <View style={styles.moduleSection}>
                <Text style={[styles.sectionLabel, { color: colors.muted }]}>
                  选择模块
                  {selectedModules.length > 0 && (
                    <Text style={{ color: "#10a37f" }}> · 已选 {selectedModules.length}</Text>
                  )}
                </Text>
                <View style={styles.moduleGrid}>
                  {ALL_MODULES.map((m) => (
                    <TouchableOpacity
                      key={m}
                      onPress={() => toggleModule(m)}
                      style={[
                        styles.moduleChip,
                        selectedModules.includes(m)
                          ? { backgroundColor: "#10a37f" }
                          : { backgroundColor: colors.background, borderColor: colors.border, borderWidth: 1 },
                      ]}
                    >
                      <Text
                        style={[
                          styles.moduleChipText,
                          selectedModules.includes(m) ? { color: "#fff" } : { color: colors.muted },
                        ]}
                      >
                        {m} {MODULE_NAMES[m]}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
            )}

            {/* Research Field */}
            <Text style={[styles.sectionLabel, { color: colors.muted }]}>研究领域（可选）</Text>
            <View style={styles.chipGrid}>
              {RESEARCH_FIELDS.map((f) => (
                <TouchableOpacity
                  key={f}
                  onPress={() => setSelectedField(selectedField === f ? "" : f)}
                  style={[
                    styles.fieldChip,
                    selectedField === f
                      ? { backgroundColor: "#10a37f", borderColor: "#10a37f" }
                      : { backgroundColor: colors.background, borderColor: colors.border },
                  ]}
                >
                  <Text
                    style={[
                      styles.fieldChipText,
                      selectedField === f ? { color: "#fff" } : { color: colors.muted },
                    ]}
                  >
                    {f}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            {/* Target Venue */}
            <Text style={[styles.sectionLabel, { color: colors.muted }]}>目标会议（可选）</Text>
            <View style={styles.chipGrid}>
              {TARGET_VENUES.map((v) => (
                <TouchableOpacity
                  key={v}
                  onPress={() => setSelectedVenue(selectedVenue === v ? "" : v)}
                  style={[
                    styles.venueChip,
                    selectedVenue === v
                      ? { backgroundColor: "#6366f1", borderColor: "#6366f1" }
                      : { backgroundColor: colors.background, borderColor: colors.border },
                  ]}
                >
                  <Text
                    style={[
                      styles.venueChipText,
                      selectedVenue === v ? { color: "#fff" } : { color: colors.muted },
                    ]}
                  >
                    {v}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            {/* Estimate */}
            <View style={[styles.estimateCard, { backgroundColor: colors.background, borderColor: colors.border }]}>
              <MaterialIcons name="info-outline" size={14} color={colors.muted} />
              <Text style={[styles.estimateText, { color: colors.muted }]}>
                预计耗时 {estimate.timeMin}-{estimate.timeMax} 分钟
                {estimate.papers !== "0" ? `，检索约 ${estimate.papers} 篇文献` : ""}
              </Text>
            </View>
          </View>
        )}

        {/* Quick Start Scenarios */}
        <View style={styles.scenariosSection}>
          <Text style={[styles.scenariosTitle, { color: colors.foreground }]}>
            快速开始
          </Text>
          <Text style={[styles.scenariosSubtitle, { color: colors.muted }]}>
            选择一个场景模板快速开始
          </Text>
          <View style={styles.scenariosGrid}>
            {SCENARIO_EXAMPLES.map((ex, i) => (
              <TouchableOpacity
                key={i}
                onPress={() => handleSuggestion(ex)}
                style={[styles.scenarioCard, { backgroundColor: colors.surface, borderColor: colors.border }]}
                activeOpacity={0.7}
              >
                <View style={[styles.scenarioIconWrap, { backgroundColor: ex.color + "18" }]}>
                  <MaterialIcons name={ex.icon as any} size={20} color={ex.color} />
                </View>
                <Text style={[styles.scenarioTitle, { color: colors.foreground }]}>
                  {ex.title}
                </Text>
                <Text style={[styles.scenarioDesc, { color: colors.muted }]}>
                  {ex.desc}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </ScrollView>

      {/* Confirm Modal */}
      <Modal
        visible={showConfirm}
        transparent
        animationType="fade"
        onRequestClose={() => setShowConfirm(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalCard, { backgroundColor: colors.surface }]}>
            <View style={styles.modalHeader}>
              <MaterialIcons name="science" size={24} color="#10a37f" />
              <Text style={[styles.modalTitle, { color: colors.foreground }]}>
                确认创建任务
              </Text>
            </View>
            <Text style={[styles.modalDesc, { color: colors.muted }]}>
              将为以下主题创建 AI 科研任务：
            </Text>
            <View style={[styles.modalTopicBox, { backgroundColor: colors.background, borderColor: colors.border }]}>
              <Text style={[styles.modalTopic, { color: colors.foreground }]} numberOfLines={4}>
                {input}
              </Text>
            </View>
            {(selectedField || selectedVenue) && (
              <View style={styles.modalMeta}>
                {selectedField && (
                  <View style={styles.metaChip}>
                    <Text style={styles.metaChipText}>{selectedField}</Text>
                  </View>
                )}
                {selectedVenue && (
                  <View style={[styles.metaChip, { backgroundColor: "#6366f115" }]}>
                    <Text style={[styles.metaChipText, { color: "#6366f1" }]}>{selectedVenue}</Text>
                  </View>
                )}
              </View>
            )}
            <View style={styles.modalBtns}>
              <TouchableOpacity
                onPress={() => setShowConfirm(false)}
                style={[styles.modalCancelBtn, { borderColor: colors.border }]}
              >
                <Text style={[styles.modalCancelText, { color: colors.muted }]}>取消</Text>
              </TouchableOpacity>
              <TouchableOpacity
                onPress={handleSubmit}
                style={styles.modalConfirmBtn}
              >
                <MaterialIcons name="rocket-launch" size={16} color="#fff" />
                <Text style={styles.modalConfirmText}>开始研究</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  scrollContent: {
    padding: 16,
    paddingBottom: 40,
  },
  heroSection: {
    paddingTop: 8,
    paddingBottom: 16,
  },
  heroTitle: {
    fontSize: 24,
    fontWeight: "700",
    marginBottom: 4,
  },
  heroSubtitle: {
    fontSize: 14,
    lineHeight: 20,
  },
  inputContainer: {
    borderRadius: 16,
    borderWidth: 1,
    padding: 14,
    gap: 10,
  },
  textInput: {
    fontSize: 15,
    lineHeight: 22,
    minHeight: 80,
    textAlignVertical: "top",
  },
  inputFooter: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  charCount: {
    fontSize: 12,
  },
  inputActions: {
    flexDirection: "row",
    gap: 8,
    alignItems: "center",
  },
  advancedBtn: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    gap: 2,
  },
  advancedBtnText: {
    fontSize: 12,
    fontWeight: "500",
  },
  sendBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: "center",
    justifyContent: "center",
  },
  inputHint: {
    fontSize: 12,
    marginTop: 6,
    marginBottom: 16,
  },
  advancedPanel: {
    borderRadius: 16,
    borderWidth: 1,
    padding: 14,
    gap: 10,
    marginBottom: 16,
  },
  sectionLabel: {
    fontSize: 12,
    fontWeight: "500",
    marginBottom: 2,
  },
  modeRow: {
    flexDirection: "row",
    gap: 10,
  },
  modeCard: {
    flex: 1,
    borderRadius: 12,
    borderWidth: 1.5,
    padding: 12,
    alignItems: "center",
    gap: 4,
  },
  modeTitle: {
    fontSize: 13,
    fontWeight: "600",
  },
  modeDesc: {
    fontSize: 11,
  },
  moduleSection: {
    gap: 8,
  },
  moduleGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
  },
  moduleChip: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 8,
  },
  moduleChipText: {
    fontSize: 12,
    fontWeight: "500",
  },
  chipGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
    marginBottom: 4,
  },
  fieldChip: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 8,
    borderWidth: 1,
  },
  fieldChipText: {
    fontSize: 12,
  },
  venueChip: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 8,
    borderWidth: 1,
  },
  venueChipText: {
    fontSize: 12,
    fontWeight: "500",
  },
  estimateCard: {
    flexDirection: "row",
    alignItems: "center",
    padding: 10,
    borderRadius: 10,
    borderWidth: 1,
    gap: 6,
    marginTop: 4,
  },
  estimateText: {
    fontSize: 12,
    flex: 1,
  },
  scenariosSection: {
    gap: 8,
  },
  scenariosTitle: {
    fontSize: 16,
    fontWeight: "600",
  },
  scenariosSubtitle: {
    fontSize: 13,
    marginBottom: 4,
  },
  scenariosGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  scenarioCard: {
    width: "47%",
    borderRadius: 14,
    borderWidth: 1,
    padding: 14,
    gap: 8,
  },
  scenarioIconWrap: {
    width: 36,
    height: 36,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
  },
  scenarioTitle: {
    fontSize: 13,
    fontWeight: "600",
    lineHeight: 18,
  },
  scenarioDesc: {
    fontSize: 11,
    lineHeight: 16,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)",
    alignItems: "center",
    justifyContent: "center",
    padding: 20,
  },
  modalCard: {
    width: "100%",
    borderRadius: 20,
    padding: 20,
    gap: 14,
  },
  modalHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: "700",
  },
  modalDesc: {
    fontSize: 13,
  },
  modalTopicBox: {
    borderRadius: 12,
    borderWidth: 1,
    padding: 12,
  },
  modalTopic: {
    fontSize: 14,
    lineHeight: 20,
  },
  modalMeta: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
  },
  metaChip: {
    backgroundColor: "#10a37f15",
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  metaChipText: {
    fontSize: 12,
    color: "#10a37f",
    fontWeight: "500",
  },
  modalBtns: {
    flexDirection: "row",
    gap: 10,
    marginTop: 4,
  },
  modalCancelBtn: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: "center",
  },
  modalCancelText: {
    fontSize: 14,
    fontWeight: "500",
  },
  modalConfirmBtn: {
    flex: 2,
    flexDirection: "row",
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: "#10a37f",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
  },
  modalConfirmText: {
    fontSize: 14,
    fontWeight: "600",
    color: "#fff",
  },
});

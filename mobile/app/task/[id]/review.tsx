import { useEffect, useState, useCallback } from "react";
import {
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
  StyleSheet,
  Modal,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";
import { useTaskContext } from "@/lib/task-store";
import { submitReviewApi, isDemoMode } from "@/lib/api";
import type { ReviewDecision, ReviewDimension } from "@/lib/types";

const DECISION_CONFIG: Record<ReviewDecision, { label: string; color: string; bgColor: string; icon: string }> = {
  accept: { label: "Accept", color: "#22c55e", bgColor: "#f0fdf4", icon: "check-circle" },
  weak_accept: { label: "Weak Accept", color: "#10a37f", bgColor: "#ecfdf5", icon: "thumb-up" },
  weak_reject: { label: "Weak Reject", color: "#f59e0b", bgColor: "#fffbeb", icon: "thumb-down" },
  reject: { label: "Reject", color: "#ef4444", bgColor: "#fef2f2", icon: "cancel" },
};

function ScoreBar({ score, maxScore, color }: { score: number; maxScore: number; color: string }) {
  const pct = (score / maxScore) * 100;
  return (
    <View style={styles.scoreBarWrap}>
      <View style={[styles.scoreBarBg]}>
        <View style={[styles.scoreBarFill, { width: `${pct}%` as any, backgroundColor: color }]} />
      </View>
      <Text style={[styles.scoreBarText, { color }]}>
        {score}/{maxScore}
      </Text>
    </View>
  );
}

function DimensionCard({ dim, index }: { dim: ReviewDimension; index: number }) {
  const colors = useColors();
  const [expanded, setExpanded] = useState(false);
  const scoreRatio = dim.score / dim.maxScore;
  const color = scoreRatio >= 0.8 ? "#22c55e" : scoreRatio >= 0.6 ? "#10a37f" : scoreRatio >= 0.4 ? "#f59e0b" : "#ef4444";

  return (
    <TouchableOpacity
      onPress={() => setExpanded(!expanded)}
      style={[styles.dimCard, { backgroundColor: colors.surface, borderColor: colors.border }]}
      activeOpacity={0.7}
    >
      <View style={styles.dimHeader}>
        <View style={[styles.dimIndex, { backgroundColor: color + "20" }]}>
          <Text style={[styles.dimIndexText, { color }]}>{index + 1}</Text>
        </View>
        <View style={styles.dimTitleArea}>
          <Text style={[styles.dimName, { color: colors.foreground }]}>{dim.name}</Text>
          <ScoreBar score={dim.score} maxScore={dim.maxScore} color={color} />
        </View>
        <MaterialIcons name={expanded ? "expand-less" : "expand-more"} size={18} color={colors.muted} />
      </View>
      {expanded && (
        <Text style={[styles.dimComment, { color: colors.muted }]}>{dim.comment}</Text>
      )}
    </TouchableOpacity>
  );
}

export default function ReviewScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const colors = useColors();
  const { state, fetchReviewResult } = useTaskContext();
  const [showHumanReview, setShowHumanReview] = useState(false);
  const [humanComment, setHumanComment] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (id) fetchReviewResult(id);
  }, [id, fetchReviewResult]);

  const review = state.reviewResult;

  const handleHumanApprove = useCallback(async (approved: boolean) => {
    if (!id) return;
    setSubmitting(true);
    try {
      if (!isDemoMode()) {
        await submitReviewApi(id, approved, humanComment);
      }
      setShowHumanReview(false);
      Alert.alert(
        approved ? "已批准" : "已拒绝",
        approved
          ? "任务已批准，将继续执行后续步骤"
          : "任务已拒绝，请修改后重新提交"
      );
    } catch {
      Alert.alert("提交失败", "请检查网络连接");
    } finally {
      setSubmitting(false);
    }
  }, [id, humanComment]);

  if (state.loading && !review) {
    return (
      <ScreenContainer>
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#10a37f" />
        </View>
      </ScreenContainer>
    );
  }

  return (
    <ScreenContainer>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <MaterialIcons name="arrow-back" size={22} color={colors.foreground} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: colors.foreground }]}>评审报告</Text>
        <View style={{ width: 36 }} />
      </View>

      {!review ? (
        <View style={styles.centerContainer}>
          <MaterialIcons name="rate-review" size={56} color={colors.border} />
          <Text style={[styles.noReviewTitle, { color: colors.foreground }]}>暂无评审报告</Text>
          <Text style={[styles.noReviewDesc, { color: colors.muted }]}>
            任务完成后，AI 将自动生成 NeurIPS 风格的学术评审报告
          </Text>
        </View>
      ) : (
        <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
          {/* Score Hero */}
          {(() => {
            const decisionConfig = DECISION_CONFIG[review.decision];
            return (
              <View style={[styles.scoreHero, { backgroundColor: decisionConfig.bgColor, borderColor: decisionConfig.color }]}>
                <View style={styles.scoreHeroLeft}>
                  <Text style={[styles.scoreNumber, { color: decisionConfig.color }]}>
                    {review.overall_score.toFixed(1)}
                  </Text>
                  <Text style={[styles.scoreMax, { color: decisionConfig.color }]}>/10</Text>
                </View>
                <View style={styles.scoreHeroRight}>
                  <View style={[styles.decisionBadge, { backgroundColor: decisionConfig.color }]}>
                    <MaterialIcons name={decisionConfig.icon as any} size={14} color="#fff" />
                    <Text style={styles.decisionText}>{decisionConfig.label}</Text>
                  </View>
                  <Text style={[styles.scoreHeroLabel, { color: decisionConfig.color }]}>
                    综合评分
                  </Text>
                  <Text style={[styles.scoreTimestamp, { color: decisionConfig.color + "aa" }]}>
                    {new Date(review.timestamp).toLocaleDateString("zh-CN")}
                  </Text>
                </View>
              </View>
            );
          })()}

          {/* Summary */}
          <View style={[styles.summaryCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <View style={styles.summaryHeader}>
              <MaterialIcons name="summarize" size={18} color="#10a37f" />
              <Text style={[styles.summaryTitle, { color: colors.foreground }]}>评审摘要</Text>
            </View>
            <Text style={[styles.summaryText, { color: colors.foreground }]}>{review.summary}</Text>
          </View>

          {/* Dimensions */}
          <View style={styles.dimensionsSection}>
            <Text style={[styles.sectionTitle, { color: colors.foreground }]}>评分维度</Text>
            <Text style={[styles.sectionSubtitle, { color: colors.muted }]}>点击查看详细评语</Text>
            {review.dimensions.map((dim, i) => (
              <DimensionCard key={i} dim={dim} index={i} />
            ))}
          </View>

          {/* Human Review */}
          <View style={styles.humanReviewSection}>
            <Text style={[styles.sectionTitle, { color: colors.foreground }]}>人工审阅</Text>
            <Text style={[styles.sectionSubtitle, { color: colors.muted }]}>
              基于 AI 评审结果，决定是否批准该研究继续进行
            </Text>
            <TouchableOpacity
              onPress={() => setShowHumanReview(true)}
              style={styles.humanReviewBtn}
            >
              <MaterialIcons name="how-to-vote" size={18} color="#fff" />
              <Text style={styles.humanReviewBtnText}>提交人工审阅决定</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      )}

      {/* Human Review Modal */}
      <Modal
        visible={showHumanReview}
        transparent
        animationType="slide"
        onRequestClose={() => setShowHumanReview(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalCard, { backgroundColor: colors.surface }]}>
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: colors.foreground }]}>人工审阅</Text>
              <TouchableOpacity onPress={() => setShowHumanReview(false)}>
                <MaterialIcons name="close" size={22} color={colors.muted} />
              </TouchableOpacity>
            </View>

            <Text style={[styles.modalDesc, { color: colors.muted }]}>
              AI 综合评分：
              <Text style={{ color: "#10a37f", fontWeight: "700" }}>
                {review?.overall_score.toFixed(1)}/10
              </Text>
              {" · "}
              {review && DECISION_CONFIG[review.decision]?.label}
            </Text>

            <Text style={[styles.commentLabel, { color: colors.muted }]}>补充意见（可选）</Text>
            <TextInput
              style={[styles.commentInput, { backgroundColor: colors.background, borderColor: colors.border, color: colors.foreground }]}
              placeholder="输入你的审阅意见..."
              placeholderTextColor={colors.muted}
              value={humanComment}
              onChangeText={setHumanComment}
              multiline
              numberOfLines={4}
              textAlignVertical="top"
            />

            <View style={styles.modalBtns}>
              <TouchableOpacity
                onPress={() => handleHumanApprove(false)}
                disabled={submitting}
                style={styles.rejectBtn}
              >
                {submitting ? (
                  <ActivityIndicator size="small" color="#ef4444" />
                ) : (
                  <MaterialIcons name="thumb-down" size={16} color="#ef4444" />
                )}
                <Text style={styles.rejectBtnText}>拒绝</Text>
              </TouchableOpacity>
              <TouchableOpacity
                onPress={() => handleHumanApprove(true)}
                disabled={submitting}
                style={styles.approveBtn}
              >
                {submitting ? (
                  <ActivityIndicator size="small" color="#fff" />
                ) : (
                  <MaterialIcons name="thumb-up" size={16} color="#fff" />
                )}
                <Text style={styles.approveBtnText}>批准</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
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
  centerContainer: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 32,
    gap: 12,
  },
  noReviewTitle: {
    fontSize: 17,
    fontWeight: "600",
    marginTop: 8,
  },
  noReviewDesc: {
    fontSize: 13,
    textAlign: "center",
    lineHeight: 18,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 40,
    gap: 16,
  },
  scoreHero: {
    flexDirection: "row",
    alignItems: "center",
    padding: 20,
    borderRadius: 20,
    borderWidth: 1.5,
    gap: 16,
  },
  scoreHeroLeft: {
    flexDirection: "row",
    alignItems: "baseline",
    gap: 2,
  },
  scoreNumber: {
    fontSize: 52,
    fontWeight: "800",
    lineHeight: 56,
  },
  scoreMax: {
    fontSize: 20,
    fontWeight: "600",
  },
  scoreHeroRight: {
    flex: 1,
    gap: 6,
  },
  decisionBadge: {
    flexDirection: "row",
    alignItems: "center",
    alignSelf: "flex-start",
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 20,
    gap: 5,
  },
  decisionText: {
    fontSize: 13,
    fontWeight: "700",
    color: "#fff",
  },
  scoreHeroLabel: {
    fontSize: 13,
    fontWeight: "500",
  },
  scoreTimestamp: {
    fontSize: 11,
  },
  summaryCard: {
    borderRadius: 16,
    borderWidth: 1,
    padding: 14,
    gap: 10,
  },
  summaryHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  summaryTitle: {
    fontSize: 15,
    fontWeight: "600",
  },
  summaryText: {
    fontSize: 13,
    lineHeight: 20,
  },
  dimensionsSection: {
    gap: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "700",
  },
  sectionSubtitle: {
    fontSize: 12,
    marginBottom: 4,
  },
  dimCard: {
    borderRadius: 12,
    borderWidth: 1,
    padding: 12,
    gap: 8,
  },
  dimHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  dimIndex: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
  },
  dimIndexText: {
    fontSize: 13,
    fontWeight: "700",
  },
  dimTitleArea: {
    flex: 1,
    gap: 4,
  },
  dimName: {
    fontSize: 14,
    fontWeight: "600",
  },
  scoreBarWrap: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  scoreBarBg: {
    flex: 1,
    height: 5,
    borderRadius: 2.5,
    backgroundColor: "#e5e7eb",
    overflow: "hidden",
  },
  scoreBarFill: {
    height: "100%",
    borderRadius: 2.5,
  },
  scoreBarText: {
    fontSize: 11,
    fontWeight: "600",
    width: 30,
    textAlign: "right",
  },
  dimComment: {
    fontSize: 12,
    lineHeight: 17,
    paddingLeft: 38,
  },
  humanReviewSection: {
    gap: 8,
  },
  humanReviewBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 14,
    borderRadius: 14,
    backgroundColor: "#10a37f",
    gap: 8,
    marginTop: 4,
  },
  humanReviewBtnText: {
    fontSize: 15,
    fontWeight: "600",
    color: "#fff",
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)",
    justifyContent: "flex-end",
  },
  modalCard: {
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 20,
    gap: 14,
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: "700",
  },
  modalDesc: {
    fontSize: 13,
  },
  commentLabel: {
    fontSize: 12,
    fontWeight: "500",
  },
  commentInput: {
    borderRadius: 12,
    borderWidth: 1,
    padding: 12,
    fontSize: 14,
    minHeight: 100,
  },
  modalBtns: {
    flexDirection: "row",
    gap: 10,
    paddingBottom: 8,
  },
  rejectBtn: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 12,
    borderRadius: 12,
    borderWidth: 1.5,
    borderColor: "#ef4444",
    backgroundColor: "#fef2f2",
    gap: 6,
  },
  rejectBtnText: {
    fontSize: 14,
    fontWeight: "600",
    color: "#ef4444",
  },
  approveBtn: {
    flex: 2,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: "#10a37f",
    gap: 6,
  },
  approveBtnText: {
    fontSize: 14,
    fontWeight: "600",
    color: "#fff",
  },
});

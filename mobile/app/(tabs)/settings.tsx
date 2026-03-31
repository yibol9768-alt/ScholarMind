import { useState, useEffect, useCallback } from "react";
import {
  Text,
  View,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  StyleSheet,
} from "react-native";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";
import { getBackendUrl, setBackendUrl, testConnection, isDemoMode } from "@/lib/api";

export default function SettingsScreen() {
  const colors = useColors();
  const [url, setUrl] = useState("");
  const [testing, setTesting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<
    "unknown" | "connected" | "failed"
  >("unknown");

  useEffect(() => {
    getBackendUrl().then(setUrl);
  }, []);

  const handleTest = useCallback(async () => {
    setTesting(true);
    setConnectionStatus("unknown");
    const ok = await testConnection(url);
    setConnectionStatus(ok ? "connected" : "failed");
    setTesting(false);
  }, [url]);

  const handleSave = useCallback(async () => {
    await setBackendUrl(url);
    Alert.alert("已保存", "后端地址已更新，将在下次请求时生效");
  }, [url]);

  return (
    <ScreenContainer>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <Text style={[styles.pageTitle, { color: colors.foreground }]}>设置</Text>

        {/* Connection Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.foreground }]}>后端连接</Text>
          <Text style={[styles.sectionDesc, { color: colors.muted }]}>
            配置 ScholarMind 后端服务器地址，实现手机与电脑端数据互联
          </Text>

          <View style={styles.fieldGroup}>
            <Text style={[styles.fieldLabel, { color: colors.muted }]}>服务器地址</Text>
            <View
              style={[styles.inputRow, { backgroundColor: colors.surface, borderColor: colors.border }]}
            >
              <MaterialIcons name="dns" size={18} color={colors.muted} />
              <TextInput
                style={[styles.fieldInput, { color: colors.foreground }]}
                value={url}
                onChangeText={setUrl}
                placeholder="http://192.168.1.100:8000"
                placeholderTextColor={colors.muted}
                autoCapitalize="none"
                autoCorrect={false}
                keyboardType="url"
                returnKeyType="done"
              />
            </View>
            <Text style={[styles.fieldHint, { color: colors.muted }]}>
              输入电脑端运行 ScholarMind 后端的 IP 地址和端口
            </Text>
          </View>

          <View style={styles.btnRow}>
            <TouchableOpacity
              onPress={handleTest}
              disabled={testing}
              style={[styles.testBtn, { borderColor: colors.border }]}
            >
              {testing ? (
                <ActivityIndicator size="small" color="#10a37f" />
              ) : (
                <MaterialIcons name="wifi-tethering" size={16} color="#10a37f" />
              )}
              <Text style={styles.testBtnText}>测试连接</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={handleSave} style={styles.saveBtn}>
              <MaterialIcons name="save" size={16} color="#fff" />
              <Text style={styles.saveBtnText}>保存</Text>
            </TouchableOpacity>
          </View>

          {connectionStatus !== "unknown" && (
            <View
              style={[
                styles.statusCard,
                {
                  backgroundColor: connectionStatus === "connected" ? "#22c55e18" : "#ef444418",
                  borderColor: connectionStatus === "connected" ? "#22c55e" : "#ef4444",
                },
              ]}
            >
              <MaterialIcons
                name={connectionStatus === "connected" ? "check-circle" : "error"}
                size={18}
                color={connectionStatus === "connected" ? "#22c55e" : "#ef4444"}
              />
              <Text
                style={[
                  styles.statusText,
                  { color: connectionStatus === "connected" ? "#22c55e" : "#ef4444" },
                ]}
              >
                {connectionStatus === "connected"
                  ? "连接成功！数据将与电脑端实时同步"
                  : "连接失败，请检查地址和网络"}
              </Text>
            </View>
          )}
        </View>

        {/* Demo Mode Info */}
        {isDemoMode() && (
          <View style={[styles.demoCard, { backgroundColor: "#10a37f10", borderColor: "#10a37f" }]}>
            <MaterialIcons name="info" size={18} color="#10a37f" />
            <View style={styles.demoContent}>
              <Text style={[styles.demoTitle, { color: colors.foreground }]}>演示模式</Text>
              <Text style={[styles.demoDesc, { color: colors.muted }]}>
                当前未连接到后端服务器，显示的是演示数据。配置正确的后端地址后，将自动切换为实时数据。
              </Text>
            </View>
          </View>
        )}

        {/* How to Connect */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.foreground }]}>如何连接</Text>
          <View style={[styles.stepsCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            {[
              { step: "1", text: "确保手机和电脑在同一局域网" },
              { step: "2", text: "在电脑端启动 ScholarMind 后端" },
              { step: "3", text: "查看电脑 IP（如 192.168.1.100）" },
              { step: "4", text: "在上方输入 http://IP:8000 并保存" },
            ].map((item, i) => (
              <View key={i} style={styles.stepRow}>
                <View style={styles.stepBadge}>
                  <Text style={styles.stepNum}>{item.step}</Text>
                </View>
                <Text style={[styles.stepText, { color: colors.foreground }]}>{item.text}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* About Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.foreground }]}>关于</Text>
          <View style={[styles.aboutCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            {[
              { label: "应用名称", value: "ScholarMind Mobile" },
              { label: "版本", value: "1.0.0" },
              { label: "技术栈", value: "React Native + Expo" },
              { label: "桌面端", value: "React + FastAPI" },
            ].map((item, i, arr) => (
              <View key={i}>
                <View style={styles.aboutRow}>
                  <Text style={[styles.aboutLabel, { color: colors.muted }]}>{item.label}</Text>
                  <Text style={[styles.aboutValue, { color: colors.foreground }]}>{item.value}</Text>
                </View>
                {i < arr.length - 1 && (
                  <View style={[styles.aboutDivider, { backgroundColor: colors.border }]} />
                )}
              </View>
            ))}
          </View>
        </View>

        {/* Feature List */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.foreground }]}>功能说明</Text>
          <View style={[styles.featureCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            {[
              { icon: "sync", text: "与电脑端实时数据同步" },
              { icon: "science", text: "查看 M1→M9 研究流水线进度" },
              { icon: "add-circle", text: "随时随地创建新研究任务" },
              { icon: "rate-review", text: "移动端完成人工审阅" },
              { icon: "article", text: "查看追溯日志和评审结果" },
            ].map((f, i) => (
              <View key={i} style={styles.featureRow}>
                <MaterialIcons name={f.icon as any} size={18} color="#10a37f" />
                <Text style={[styles.featureText, { color: colors.foreground }]}>{f.text}</Text>
              </View>
            ))}
          </View>
        </View>
      </ScrollView>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  scrollContent: {
    padding: 16,
    paddingBottom: 40,
  },
  pageTitle: {
    fontSize: 24,
    fontWeight: "700",
    marginBottom: 20,
    paddingTop: 4,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 4,
  },
  sectionDesc: {
    fontSize: 13,
    marginBottom: 14,
    lineHeight: 18,
  },
  fieldGroup: {
    marginBottom: 12,
  },
  fieldLabel: {
    fontSize: 12,
    fontWeight: "500",
    marginBottom: 6,
  },
  inputRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 12,
    borderWidth: 1,
    gap: 8,
  },
  fieldInput: {
    flex: 1,
    fontSize: 14,
    paddingVertical: 0,
  },
  fieldHint: {
    fontSize: 11,
    marginTop: 4,
  },
  btnRow: {
    flexDirection: "row",
    gap: 10,
  },
  testBtn: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 10,
    borderRadius: 12,
    borderWidth: 1,
    gap: 6,
  },
  testBtnText: {
    fontSize: 13,
    fontWeight: "500",
    color: "#10a37f",
  },
  saveBtn: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 10,
    borderRadius: 12,
    backgroundColor: "#10a37f",
    gap: 6,
  },
  saveBtnText: {
    fontSize: 13,
    fontWeight: "600",
    color: "#fff",
  },
  statusCard: {
    flexDirection: "row",
    alignItems: "center",
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    marginTop: 12,
    gap: 8,
  },
  statusText: {
    fontSize: 13,
    flex: 1,
  },
  demoCard: {
    flexDirection: "row",
    alignItems: "flex-start",
    padding: 14,
    borderRadius: 14,
    borderWidth: 1,
    marginBottom: 24,
    gap: 10,
  },
  demoContent: {
    flex: 1,
  },
  demoTitle: {
    fontSize: 14,
    fontWeight: "600",
    marginBottom: 2,
  },
  demoDesc: {
    fontSize: 12,
    lineHeight: 17,
  },
  stepsCard: {
    borderRadius: 14,
    borderWidth: 1,
    padding: 14,
    marginTop: 8,
    gap: 12,
  },
  stepRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  stepBadge: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: "#10a37f",
    alignItems: "center",
    justifyContent: "center",
  },
  stepNum: {
    fontSize: 12,
    fontWeight: "700",
    color: "#fff",
  },
  stepText: {
    fontSize: 13,
    flex: 1,
  },
  aboutCard: {
    borderRadius: 14,
    borderWidth: 1,
    overflow: "hidden",
    marginTop: 8,
  },
  aboutRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  aboutLabel: {
    fontSize: 13,
  },
  aboutValue: {
    fontSize: 13,
    fontWeight: "500",
  },
  aboutDivider: {
    height: 0.5,
    marginHorizontal: 14,
  },
  featureCard: {
    borderRadius: 14,
    borderWidth: 1,
    padding: 14,
    marginTop: 8,
    gap: 12,
  },
  featureRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  featureText: {
    fontSize: 13,
  },
});

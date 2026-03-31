from __future__ import annotations
"""M6: 自动化Agent实验执行模块

基于 AI-Scientist 重构：
直接复用 AI-Scientist perform_experiments.py 的 run_experiment() 逻辑，
在沙箱中执行 python experiment.py --out_dir=run_i，
出错时通过 Aider 自动修复。

核心依赖: AI-Scientist perform_experiments.py
"""

import json
import os
import shutil
import subprocess
from subprocess import TimeoutExpired

from modules.base import BaseModule
from pipeline.tracer import Tracer
from pipeline.state import TaskStateMachine
import config

# AI-Scientist 常量
MAX_ITERS = 4
MAX_RUNS = 5
MAX_STDERR_OUTPUT = 1500


class AgentRunnerModule(BaseModule):
    module_id = 6
    name = "Agent实验执行"

    async def execute(self, context: dict, tracer: Tracer, state: TaskStateMachine) -> dict:
        project_dir = context.get("project_dir", context.get("code_dir", ""))
        baseline_results = context.get("baseline_results", {})
        best_idea = context.get("best_idea", {})
        workspace = context["workspace"]
        max_runs = context.get("max_runs", MAX_RUNS)
        experiment_timeout = context.get("config", {}).get("experiment_timeout", config.SANDBOX_TIMEOUT)

        raw_idea = best_idea.get("_raw", best_idea)

        all_results = []

        # ── AI-Scientist perform_experiments 逻辑 ──
        tracer.step_start()
        await tracer.log(6, "run_experiments", f"开始执行实验 (最多 {max_runs} runs)")

        # 初始化 Aider coder (用于修复错误和迭代实验)
        coder = await self._init_coder(project_dir)

        current_iter = 0
        run_num = 1

        # 构建初始 prompt (AI-Scientist coder_prompt)
        from modules.m5_experiment_design import CODER_PROMPT
        next_prompt = CODER_PROMPT.format(
            title=raw_idea.get("Title", best_idea.get("title", "")),
            idea=raw_idea.get("Experiment", best_idea.get("experiment_plan", "")),
            max_runs=max_runs,
            baseline_results=json.dumps(baseline_results, indent=2),
        )

        while run_num <= max_runs:
            if state.is_aborted:
                break
            if current_iter >= MAX_ITERS:
                await tracer.log(6, "run_experiments", "达到最大迭代次数", level="warn")
                break

            # 让 Aider 修改代码
            if coder:
                try:
                    coder_out = coder.run(next_prompt)
                    if "ALL_COMPLETED" in str(coder_out):
                        await tracer.log(6, "run_experiments", "Aider 表示所有实验完成")
                        break
                except Exception as e:
                    await tracer.log(6, "run_experiments",
                                     f"Aider 调用失败: {e}", level="warn")

            # 运行实验 (AI-Scientist run_experiment 逻辑)
            await tracer.log(6, f"run_{run_num}", f"执行 run_{run_num}")
            returncode, next_prompt, metrics = self._run_experiment(
                project_dir, run_num, timeout=experiment_timeout
            )

            if returncode == 0:
                all_results.append({
                    "experiment": f"run_{run_num}",
                    "type": "main",
                    "status": "success",
                    "metrics": metrics,
                    "fix_rounds": current_iter,
                })
                await tracer.log(6, f"run_{run_num}",
                                 f"run_{run_num} 成功: {metrics}")
                run_num += 1
                current_iter = 0
            else:
                all_results.append({
                    "experiment": f"run_{run_num}_attempt_{current_iter}",
                    "type": "failed",
                    "status": "failed",
                    "metrics": {},
                    "error": next_prompt[:500],
                })
                await tracer.log(6, f"run_{run_num}",
                                 f"run_{run_num} 失败，重试中...", level="warn")
                current_iter += 1

        # ── 运行 plot.py (AI-Scientist run_plotting) ──
        tracer.step_start()
        await tracer.log(6, "run_plotting", "生成可视化图表")
        self._run_plotting(project_dir)

        # ── 生成 notes.txt ──
        if coder:
            try:
                coder.run(
                    "Please modify `notes.txt` with a description of what each "
                    "experiment run shows along with the key results. "
                    "Somebody else will use this to write a paper."
                )
            except Exception:
                pass

        # ── 保存产出 ──
        results_path = os.path.join(workspace, "m6_experiment_results.json")
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump({"results": all_results}, f, ensure_ascii=False, indent=2)

        successful = [r for r in all_results if r["status"] == "success"]
        await tracer.save_output(6, "experiment_results", file_path=results_path,
                                  metadata={
                                      "total_runs": len(all_results),
                                      "successful": len(successful),
                                  })
        await tracer.log(6, "run_experiments",
                         f"实验完成: {len(successful)}/{len(all_results)} 成功")

        context["experiment_results"] = all_results
        return context

    def _run_experiment(self, folder_name, run_num, timeout=7200):
        """运行单个实验 (复用 AI-Scientist run_experiment)"""
        cwd = os.path.abspath(folder_name)

        # 备份当前代码
        src = os.path.join(folder_name, "experiment.py")
        dst = os.path.join(folder_name, f"run_{run_num}.py")
        if os.path.exists(src):
            shutil.copy(src, dst)

        command = ["python", "experiment.py", f"--out_dir=run_{run_num}"]

        try:
            result = subprocess.run(
                command, cwd=cwd, stderr=subprocess.PIPE, text=True, timeout=timeout
            )

            if result.returncode != 0:
                stderr_output = result.stderr
                if len(stderr_output) > MAX_STDERR_OUTPUT:
                    stderr_output = "..." + stderr_output[-MAX_STDERR_OUTPUT:]
                next_prompt = f"Run failed with the following error {stderr_output}"
                if os.path.exists(os.path.join(cwd, f"run_{run_num}")):
                    shutil.rmtree(os.path.join(cwd, f"run_{run_num}"))
                return result.returncode, next_prompt, {}
            else:
                # 读取结果
                info_path = os.path.join(cwd, f"run_{run_num}", "final_info.json")
                metrics = {}
                if os.path.exists(info_path):
                    with open(info_path, "r") as f:
                        results = json.load(f)
                    metrics = {k: v["means"] for k, v in results.items()
                               if isinstance(v, dict) and "means" in v}

                next_prompt = f"""Run {run_num} completed. Here are the results:
{json.dumps(metrics, indent=2)}

Decide if you need to re-plan your experiments given the result.
Then, implement the next thing on your list.
We will then run the command `python experiment.py --out_dir=run_{run_num + 1}'.
If you are finished with experiments, respond with 'ALL_COMPLETED'."""

                return 0, next_prompt, metrics

        except TimeoutExpired:
            if os.path.exists(os.path.join(cwd, f"run_{run_num}")):
                shutil.rmtree(os.path.join(cwd, f"run_{run_num}"))
            return 1, f"Run timed out after {timeout} seconds", {}

    def _run_plotting(self, folder_name, timeout=600):
        """运行 plot.py (复用 AI-Scientist run_plotting)"""
        cwd = os.path.abspath(folder_name)
        try:
            subprocess.run(
                ["python", "plot.py"],
                cwd=cwd, stderr=subprocess.PIPE, text=True, timeout=timeout,
            )
        except Exception:
            pass

    async def _init_coder(self, project_dir):
        """初始化 Aider coder"""
        try:
            from aider.coders import Coder
            from aider.models import Model
            from aider.io import InputOutput

            os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY
            os.environ["OPENAI_API_BASE"] = config.OPENAI_BASE_URL

            model = Model(f"openai/{config.OPENAI_MODEL}")
            io = InputOutput(yes=True)
            fnames = [os.path.join(project_dir, "experiment.py")]

            return Coder.create(
                main_model=model,
                fnames=fnames,
                io=io,
                stream=False,
                use_git=True,
                edit_format="diff",
            )
        except Exception as e:
            print(f"Failed to init Aider coder: {e}")
            return None

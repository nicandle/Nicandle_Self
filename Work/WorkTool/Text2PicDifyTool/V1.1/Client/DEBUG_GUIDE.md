# Dify 节点本地调试指南 (Local Debug Guide)

本文档旨在帮助开发者在本地 Cursor 环境中，通过 Python 脚本快速调试 Dify 工作流中的 LLM 节点，遵循 "Code-First" 开发模式。

## 1. 环境准备 (Setup)

首次开始调试前，请确保完成以下配置：

### 1.1 安装依赖
打开终端 (Terminal)，进入 `Client` 目录并安装 Python 依赖：

```bash
cd WorkTool/Text2PicDifyTool/V1.1/Client
pip install -r requirements.txt
```

### 1.2 配置 API Key
1.  找到 `WorkTool/Text2PicDifyTool/V1.1/Client/.env.example` 文件。
2.  将其复制并重命名为 `.env`。
3.  在 `.env` 文件中填入您的 OpenAI API Key（或兼容 OpenAI 协议的 Key，如 DeepSeek, Moonshot 等）：

```ini
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 2. 调试流程 (Debug Workflow)

核心调试文件为：`debug_node.py`。该脚本模拟了 Dify 的 LLM 节点运行环境。

### 步骤 A: 修改测试用例 (Mock Input)
打开 `debug_node.py`，滚动到底部的 `if __name__ == "__main__":` 区域。
修改 `test_case` 字典，模拟上游节点传入的变量。

```python
# [SECTION 3] 调试入口
if __name__ == "__main__":
    # 在这里快速修改测试用例
    test_case = {
        "species_out": "柯基犬",             # 模拟基础物种
        "combined_out": "吐司面包, 芝士",    # 模拟特征基因
        "pose_description": "四足趴卧姿态",  # 模拟姿态描述
        "eye_requirements": "豆豆眼",        # 模拟眼睛要求
        "query": "生成 Prompt"              # 模拟用户输入
    }
    
    run_simulation(DIFY_NODE_CONFIG, test_case)
```

### 步骤 B: 运行调试脚本
在终端中运行：

```bash
python debug_node.py
```

### 步骤 C: 查看与分析结果
观察终端输出：
1.  **输入检查**: 确认 `📥 输入变量` 是否正确。
2.  **结果检查**: 查看 `✅ [输出结果]`，这是 LLM 生成的最终 Prompt。

### 步骤 D: 优化 Prompt (Iterate)
如果生成结果不理想，回到 `debug_node.py` 的顶部 `[SECTION 1]`。
直接修改 `DIFY_NODE_CONFIG` 中的 `system_prompt`。

*   **调整指令**: 修改 System Prompt 的文字描述。
*   **调整参数**: 修改 `model_config` 中的 `temperature` (温度值) 来控制随机性。

---

## 3. 导出到 Dify (Export)

当您在本地调试出满意的 Prompt 后，无需手动复制粘贴。
请在 Cursor 对话框中输入：

> "导出这个节点的 DSL"

AI 助手会将 Python 配置转换为 Dify 兼容的 YAML 代码片段，您只需将其粘贴到 Dify 的 DSL 文件中即可。

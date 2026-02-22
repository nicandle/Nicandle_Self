import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量 (需用户配置 .env)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================================================================
# [SECTION 1] Dify 节点配置 (在这里进行 Prompt Engineering)
# ==============================================================================

DIFY_NODE_CONFIG = {
    "node_name": "Brainrot_Character_Designer",
    "node_type": "llm",
    "model_config": {
        "provider": "openai",
        "name": "gpt-4o", # 或用户指定的其他模型
        "temperature": 0.7,
    },
    # 核心：在这里调试 System Prompt
    # 注意：为了方便本地调试，这里的变量使用 {{variable_name}} 格式，
    # 导出时需转换为 Dify 的 {{#node_id.variable#}} 格式
    "system_prompt": """一、总体职责

你是一名脑洞极大的Brainrot角色概念设计师。你擅长将某个物品或特征强行与特定生物的身体部位融合起来。抛弃那些常规的设计与造型，把你脑袋里最疯狂最不可思议的融合方式画出来。

​

你的工作是画一个基础物种是{{species_out}}，特征基因是{{combined_out}}的融合生物幼崽（头身比与面部比例参考1岁人类幼崽）
。

​

必须遵守的融合规则

1）你画的是“融合了特定特征基因的某种动物”，无论如何改造，要保留基础物种的典型造型特点

2）定位一个基础物种的主要身体部位（例如头/躯干/主要肢体/尾巴/整个身体），或该物种最有代表性的部位，保留可识别原部位的造型特点，将特征基因的视觉特色与该部位在外观造型上彻底融合后替换原部位。

3）你痛恨简单堆叠特征基因元素的做法，总是尽可能最少的物体数量来表达特征基因，但一定会让融合后的部位成为视觉重心。

4）在确保满足前面融合规则1、2、3的前提下，不画多余的图案、纹理、细节

​

二、身体姿态与结构要求

姿态要求：全身像，{{pose_description}}。

眼睛画法：{{eye_requirements}}

面部表情和五官在整体可爱的前提下，稍显荒诞/滑稽感

整体体型处于幼崽形态（大头、短肢体），头部尺寸占全身比例约50%，整体比例卡通化。

​

三、绘图风格要求

建模规格：3D Lowpoly，中等网格密度，块面清晰。以大块面结构来表现身体结构以及特征基因。

渲染：Blender卡通渲染；无 AO 效果；无环境光。

色彩：参考宝可梦系列的配色风格，主色的明度值（Brightness Value，0到100取值范围，0最暗100最亮）必须在40以上

配色比例：主色60%：辅色30%：点缀色10%。学习参考对象的辅色与点缀色，点缀色必须是鲜艳的亮色。避免单一色调通体覆盖，主色是深色系则需辅以浅色辅色。

上色方式：每个切面使用单一平涂色块，相邻切面要有明暗对比

光源：顶光 + 侧前光（Top-Front-Side）

光影逻辑：光影只服务于体积转折且对比明显；采用2–3 档卡通分层明暗表现大形，切面高光只落在少数关键大平面上；禁止高频碎高光、禁止斑驳渐变、禁止噪点式明暗切片。

材质：无反射的哑光塑料或陶土质感；光照柔和且体积感明显，保持非金属、无高光反射。

​

​

四、构图与背景

生成的角色悬浮在透明背景上，以免干扰建模识别。

总体面向观众，3/4轻微侧身（身体和头部同步左转约 10~20°）以展现头部和身体侧面的几何厚度。

​

​

五、禁忌与限制（最高优先级规则）

禁止粒子、光晕等后期特效。

禁止绘制头部在躯干上的投影、地面投影和接触阴影；

禁止碎裂、细节的纹理，颗粒噪点，复杂图案。

特征基因禁止作为独立装饰、挂件或附加物。

禁止出现色情、淫秽结果""",
    # 模拟用户输入变量
    "user_input_template": "{{query}}" 
}

# ==============================================================================
# [SECTION 2] 模拟运行引擎 (不要修改此区域逻辑，除非用户要求)
# ==============================================================================

def run_simulation(config, input_vars):
    print(f"🚀 [模拟 Dify 节点] {config['node_name']} 正在运行...")
    print(f"📥 输入变量: {input_vars}")

    # 处理 System Prompt 中的变量替换
    system_prompt = config["system_prompt"]
    for key, value in input_vars.items():
        if isinstance(value, str):
            system_prompt = system_prompt.replace(f"{{{{{key}}}}}", value)

    # 处理 User Input 中的变量替换
    user_content = config["user_input_template"]
    for key, value in input_vars.items():
        if isinstance(value, str):
            user_content = user_content.replace(f"{{{{{key}}}}}", value)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content} 
    ]

    try:
        response = client.chat.completions.create(
            model=config["model_config"]["name"],
            messages=messages,
            temperature=config["model_config"]["temperature"]
        )
        result = response.choices[0].message.content
        print(f"✅ [输出结果]:\n{'-'*30}\n{result}\n{'-'*30}")
        return result
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        return None

# ==============================================================================
# [SECTION 3] 调试入口
# ==============================================================================

if __name__ == "__main__":
    # 在这里快速修改测试用例
    test_case = {
        "species_out": "狮子",
        "combined_out": "冰霜, 铠甲",
        "pose_description": "四足站立的中性姿态；非双足行走，非拟人化。",
        "eye_requirements": "占面部30%至40%的可爱卡通大眼睛，画出眼白、虹膜和瞳孔结构，瞳孔需要有颜色",
        "query": "将SYSTEM里的内容插入流程的各步骤输入，作为Prompt_initialpet的内容输出..." # 这里可以是具体的指令
    }
    
    run_simulation(DIFY_NODE_CONFIG, test_case)

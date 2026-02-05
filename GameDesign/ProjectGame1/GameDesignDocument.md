# 星际驿站 (Stellar Station) - 游戏开发设计文档 (GDD)

## 1. 项目概述 (Project Overview)
*   **游戏名称**：星际驿站 (Stellar Station)
*   **核心概念**：节点探险 + 基因模拟 + 物理沙盒
*   **目标平台**：PC / Mobile
*   **开发引擎**：Unity (推荐) 或 Godot
*   **一句话介绍**：带着外星萌宠去捡垃圾，回来给它们盖个家。

---

## 2. 核心玩法循环 (Core Loop)

```mermaid
graph LR
    Step1[**探险 (Exploration)**<br/>节点移动/背包决策] --> Step2[**鉴定 (Reveal)**<br/>清洗包裹/永久解锁]
    Step2 --> Step3[**入住 (Move-In)**<br/>2D模拟/3D实体化]
    Step3 --> Step4[**建设 (Build)**<br/>力场共鸣/满足需求]
    Step4 --> Step5[**互动 (Interact)**<br/>物理沙盒/上帝之手]
    Step5 --> Step1
```

---

## 3. 详细系统设计 (System Design)

### 3.1 阶段一：星际拾荒 (Exploration)
*   **核心机制**：节点地图探险 + 背包格子管理 (Tetris-lite)。
*   **地图结构**：
    *   **Node Graph**：地图由**节点 (Nodes)** 和 **连线 (Edges)** 构成。
    *   **迷雾 (Fog)**：仅相邻节点可见。
    *   **风险递增**：随着步数增加，遭遇危险事件的概率提升。
*   **流程**：
    1.  **极简筹备**：选择 1 只宠物出发（环境匹配提供 Buff/Debuff）。
    2.  **节点移动**：点击相邻节点移动。
    3.  **节点事件**：
        *   `物资点`：发现不同尺寸的包裹（1/2/4格）。
        *   `危险点`：属性判定（如力量判定），失败则丢弃物品或扣血。
        *   `撤离点`：起始点或隐藏信标，点击结算返航。
    4.  **背包决策**：背包满时，必须在“丢弃旧物”和“放弃新物”中做抉择。

### 3.2 阶段二：伙伴入住 (Move-In)
*   **核心机制**：2D 基因模拟 $\rightarrow$ 3D 实体化。
*   **流程**：
    1.  **基因模拟 (2D)**：投入基因，消耗少量资源生成一张 **2D 概念图**（拍立得风格）。如果不满意，可低成本重随。
    2.  **实体化 (3D)**：确认满意后，消耗大量资源将 2D 图片转化为游戏内的 **3D 实体**。
    3.  **性格生成**：系统基于 2D 图片的**视觉特征**（如大眼睛、强壮四肢）自动赋予性格标签（如[好奇]、[多动症]）。
*   **永久解锁**：基因图谱一旦获得即永久解锁，后续生成不再消耗基因物品。

### 3.3 阶段三：家园建设 (Construction)
*   **核心机制**：宠物中心主义 + 范围力场。
*   **建造系统**：
    *   **网格吸附**：家具放置在网格上。
    *   **范围力场**：功能性家具产生圆形/方形力场（如：暖炉 $\rightarrow$ 半径3格[温暖区]）。
    *   **无堆砌**：相同力场叠加只扩大范围，不增加数值强度。
*   **需求匹配**：
    *   宠物头顶冒出需求气泡（🔥/❄️/🍖）。
    *   只要宠物处于符合其性格标签的区域，心情即提升。

### 3.4 阶段四：生活与互动 (Interaction)
*   **核心机制**：AI 自主行为 + 物理沙盒 + 上帝之手。
*   **AI 行为 (Autonomous)**：
    *   基于性格标签的 FSM（状态机）：[多动症] 会跑酷，[懒癌] 会瘫倒。
*   **物理沙盒 (Physics)**：
    *   玩具具有真实物理属性（弹力、质量）。宠物会被球弹飞，会推倒纸箱。
*   **上帝之手 (God Hand)**：
    *   玩家可直接抓取宠物（拎后颈皮）、投掷宠物、抚摸或使用激光笔逗宠。
*   **社交剧场**：
    *   自动演算宠物间的追逐、模仿和冲突行为。

---

## 4. 技术架构 (Technical Architecture)

### 4.1 数据结构 (Data Models)

#### A. 地图与节点 (Map & Nodes)
```csharp
[System.Serializable]
public class MapNode {
    public int id;
    public NodeType type; // Start, Resource, Danger, Event
    public List<int> connectedNodeIds;
    public bool isRevealed;
}

[System.Serializable]
public class MapGraph {
    public string mapId;
    public List<MapNode> nodes;
}
```

#### B. 宠物数据 (Pet Data)
```csharp
[System.Serializable]
public class PetData {
    public string instanceId;
    public string name;
    // Visuals
    public string birthPhotoUrl; // 2D Preview
    public ModelConfig modelConfig; // 3D Assets
    // AI
    public List<string> personalityTags; // ["energetic", "curious"]
    public float mood;
}
```

#### C. 物品与背包 (Item & Inventory)
```csharp
[System.Serializable]
public class ItemData {
    public string id;
    public ItemType type; // DirtyPackage, Gene, Furniture
    public int size;      // 1, 2, 4 slots
}
```

### 4.2 核心系统 (Core Systems)
*   **MapManager**: 生成和管理节点图，处理迷雾和移动逻辑。
*   **InteractionSystem**: 处理物理射线检测（上帝之手），管理玩具物理碰撞。
*   **PetAISystem**: 基于性格标签的行为树/状态机，驱动宠物在 Idle/Play/Social 状态间切换。
*   **ConstructionSystem**: 处理网格吸附、力场计算和可视化。

---

## 5. Demo 开发计划 (Vertical Slice)

### 5.1 范围限制
*   **地图**：1 张包含 10-15 个节点的火山地图。
*   **角色**：2 只不同性格的宠物（一只[多动症]，一只[懒癌]）。
*   **物品**：3 种尺寸的包裹，1 个暖炉（力场演示），1 个瑜伽球（物理演示）。

### 5.2 开发步骤
1.  **Step 1: 节点移动与背包**
    *   实现节点图生成与点击移动。
    *   实现背包 Tetris 逻辑（拾取/丢弃）。
2.  **Step 2: 基地与实体化**
    *   实现简单的“2D图片 -> 3D模型”切换流程（模拟实体化）。
    *   实现清洗机开箱逻辑。
3.  **Step 3: 建设与力场**
    *   实现网格放置家具。
    *   实现力场范围检测（宠物进入暖炉范围变开心）。
4.  **Step 4: 物理互动**
    *   实现“上帝之手”抓取和投掷宠物。
    *   实现宠物与物理玩具的简单碰撞。

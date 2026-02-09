# 🎮 玩法可视化：SimPets 物理派对 (Gameplay Visualization)

> **用途**：用于团队内部快速对齐玩法思路。不包含局外循环，仅聚焦于**关卡内的核心体验**。

## 1. 五大玩法核心机制对比 (Core Mechanics Matrix)

```mermaid
mindmap
  root((核心玩法库))
    (方案3: 极限装车<br>Wobbly Packer)
      ::icon(fa fa-star)
      [核心动作: 堆叠 + 挤压]
      [操作焦点: 原地抓取]
      [胜利条件: 强行关上门]
      [开发成本: ⭐⭐⭐⭐⭐ (极低)]
      [体验: 强迫症爽感]
    (方案1: 软体快递<br>Jelly Express)
      [核心动作: 跑酷 + 平衡]
      [操作焦点: 移动 + 双手抓]
      [胜利条件: 抵达终点]
      [开发成本: ⭐⭐⭐ (中)]
      [体验: 跌跌撞撞]
    (方案2: 笨贼妙手<br>Clumsy Heist)
      [核心动作: 潜行 + 避障]
      [操作焦点: 微操控制]
      [胜利条件: 噪音条未满]
      [开发成本: ⭐⭐ (高)]
      [体验: 紧张滑稽]
    (方案4: 灾难求生<br>Survival Drill)
      [核心动作: 抓取 + 反应]
      [操作焦点: 死按住不放]
      [胜利条件: 存活倒计时]
      [开发成本: ⭐⭐⭐⭐ (低)]
      [体验: 劫后余生]
    (方案5: 软体清洁工<br>Clumsy Janitor)
      [核心动作: 工具 + 互动]
      [操作焦点: 挥动拖把]
      [胜利条件: 垃圾归位]
      [开发成本: ⭐ (极高)]
      [体验: 越帮越忙]
```

---

## 2. 推荐方案 (方案3) 详细交互流程

**方案：极限装车 (Wobbly Packer)**
*   **场景**：一辆后备箱敞开的卡车 + 一地散落的家具。
*   **目标**：把东西塞进去，关上门。

```mermaid
sequenceDiagram
    participant P as 玩家 (Player)
    participant H as 笨拙双手 (Hands)
    participant C as 货物 (Cargo)
    participant T as 卡车后备箱 (Truck)
    
    Note over P, T: 倒计时: 180秒
    
    loop 搬运循环
        P->>H: 1. 控制移动/抓取
        H->>C: 物理吸附 (Grab)
        C-->>H: 反馈重量/惯性 (笨拙感)
        
        alt 塞得进去
            H->>T: 2. 拖拽进车厢
            C->>C: 物理堆叠/挤压
        else 塞不进去
            C->>C: 掉落/弹飞
            P->>H: 重新抓取
        end
    end
    
    P->>T: 3. 按下 [关门] 按钮
    
    alt 门被卡住
        T-->>C: 物理碰撞检测
        T->>P: 门弹开 (Fail)
        P->>H: 4. 用身体撞门 (暴力关门)
    else 门关上了
        T->>P: 任务成功 (Success)
    end
```

---

## 3. 备选方案 (方案1) 详细交互流程

**方案：软体快递 (Jelly Express)**
*   **场景**：一条充满物理机关的赛道。
*   **目标**：抱着货物活着走到终点。

```mermaid
graph TD
    Start((起点: 接单)) --> Pick[抓取货物]
    Pick --> Move{移动过程}
    
    subgraph Physics_Challenge [物理挑战]
        direction TB
        Obstacle1[旋转盘: 离心力甩飞]
        Obstacle2[独木桥: 重心不稳]
        Obstacle3[强风口: 货物被吹跑]
    end
    
    Move --> Obstacle1
    Obstacle1 --> Obstacle2
    Obstacle2 --> Obstacle3
    
    Obstacle3 --> Check{货物还在吗?}
    Check -- 掉了 --> Recover[回头去捡]
    Recover --> Move
    Check -- 还在 --> Finish((终点: 交付))
    
    style Physics_Challenge fill:#f9f9f9,stroke:#333,stroke-dasharray: 5 5
```

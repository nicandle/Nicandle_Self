import csv

# --- 1. 基础定义 (Inputs) ---
ATTRIBUTES = {1: '力量', 2: '体质', 3: '敏捷', 4: '感知'}
RATINGS = {1: 'D', 2: 'C', 3: 'B', 4: 'A', 5: 'S'}
ELEMENTS = {0: '无', 101: '草', 102: '火', 103: '水'}
# 元素与属性的关联
ATTR_ELEMENT_MAP = {1: 102, 2: 101, 3: 103, 4: 0}

# --- 2. 主生成函数 ---
def generate_exploration_events():
    events = []
    event_id_counter = 1001001

    # --- 特殊格: 安全通过 ---
    events.append([
        event_id_counter, 1, '安全通过', 30, 0, 0, '', '', '', '', '1'
    ])
    event_id_counter += 1

    # --- 生成单属性事件 ---
    for attr_id, attr_name in ATTRIBUTES.items():
        for rating_val, rating_name in RATINGS.items():
            if rating_val <= 2: tier = 1
            elif rating_val <= 4: tier = 2
            else: tier = 3

            spawn_weight_map = {1: 15, 2: 15, 3: 10, 4: 8, 5: 5}
            explore_progress_map = {1: '1,2', 2: '2,3', 3: '3,5'}

            element_type = ATTR_ELEMENT_MAP[attr_id] if rating_val >= 4 else 0
            remark = f"T{tier}-单-{attr_name}-{rating_name}"

            events.append([
                event_id_counter, 1, remark, spawn_weight_map[rating_val], element_type, tier,
                attr_id, rating_val, '', '', explore_progress_map[tier]
            ])
            event_id_counter += 1

    # --- 生成双属性事件 ---
    attr_ids = list(ATTRIBUTES.keys())
    for i in range(len(attr_ids)):
        for j in range(i + 1, len(attr_ids)):
            attr1_id, attr2_id = attr_ids[i], attr_ids[j]
            attr1_name, attr2_name = ATTRIBUTES[attr1_id], ATTRIBUTES[attr2_id]

            for r1_val, r1_name in RATINGS.items():
                for r2_val, r2_name in RATINGS.items():
                    if r1_val <= 2 and r2_val <= 2: tier = 2
                    else: tier = 3

                    avg_rating = (r1_val + r2_val) // 2
                    spawn_weight_map = {1:7, 2:6, 3:4, 4:2, 5:1}
                    spawn_weight = spawn_weight_map.get(avg_rating, 1)

                    explore_progress_map = {2: '2,3', 3: '4,6'}
                    remark = f"T{tier}-双-{attr1_name}{r1_name}-{attr2_name}{r2_name}"

                    events.append([
                        event_id_counter, 1, remark, spawn_weight, 0, tier,
                        attr1_id, r1_val, attr2_id, r2_val, explore_progress_map[tier]
                    ])
                    event_id_counter += 1
    return events

# --- 3. 输出到文件 ---
def write_to_csv(events, filename="ExplorationEvents_Full.csv"):
    header = [
        'Id', 'Type', '备注', 'SpawnWeight', 'ElementType', 'DifficultyTier',
        'Attr1', 'Attr1_value', 'Attr2', 'Attr2_value', 'ExploreProgress'
    ]
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(events)
    print(f"成功生成完整探索事件表: {filename}")

# --- 执行 ---
if __name__ == "__main__":
    full_events = generate_exploration_events()
    write_to_csv(full_events)
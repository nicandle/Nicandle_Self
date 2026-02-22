-- 目标：统计新手引导和任务的完成人数，并按指定顺序输出漏斗数据
-- 数据库：nvwa_cbt1
-- 引擎：Spark SQL
-- 筛选条件：注册日期 20260129~20260130，IP 区域为 BR 或 ID

with player_base as (
    -- 第一步：获取 20260129-20260130 注册的玩家底表
    SELECT 
        account_id,
        ip_region as region
    FROM nvwa_cbt1.accountregister
    WHERE dt BETWEEN '20260129' AND '20260130'
      AND ip_region IN ('BR', 'ID')
),
guide_log as (
    -- 第二步：提取引导完成记录
    SELECT 
        account_id,
        guide_id
    FROM nvwa_cbt1.guidestep
    WHERE local_dt_srv >= '20260129'
    GROUP BY account_id, guide_id
),
task_log as (
    -- 第三步：提取任务完成记录 (task_action = 2 表示完成)
    SELECT 
        account_id,
        task_id
    FROM nvwa_cbt1.taskaction
    WHERE local_dt_srv >= '20260129'
      AND task_action = 2
    GROUP BY account_id, task_id
),
-- 定义漏斗顺序（根据 CSV 样例整理）
funnel_order as (
    SELECT 'Guide' as type, 100101 as id, 1 as sort_idx UNION ALL
    SELECT 'Guide', 100102, 2 UNION ALL
    SELECT 'Guide', 100201, 3 UNION ALL
    SELECT 'Guide', 100202, 4 UNION ALL
    SELECT 'Guide', 100203, 5 UNION ALL
    SELECT 'Task', 1010101, 6 UNION ALL
    SELECT 'Guide', 100204, 7 UNION ALL
    SELECT 'Guide', 100401, 8 UNION ALL
    SELECT 'Guide', 100402, 9 UNION ALL
    SELECT 'Guide', 100403, 10 UNION ALL
    SELECT 'Guide', 100404, 11 UNION ALL
    SELECT 'Guide', 100405, 12 UNION ALL
    SELECT 'Guide', 100406, 13 UNION ALL
    SELECT 'Guide', 100501, 14 UNION ALL
    SELECT 'Guide', 100502, 15 UNION ALL
    SELECT 'Task', 1010102, 16 UNION ALL
    SELECT 'Guide', 100601, 17 UNION ALL
    SELECT 'Guide', 100602, 18 UNION ALL
    SELECT 'Guide', 100603, 19 UNION ALL
    SELECT 'Guide', 100701, 20 UNION ALL
    SELECT 'Guide', 100702, 21 UNION ALL
    SELECT 'Guide', 100703, 22 UNION ALL
    SELECT 'Guide', 100704, 23 UNION ALL
    SELECT 'Guide', 100705, 24 UNION ALL
    SELECT 'Guide', 100706, 25 UNION ALL
    SELECT 'Guide', 100707, 26 UNION ALL
    SELECT 'Guide', 100708, 27 UNION ALL
    SELECT 'Guide', 100709, 28 UNION ALL
    SELECT 'Guide', 100801, 29 UNION ALL
    SELECT 'Task', 1010201, 30 UNION ALL
    SELECT 'Task', 10102011, 31 UNION ALL
    SELECT 'Task', 10102012, 32 UNION ALL
    SELECT 'Guide', 101101, 33 UNION ALL
    SELECT 'Task', 10102013, 34 UNION ALL
    SELECT 'Task', 1010202, 35 UNION ALL
    SELECT 'Task', 1010301, 36 UNION ALL
    SELECT 'Task', 1010302, 37 UNION ALL
    SELECT 'Task', 1010303, 38 UNION ALL
    SELECT 'Task', 1010402, 39 UNION ALL
    SELECT 'Task', 1010403, 40 UNION ALL
    SELECT 'Task', 10104031, 41 UNION ALL
    SELECT 'Task', 1010404, 42 UNION ALL
    SELECT 'Task', 10104041, 43 UNION ALL
    SELECT 'Task', 10104042, 44 UNION ALL
    SELECT 'Task', 10104043, 45 UNION ALL
    SELECT 'Task', 1010501, 46 UNION ALL
    SELECT 'Task', 1010502, 47 UNION ALL
    SELECT 'Task', 1010503, 48 UNION ALL
    SELECT 'Task', 1010504, 49 UNION ALL
    SELECT 'Task', 1010601, 50 UNION ALL
    SELECT 'Task', 1010602, 51 UNION ALL
    SELECT 'Task', 1010603, 52 UNION ALL
    SELECT 'Task', 1010604, 53 UNION ALL
    SELECT 'Task', 1010605, 54 UNION ALL
    SELECT 'Task', 1010701, 55 UNION ALL
    SELECT 'Task', 1010702, 56 UNION ALL
    SELECT 'Task', 1010703, 57 UNION ALL
    SELECT 'Task', 10107031, 58 UNION ALL
    SELECT 'Task', 10107032, 59 UNION ALL
    SELECT 'Task', 1010801, 60 UNION ALL
    SELECT 'Task', 1010802, 61 UNION ALL
    SELECT 'Task', 1010803, 62 UNION ALL
    SELECT 'Task', 1010901, 63 UNION ALL
    SELECT 'Task', 1010902, 64 UNION ALL
    SELECT 'Task', 10109021, 65 UNION ALL
    SELECT 'Task', 10109022, 66 UNION ALL
    SELECT 'Task', 1010903, 67 UNION ALL
    SELECT 'Task', 1010904, 68 UNION ALL
    SELECT 'Task', 1010905, 69 UNION ALL
    SELECT 'Task', 1011001, 70 UNION ALL
    SELECT 'Task', 1011002, 71 UNION ALL
    SELECT 'Task', 1011003, 72 UNION ALL
    SELECT 'Task', 1011004, 73 UNION ALL
    SELECT 'Task', 1011101, 74 UNION ALL
    SELECT 'Task', 10111011, 75 UNION ALL
    SELECT 'Task', 1011102, 76 UNION ALL
    SELECT 'Task', 1011103, 77 UNION ALL
    SELECT 'Task', 1011104, 78 UNION ALL
    SELECT 'Task', 1011105, 79 UNION ALL
    SELECT 'Task', 1011201, 80 UNION ALL
    SELECT 'Task', 1011202, 81 UNION ALL
    SELECT 'Task', 1011203, 82 UNION ALL
    SELECT 'Task', 1011301, 83 UNION ALL
    SELECT 'Task', 1011302, 84 UNION ALL
    SELECT 'Task', 1011303, 85 UNION ALL
    SELECT 'Task', 1011304, 86 UNION ALL
    SELECT 'Task', 1011305, 87 UNION ALL
    SELECT 'Task', 10113051, 88 UNION ALL
    SELECT 'Task', 1011306, 89 UNION ALL
    SELECT 'Task', 1011401, 90 UNION ALL
    SELECT 'Task', 1011402, 91 UNION ALL
    SELECT 'Task', 1011403, 92 UNION ALL
    SELECT 'Task', 1011404, 93 UNION ALL
    SELECT 'Task', 1011405, 94 UNION ALL
    SELECT 'Task', 1011501, 95 UNION ALL
    SELECT 'Task', 1011502, 96 UNION ALL
    SELECT 'Task', 1011503, 97 UNION ALL
    SELECT 'Task', 10115031, 98 UNION ALL
    SELECT 'Task', 1011601, 99 UNION ALL
    SELECT 'Task', 1011602, 100 UNION ALL
    SELECT 'Task', 1011603, 101 UNION ALL
    SELECT 'Task', 1011604, 102 UNION ALL
    SELECT 'Task', 1011605, 103 UNION ALL
    SELECT 'Task', 1011606, 104 UNION ALL
    SELECT 'Task', 1011701, 105 UNION ALL
    SELECT 'Task', 10117011, 106 UNION ALL
    SELECT 'Task', 1011702, 107 UNION ALL
    SELECT 'Task', 1011703, 108 UNION ALL
    SELECT 'Task', 1011704, 109 UNION ALL
    SELECT 'Task', 1011705, 110 UNION ALL
    SELECT 'Task', 1011801, 111 UNION ALL
    SELECT 'Task', 1011802, 112 UNION ALL
    SELECT 'Task', 1011803, 113 UNION ALL
    SELECT 'Task', 1011804, 114 UNION ALL
    SELECT 'Task', 1011805, 115 UNION ALL
    SELECT 'Task', 1011901, 116 UNION ALL
    SELECT 'Task', 1011902, 117 UNION ALL
    SELECT 'Task', 10119021, 118 UNION ALL
    SELECT 'Task', 1011903, 119 UNION ALL
    SELECT 'Task', 1011904, 120 UNION ALL
    SELECT 'Task', 1011905, 121 UNION ALL
    SELECT 'Task', 1011906, 122 UNION ALL
    SELECT 'Task', 1012001, 123 UNION ALL
    SELECT 'Task', 1012002, 124 UNION ALL
    SELECT 'Task', 1012003, 125 UNION ALL
    SELECT 'Task', 1012004, 126 UNION ALL
    SELECT 'Task', 10120041, 127
),
-- 计算每个步骤在不同地区的完成人数
step_counts as (
    SELECT 
        pb.region,
        fo.type,
        fo.id,
        fo.sort_idx,
        count(distinct 
            case 
                when fo.type = 'Guide' and gl.account_id is not null then pb.account_id
                when fo.type = 'Task' and tl.account_id is not null then pb.account_id
                else null 
            end
        ) as user_count
    FROM player_base pb
    CROSS JOIN funnel_order fo
    LEFT JOIN guide_log gl ON pb.account_id = gl.account_id AND fo.id = gl.guide_id AND fo.type = 'Guide'
    LEFT JOIN task_log tl ON pb.account_id = tl.account_id AND fo.id = tl.task_id AND fo.type = 'Task'
    GROUP BY pb.region, fo.type, fo.id, fo.sort_idx
),
-- 计算漏斗和流失率
final_stats as (
    SELECT 
        region as `国家`,
        type as `类型`,
        id as `id`,
        user_count as `人数`,
        sort_idx, -- 保留排序索引
        -- 漏斗：当前人数 / 第一步人数
        round(user_count * 100.0 / first_value(user_count) over(partition by region order by sort_idx), 2) as `漏斗(%)`,
        -- 流失率：(上一步人数 - 当前人数) / 第一步人数
        round((lag(user_count, 1, user_count) over(partition by region order by sort_idx) - user_count) * 100.0 / first_value(user_count) over(partition by region order by sort_idx), 2) as `流失率(%)`
    FROM step_counts
)
SELECT 
    `国家`,
    `类型`,
    `id`,
    `人数`,
    `漏斗(%)`,
    `流失率(%)`
FROM final_stats
ORDER BY `国家`, sort_idx;

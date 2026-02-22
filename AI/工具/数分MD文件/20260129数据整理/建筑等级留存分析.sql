-- 目标：分析 building_type=101 的建筑等级分布及其对应的玩家留存情况
-- 数据库：nvwa_cbt1 (原始日志), nvwa_cooked_cbt1 (留存底表)
-- 引擎：Trino (Presto) 终极修复版
-- 核心策略：彻底移除 = 1 这种 bigint 比较，改用字符串比较，并对 SUM 结果进行显式转换

with player_base as (
    -- 第一步：获取目标注册玩家底表
    SELECT 
        local_dt,
        region,
        account_id,
        -- 彻底隔离类型：将 is_r2 转换为字符串后再进行字符串比较，返回数字
        case 
            when cast(is_r2 as varchar) = '1' or cast(is_r2 as varchar) = 'true' then 1 
            else 0 
        end as is_r2_flag
    FROM nvwa_cooked_cbt1.dws_user_register_account_retention_d_i
    WHERE local_dt BETWEEN '20260127' AND '20260128'
      AND ip_region IN ('BR', 'ID')
),
building_log as (
    -- 第二步：提取最高等级
    SELECT 
        account_id,
        max(building_level) as max_level
    FROM nvwa_cbt1.homebuild
    WHERE local_dt_srv >= '20260127' 
      AND building_type = 101
    GROUP BY account_id
)
-- 第三步：聚合统计
-- 关键：Trino 在处理 SUM 和 COUNT 混合计算时，有时会因为别名引用触发类型推导错误
-- 我们在 GROUP BY 中显式写出所有表达式，并确保计算中不出现隐式转换
SELECT 
    t1.region as "游戏大区",
    coalesce(t2.max_level, 1) as "建筑等级", 
    count(distinct t1.account_id) as "该等级玩家总数",
    -- 使用 sum 统计处理好的数字标志位
    sum(t1.is_r2_flag) as "留存玩家数",
    -- 显式计算流失人数
    count(distinct t1.account_id) - sum(t1.is_r2_flag) as "流失玩家数",
    -- 计算留存率：确保分子分母都是浮点数或显式转换
    round(cast(sum(t1.is_r2_flag) as double) * 100.0 / cast(nullif(count(distinct t1.account_id), 0) as double), 2) as "次留率(%)"
FROM player_base t1
LEFT JOIN building_log t2 ON t1.account_id = t2.account_id
GROUP BY t1.region, coalesce(t2.max_level, 1)
ORDER BY t1.region, "建筑等级" ASC;

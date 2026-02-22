-- 目标：分析 building_type=101 的建筑等级分布及其对应的玩家留存情况
-- 数据库：nvwa_cbt1 (原始日志), nvwa_cooked_cbt1 (留存底表)
-- 引擎：Spark SQL 存档版
-- 筛选条件：注册日期 20260127~20260128，IP 区域为 BR 或 ID

with player_base as (
    -- 第一步：获取目标注册玩家底表（27-28号注册，且在指定地区）
    SELECT 
        local_dt,
        region,
        account_id,
        -- Spark 兼容性处理：转换为数字 1 或 0
        case 
            when cast(is_r2 as string) = '1' or cast(is_r2 as string) = 'true' then 1 
            else 0 
        end as is_r2_flag
    FROM nvwa_cooked_cbt1.dws_user_register_account_retention_d_i
    WHERE local_dt BETWEEN '20260127' AND '20260128'
      AND ip_region IN ('BR', 'ID')
),
building_log as (
    -- 第二步：提取这些玩家关于 101 建筑的最高等级记录
    SELECT 
        account_id,
        max(building_level) as max_level
    FROM nvwa_cbt1.homebuild
    WHERE local_dt_srv >= '20260127' 
      AND building_type = 101
    GROUP BY account_id
)
-- 第三步：以玩家底表为主，关联等级信息并聚合统计
-- Spark SQL 使用反引号 ` 来引用中文列名
SELECT 
    t1.region as `游戏大区`,
    coalesce(t2.max_level, 1) as `建筑等级`, 
    count(distinct t1.account_id) as `该等级玩家总数`,
    sum(t1.is_r2_flag) as `留存玩家数`,
    count(distinct t1.account_id) - sum(t1.is_r2_flag) as `流失玩家数`,
    round(sum(t1.is_r2_flag) * 100.0 / nullif(count(distinct t1.account_id), 0), 2) as `次留率(%)`
FROM player_base t1
LEFT JOIN building_log t2 ON t1.account_id = t2.account_id
GROUP BY t1.region, coalesce(t2.max_level, 1)
ORDER BY t1.region, `建筑等级` ASC;

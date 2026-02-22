-- 目标：提取家园等级为 1 且孵化次数大于等于 6 次的玩家 ID 列表
-- 数据库：nvwa_cbt1 (原始日志), nvwa_cooked_cbt1 (留存底表)
-- 引擎要求：Spark SQL

with player_base as (
    -- 第一步：获取目标注册玩家底表（27-28号注册，且在指定地区）
    SELECT 
        region,
        account_id
    FROM nvwa_cooked_cbt1.dws_user_register_account_retention_d_i
    WHERE local_dt BETWEEN '20260127' AND '20260128'
      AND ip_region IN ('BR', 'ID')
),
home_level_info as (
    -- 第二步：提取每个玩家的最高家园等级 (building_type=101)
    SELECT 
        account_id,
        max(building_level) as home_level
    FROM nvwa_cbt1.homebuild
    WHERE local_dt_srv >= '20260127'
      AND building_type = 101
    GROUP BY account_id
),
hatch_stats as (
    -- 第三步：统计每个玩家的孵化次数 (PetCreateCustom)
    SELECT 
        account_id,
        count(*) as hatch_count
    FROM nvwa_cbt1.PetCreateCustom
    WHERE local_dt_srv >= '20260127'
    GROUP BY account_id
    HAVING count(*) >= 6 -- 筛选孵化次数 6 次及以上的玩家
)
-- 第四步：关联并筛选家园等级为 1 的玩家
SELECT 
    p.region as `游戏大区`,
    p.account_id as `玩家ID`,
    coalesce(hl.home_level, 1) as `家园等级`,
    hs.hatch_count as `孵化次数`
FROM player_base p
INNER JOIN hatch_stats hs ON p.account_id = hs.account_id
LEFT JOIN home_level_info hl ON p.account_id = hl.account_id
WHERE coalesce(hl.home_level, 1) = 1 -- 筛选家园等级为 1 的玩家
ORDER BY p.region, hs.hatch_count DESC;

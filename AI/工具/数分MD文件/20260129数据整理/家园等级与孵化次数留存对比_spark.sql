-- 目标：分析相同家园等级下，不同孵化次数玩家的留存对比
-- 数据库：nvwa_cbt1 (原始日志), nvwa_cooked_cbt1 (留存底表)
-- 引擎要求：Spark SQL

with player_base as (
    -- 第一步：获取目标注册玩家底表（0129和0130注册，且在指定地区）
    SELECT 
        region,
        account_id,
        case 
            when cast(is_r2 as string) = '1' or cast(is_r2 as string) = 'true' then 1 
            else 0 
        end as is_r2_flag
    FROM nvwa_cooked_cbt1.dws_user_register_account_retention_d_i
    WHERE local_dt BETWEEN '20260129' AND '20260130'
      AND ip_region IN ('BR', 'ID')
),
home_level_info as (
    -- 第二步：提取每个玩家的最高家园等级 (假设 building_type=101 代表家园核心建筑)
    SELECT 
        account_id,
        max(building_level) as home_level
    FROM nvwa_cbt1.homebuild
    WHERE local_dt_srv >= '20260129'
      AND building_type = 101
    GROUP BY account_id
),
hatch_stats as (
    -- 第三步：统计每个玩家注册当天的孵化次数 (PetCreateCustom) 并分档，只看首日、用于次留分析
    SELECT 
        p.account_id,
        count(h.account_id) as raw_hatch_count,
        case 
            when count(h.account_id) = 0 then '0次'
            when count(h.account_id) = 1 then '1次'
            when count(h.account_id) = 2 then '2次'
            when count(h.account_id) = 3 then '3次'
            when count(h.account_id) = 4 then '4次'
            when count(h.account_id) = 5 then '5次'
            when count(h.account_id) >= 6 then '6次+'
            else '0次'
        end as hatch_tag
    FROM (
        SELECT account_id, local_dt as register_dt
        FROM nvwa_cooked_cbt1.dws_user_register_account_retention_d_i
        WHERE local_dt BETWEEN '20260129' AND '20260130' AND ip_region IN ('BR', 'ID')
    ) p
    LEFT JOIN nvwa_cbt1.PetCreateCustom h ON p.account_id = h.account_id AND h.local_dt_srv = p.register_dt
    GROUP BY p.account_id
)
-- 第四步：聚合统计相同家园等级下，不同孵化档位的留存表现
SELECT 
    p.region as `游戏大区`,
    coalesce(hl.home_level, 1) as `家园等级`,
    coalesce(hs.hatch_tag, '0次') as `孵化次数档位`,
    count(distinct p.account_id) as `玩家总数`,
    sum(p.is_r2_flag) as `留存玩家数`,
    count(distinct p.account_id) - sum(p.is_r2_flag) as `流失玩家数`,
    concat(round(sum(p.is_r2_flag) * 100.0 / nullif(count(distinct p.account_id), 0), 2), '%') as `次留率`
FROM player_base p
LEFT JOIN home_level_info hl ON p.account_id = hl.account_id
LEFT JOIN hatch_stats hs ON p.account_id = hs.account_id
GROUP BY 1, 2, 3
ORDER BY 1, 2 ASC, 3 ASC;

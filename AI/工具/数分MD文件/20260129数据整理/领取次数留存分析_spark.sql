-- 目标：统计不同【领取次数】下的玩家分布及留存情况（忽略孵化次数）
-- 数据库：nvwa_cbt1 (原始日志), nvwa_cooked_cbt1 (留存底表)
-- 引擎要求：Spark SQL

with player_base as (
    -- 第一步：获取目标注册玩家底表（27-28号注册，且在指定地区）
    SELECT 
        region,
        account_id,
        -- 留存标志处理：1为留存，0为流失
        case 
            when cast(is_r2 as string) = '1' or cast(is_r2 as string) = 'true' then 1 
            else 0 
        end as is_r2_flag
    FROM nvwa_cooked_cbt1.dws_user_register_account_retention_d_i
    WHERE local_dt BETWEEN '20260127' AND '20260128'
      AND ip_region IN ('BR', 'ID')
),
claim_stats as (
    -- 第二步：统计每个玩家的累计领取次数 (PetClaim)
    SELECT 
        account_id,
        count(*) as claim_count
    FROM nvwa_cbt1.PetClaim
    WHERE local_dt_srv >= '20260127'
    GROUP BY account_id
)
-- 第三步：聚合统计不同领取次数下的留存表现
SELECT 
    p.region as `游戏大区`,
    coalesce(c.claim_count, 0) as `领取次数`,
    count(distinct p.account_id) as `玩家总数`,
    sum(p.is_r2_flag) as `留存玩家数`,
    count(distinct p.account_id) - sum(p.is_r2_flag) as `流失玩家数`,
    concat(round(sum(p.is_r2_flag) * 100.0 / nullif(count(distinct p.account_id), 0), 2), '%') as `次留率`,
    concat(round(sum(p.is_r2_flag) * 100.0 / nullif(sum(count(distinct p.account_id)) over(partition by p.region), 0), 2), '%') as `留存玩家占总玩家比例`
FROM player_base p
LEFT JOIN claim_stats c ON p.account_id = c.account_id
GROUP BY 1, 2
ORDER BY 1, 2 ASC;

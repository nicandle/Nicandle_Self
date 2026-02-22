-- 目标：统计【至少有1次领取记录】且【总孵化次数 >= 2】的玩家留存情况
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
hatch_stats as (
    -- 第二步：统计每个玩家的孵化次数 (PetCreateCustom)
    SELECT 
        account_id,
        count(*) as hatch_count
    FROM nvwa_cbt1.PetCreateCustom
    WHERE local_dt_srv >= '20260127'
    GROUP BY account_id
    HAVING count(*) >= 2 -- 筛选总孵化次数 >= 2 的玩家
),
claim_stats as (
    -- 第三步：统计每个玩家的领取次数 (PetClaim)
    SELECT 
        account_id,
        count(*) as claim_count
    FROM nvwa_cbt1.PetClaim
    WHERE local_dt_srv >= '20260127'
    GROUP BY account_id
    HAVING count(*) >= 1 -- 筛选至少有 1 次领取记录的玩家
)
-- 第四步：聚合统计符合条件的玩家留存表现
SELECT 
    p.region as `游戏大区`,
    count(distinct p.account_id) as `符合条件玩家总数`,
    sum(p.is_r2_flag) as `留存玩家数`,
    count(distinct p.account_id) - sum(p.is_r2_flag) as `流失玩家数`,
    concat(round(sum(p.is_r2_flag) * 100.0 / nullif(count(distinct p.account_id), 0), 2), '%') as `次留率`
FROM player_base p
INNER JOIN hatch_stats h ON p.account_id = h.account_id
INNER JOIN claim_stats c ON p.account_id = c.account_id
GROUP BY 1
ORDER BY 1 ASC;

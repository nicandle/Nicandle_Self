-- 目标：统计不同【孵化次数】与【领取次数】组合下的玩家分布及留存情况
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
),
claim_stats as (
    -- 第三步：统计每个玩家的领取次数 (PetClaim)
    SELECT 
        account_id,
        count(*) as claim_count
    FROM nvwa_cbt1.PetClaim
    WHERE local_dt_srv >= '20260127'
    GROUP BY account_id
),
user_combined_stats as (
    -- 第四步：合并玩家的孵化与领取数据
    SELECT 
        p.region,
        p.account_id,
        p.is_r2_flag,
        coalesce(h.hatch_count, 0) as hatch_count,
        coalesce(c.claim_count, 0) as claim_count
    FROM player_base p
    LEFT JOIN hatch_stats h ON p.account_id = h.account_id
    LEFT JOIN claim_stats c ON p.account_id = c.account_id
)
-- 第五步：按【孵化次数】和【领取次数】的组合进行聚合统计
SELECT 
    region as `游戏大区`,
    hatch_count as `孵化次数`,
    claim_count as `领取次数`,
    count(distinct account_id) as `玩家总数`,
    sum(is_r2_flag) as `留存玩家数`,
    count(distinct account_id) - sum(is_r2_flag) as `流失玩家数`,
    round(sum(is_r2_flag) * 100.0 / nullif(count(distinct account_id), 0), 2) as `次留率(%)`
FROM user_combined_stats
GROUP BY 1, 2, 3
ORDER BY 1, 2 ASC, 3 ASC;

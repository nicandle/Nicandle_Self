-- 目标：分析孵化机会的倾向性（动力强度）
-- 逻辑：
-- 1. 基础人群：当日有领取孵化行为的用户 (PetClaim)
-- 2. 倾向性指标：在基础人群中，起孵化次数 (PetCreateCustom) >= 2 的用户占比
-- 数据库：nvwa_cbt1, nvwa_cooked_cbt1

with player_base as (
    -- 第一步：获取目标注册玩家底表（27-28号注册，且在指定地区）
    SELECT 
        region,
        account_id,
        case 
            when cast(is_r2 as string) = '1' or cast(is_r2 as string) = 'true' then 1 
            else 0 
        end as is_r2_flag
    FROM nvwa_cooked_cbt1.dws_user_register_account_retention_d_i
    WHERE local_dt BETWEEN '20260127' AND '20260128'
      AND ip_region IN ('BR', 'ID')
),
claim_users as (
    -- 第二步：获取当日有领取行为的用户 (数据1：领取孵化的当日用户数)
    SELECT 
        account_id,
        count(*) as claim_total_count
    FROM nvwa_cbt1.PetClaim
    WHERE local_dt_srv >= '20260127'
    GROUP BY account_id
),
hatch_stats as (
    -- 第三步：统计这些用户的起孵化次数 (PetCreateCustom)
    SELECT 
        account_id,
        count(*) as hatch_total_count
    FROM nvwa_cbt1.PetCreateCustom
    WHERE local_dt_srv >= '20260127'
    GROUP BY account_id
)
-- 第四步：聚合统计
SELECT 
    p.region as `游戏大区`,
    count(distinct c.account_id) as `领取孵化总用户数(数据1)`,
    count(distinct case when h.hatch_total_count >= 3 then c.account_id end) as `起孵化大于等于3次用户数(数据2)`,
    concat(round(count(distinct case when h.hatch_total_count >= 3 then c.account_id end) * 100.0 / nullif(count(distinct c.account_id), 0), 2), '%') as `孵化倾向强度(数据2/数据1)`,
    -- 留存相关分析
    sum(case when h.hatch_total_count >= 3 then p.is_r2_flag else 0 end) as `高倾向留存玩家数`,
    concat(round(sum(case when h.hatch_total_count >= 3 then p.is_r2_flag else 0 end) * 100.0 / nullif(count(distinct case when h.hatch_total_count >= 3 then c.account_id end), 0), 2), '%') as `高倾向玩家次留率`
FROM player_base p
INNER JOIN claim_users c ON p.account_id = c.account_id
LEFT JOIN hatch_stats h ON p.account_id = h.account_id
GROUP BY 1
ORDER BY 1 ASC;

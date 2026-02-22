-- 目标：分析孵化机会的倾向性（动力强度）多阶梯分布
-- 逻辑：
-- 1. 基础人群：当日有领取孵化行为的用户 (数据1：领取总用户数)
-- 2. 倾向性阶梯：在基础人群中，分别统计起孵化次数 >=3, >=4, >=5, >=6, >=7 的用户数及占比
-- 数据库：nvwa_cbt1, nvwa_cooked_cbt1

with player_base as (
    -- 第一步：获取目标注册玩家底表（1.30当日注册，且在指定地区）
    SELECT 
        region,
        account_id,
        case 
            when cast(is_r2 as string) = '1' or cast(is_r2 as string) = 'true' then 1 
            else 0 
        end as is_r2_flag
    FROM nvwa_cooked_cbt1.dws_user_register_account_retention_d_i
    WHERE local_dt = '20260130'
      AND ip_region IN ('BR', 'ID')
),
claim_users as (
    -- 第二步：获取当日有领取行为的用户 (数据1基准)
    SELECT 
        account_id
    FROM nvwa_cbt1.PetClaim
    WHERE local_dt_srv >= '20260130'
    GROUP BY account_id
),
hatch_stats as (
    -- 第三步：统计这些用户的起孵化次数
    SELECT 
        account_id,
        count(*) as hatch_total_count
    FROM nvwa_cbt1.PetCreateCustom
    WHERE local_dt_srv >= '20260130'
    GROUP BY account_id
),
user_combined as (
    -- 第四步：合并数据，为每个领取玩家打上孵化阶梯标签
    SELECT 
        p.region,
        p.account_id,
        p.is_r2_flag,
        coalesce(h.hatch_total_count, 0) as hatch_count
    FROM player_base p
    INNER JOIN claim_users c ON p.account_id = c.account_id
    LEFT JOIN hatch_stats h ON p.account_id = h.account_id
),
thresholds as (
    -- 第五步：定义阶梯阈值（用于交叉连接生成表格结构）
    SELECT explode(array(3, 4, 5, 6, 7)) as min_hatch
)
-- 第六步：最终聚合统计
SELECT 
    u.region as `游戏大区`,
    t.min_hatch as `孵化次数阈值(>=N)`,
    count(distinct u.account_id) as `符合条件用户数(数据2)`,
    -- 计算占比：数据2 / 数据1 (该大区下所有领取用户的总数)
    concat(round(count(distinct u.account_id) * 100.0 / nullif(first(total_claim_users_in_region), 0), 2), '%') as `倾向强度占比`,
    sum(u.is_r2_flag) as `留存玩家数`,
    concat(round(sum(u.is_r2_flag) * 100.0 / nullif(count(distinct u.account_id), 0), 2), '%') as `次留率`
FROM (
    -- 预计算每个大区的总领取人数，避免在聚合时产生歧义
    -- 修复：Spark 不支持 count(distinct) 窗口函数，改用 size(collect_set())
    SELECT 
        *,
        size(collect_set(account_id) over(partition by region)) as total_claim_users_in_region
    FROM user_combined
) u
CROSS JOIN thresholds t
WHERE u.hatch_count >= t.min_hatch
GROUP BY u.region, t.min_hatch
ORDER BY u.region ASC, t.min_hatch ASC;

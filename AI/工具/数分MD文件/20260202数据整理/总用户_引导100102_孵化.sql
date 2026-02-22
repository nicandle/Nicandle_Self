-- 目标：统计29/30日注册用户数、完成 GuideStep guide_id=100102 用户数、生涯完成1次孵化用户数，按地区展示
-- 逻辑：在总用户_孵化基础上，在两档人数之间增加「双地区完成 GuideStep 中 guide_id=100102 的人数」（有该 step 日志即计 1 人）
-- 数据库：nvwa_cbt1, nvwa_cooked_cbt1
-- 引擎：Spark SQL
-- 筛选条件：注册日期 20260129、20260130，IP 区域为 BR 或 ID

with player_base as (
    -- 第一步：获取29/30日注册玩家底表（加工表，local_dt；按注册日、地区）
    SELECT 
        local_dt as register_dt,
        region,
        account_id
    FROM nvwa_cooked_cbt1.dws_user_register_account_retention_d_i
    WHERE local_dt IN ('20260129', '20260130')
      AND ip_region IN ('BR', 'ID')
),
guide_100102 as (
    -- 第二步：完成 GuideStep guide_id=100102 的用户（有该 step_id 的日志即计 1 人）
    SELECT 
        account_id
    FROM nvwa_cbt1.guidestep
    WHERE guide_id = 100102
    GROUP BY account_id
),
hatch_once as (
    -- 第三步：生涯至少完成1次孵化的用户（PetClaim 至少1条即为完成1次孵化）
    SELECT 
        account_id
    FROM nvwa_cbt1.PetClaim
    GROUP BY account_id
)
SELECT 
    p.register_dt as `注册日期`,
    p.region as `地区`,
    count(distinct p.account_id) as `注册用户数`,
    count(distinct case when g.account_id is not null then p.account_id end) as `完成guide_id100102用户数`,
    count(distinct case when h.account_id is not null then p.account_id end) as `完成1次孵化用户数`
FROM player_base p
LEFT JOIN guide_100102 g ON p.account_id = g.account_id
LEFT JOIN hatch_once h ON p.account_id = h.account_id
GROUP BY p.register_dt, p.region
ORDER BY p.register_dt ASC, p.region ASC;

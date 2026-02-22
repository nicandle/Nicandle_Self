-- 目标：统计第一天留存的用户，在第二天时的孵化次数增量和主城等级增量
-- 数据库：nvwa_cbt1
-- 引擎：Spark SQL
-- 定义：
--   1. 第一天留存用户：注册日期为 T，在 T+1 日有活跃行为的用户。
--   2. 次日定义：
--      - 0129 注册的用户，统计 0130 的数据。
--      - 0130 注册的用户，统计 0131 的数据。
--   3. 孵化次数增量：用户在 T+1 日当天的孵化次数（即 T+1 日累计次数 - T 日累计次数）。
--   4. 主城等级增量：(T+1 日主城最大等级) - (T 日主城最大等级)。只统计 building_type = 101。

WITH 
-- 1. 注册用户基础表 (T日)
RegisterUsers AS (
    SELECT 
        account_id,
        dt as reg_dt,
        ip_region as region
    FROM nvwa_cbt1.accountregister
    WHERE dt BETWEEN '20260129' AND '20260130'
      AND ip_region IN ('BR', 'ID')
),

-- 2. 用户活跃日志 (用于判断留存 - 只要 T+1 日有任意行为)
UserActiveDays AS (
    SELECT account_id, substring(cast(local_dt_srv as string), 1, 8) as active_dt FROM nvwa_cbt1.taskaction WHERE local_dt_srv >= '20260130'
    UNION
    SELECT account_id, substring(cast(local_dt_srv as string), 1, 8) as active_dt FROM nvwa_cbt1.PetCreateCustom WHERE local_dt_srv >= '20260130'
    UNION
    SELECT account_id, substring(cast(local_dt_srv as string), 1, 8) as active_dt FROM nvwa_cbt1.homebuild WHERE local_dt_srv >= '20260130'
),

-- 3. 筛选留存用户 (T+1日有活跃)
RetainedUsers AS (
    SELECT DISTINCT
        r.account_id,
        r.reg_dt,
        r.region,
        date_format(date_add(to_date(r.reg_dt, 'yyyyMMdd'), 1), 'yyyyMMdd') as next_day_dt
    FROM RegisterUsers r
    JOIN UserActiveDays a ON r.account_id = a.account_id AND a.active_dt = date_format(date_add(to_date(r.reg_dt, 'yyyyMMdd'), 1), 'yyyyMMdd')
),

-- 4. 次日孵化数据 (增量)
-- 统计 T+1 日当天的孵化次数。这等同于 (截止 T+1 日累计 - 截止 T 日累计)
HatchDailyCount AS (
    SELECT 
        account_id,
        substring(cast(local_dt_srv as string), 1, 8) as dt,
        count(*) as hatch_count
    FROM nvwa_cbt1.PetCreateCustom
    WHERE local_dt_srv >= '20260130'
    GROUP BY account_id, substring(cast(local_dt_srv as string), 1, 8)
),

-- 5. 主城等级数据 (只看 building_type = 101)
-- 分别获取 T 日和 T+1 日的最大等级
HomeLevelStats AS (
    SELECT 
        account_id,
        substring(cast(local_dt_srv as string), 1, 8) as dt,
        max(building_level) as max_level
    FROM nvwa_cbt1.homebuild
    WHERE local_dt_srv >= '20260129'
      AND building_type = 101
    GROUP BY account_id, substring(cast(local_dt_srv as string), 1, 8)
)

-- 6. 最终统计
SELECT 
    r.reg_dt as `注册日期`,
    r.region as `地区`,
    count(distinct r.account_id) as `次日留存用户数`,
    
    -- 孵化增量统计 (直接取次日当天的次数)
    sum(coalesce(h.hatch_count, 0)) as `次日总孵化增量`,
    round(avg(coalesce(h.hatch_count, 0)), 2) as `人均次日孵化增量`,
    
    -- 主城等级增量统计
    -- 逻辑：Day2_Max - Day1_Max。
    -- Day1 缺省为 1。Day2 缺省为 Day1 的值 (即增量为0)。
    sum(
        case 
            when coalesce(hl2.max_level, coalesce(hl1.max_level, 1)) > coalesce(hl1.max_level, 1) 
            then coalesce(hl2.max_level, coalesce(hl1.max_level, 1)) - coalesce(hl1.max_level, 1)
            else 0 
        end
    ) as `次日总主城等级增量`,
    
    round(avg(
        case 
            when coalesce(hl2.max_level, coalesce(hl1.max_level, 1)) > coalesce(hl1.max_level, 1) 
            then coalesce(hl2.max_level, coalesce(hl1.max_level, 1)) - coalesce(hl1.max_level, 1)
            else 0 
        end
    ), 2) as `人均次日主城等级增量`

FROM RetainedUsers r
LEFT JOIN HatchDailyCount h ON r.account_id = h.account_id AND r.next_day_dt = h.dt
LEFT JOIN HomeLevelStats hl1 ON r.account_id = hl1.account_id AND r.reg_dt = hl1.dt
LEFT JOIN HomeLevelStats hl2 ON r.account_id = hl2.account_id AND r.next_day_dt = hl2.dt
GROUP BY r.reg_dt, r.region
ORDER BY r.reg_dt, r.region;

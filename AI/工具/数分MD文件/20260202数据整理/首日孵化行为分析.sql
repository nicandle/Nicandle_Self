-- 目标：统计29/30日注册且当天有过孵化行为的新玩家，其当天的人均孵化次数
-- 数据库：nvwa_cbt1
-- 引擎：Spark SQL
-- 逻辑：
-- 1. 筛选 20260129 和 20260130 注册的用户 (BR/ID 地区)。
-- 2. 关联 PetCreateCustom 表，只匹配注册当天的孵化记录。
-- 3. 统计有过孵化行为的用户数和总次数，计算人均值。

SELECT
    r.dt as reg_date,
    r.ip_region as region,
    count(distinct r.account_id) as hatch_user_count,
    sum(h.hatch_count) as total_hatch_count,
    round(sum(h.hatch_count) / count(distinct r.account_id), 2) as avg_hatch_count
FROM nvwa_cbt1.accountregister r
JOIN (
    SELECT
        account_id,
        substring(cast(local_dt_srv as string), 1, 8) as hatch_dt,
        count(*) as hatch_count
    FROM nvwa_cbt1.PetCreateCustom
    WHERE local_dt_srv >= '20260129'
    GROUP BY account_id, substring(cast(local_dt_srv as string), 1, 8)
) h ON r.account_id = h.account_id AND r.dt = h.hatch_dt
WHERE r.dt BETWEEN '20260129' AND '20260130'
  AND r.ip_region IN ('BR', 'ID')
GROUP BY r.dt, r.ip_region
ORDER BY r.dt, r.ip_region;

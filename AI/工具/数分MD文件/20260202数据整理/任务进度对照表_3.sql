-- 目标：任务进度对照表_3——按「完成该任务」维度，统计完成过该任务的玩家数及完成时的平均孵化次数
-- 数据库：nvwa_cbt1
-- 引擎：Spark SQL（无 WITH 语法，使用子查询）
-- 筛选条件：注册日期 20260129~20260130，IP 区域为 BR 或 ID；完成时刻之前的 PetClaim 条数计为完成时孵化次数

SELECT
    t.task_id as `任务ID`,
    case when agg.`完成该任务的玩家数` is not null then agg.`完成该任务的玩家数` else 0 end as `完成该任务的玩家数`,
    round(case when agg.`玩家完成该任务时的平均孵化次数` is not null then agg.`玩家完成该任务时的平均孵化次数` else 0 end, 2) as `玩家完成该任务时的平均孵化次数`
FROM (
    SELECT 1010201 as task_id, 1 as sort_idx
    UNION ALL SELECT 10102013, 2
    UNION ALL SELECT 1010601, 3
    UNION ALL SELECT 1011001, 4
    UNION ALL SELECT 1011301, 5
    UNION ALL SELECT 1011801, 6
    UNION ALL SELECT 1012301, 7
    UNION ALL SELECT 1012701, 8
) t
LEFT JOIN (
    SELECT
        task_id,
        count(distinct account_id) as `完成该任务的玩家数`,
        case when count(distinct account_id) = 0 then null else sum(hatch_num) * 1.0 / count(distinct account_id) end as `玩家完成该任务时的平均孵化次数`
    FROM (
        SELECT
            t1.account_id,
            t1.task_id,
            t1.ts,
            count(t2.account_id) as hatch_num
        FROM (
            SELECT
                td.account_id,
                td.task_id,
                td.ts
            FROM nvwa_cbt1.taskaction td
            INNER JOIN (
                SELECT account_id
                FROM nvwa_cbt1.accountregister
                WHERE dt BETWEEN '20260129' AND '20260130' AND ip_region IN ('BR', 'ID')
            ) p ON td.account_id = p.account_id
            WHERE td.local_dt_srv >= '20260129'
                AND td.task_action = 2
                AND td.task_id IN (1010201, 10102013, 1010601, 1011001, 1011301, 1011801, 1012301, 1012701)
        ) t1
        LEFT JOIN (
            SELECT account_id, ts as claim_ts
            FROM nvwa_cbt1.PetClaim
            WHERE local_dt_srv >= '20260129'
        ) t2 ON t1.account_id = t2.account_id AND t2.claim_ts <= t1.ts
        GROUP BY t1.account_id, t1.task_id, t1.ts
    ) per_completion
    GROUP BY task_id
) agg ON t.task_id = agg.task_id
ORDER BY t.sort_idx ASC;

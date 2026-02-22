-- 目标：任务进度对照表_5——按「完成该任务」维度，统计每任务完成玩家数及完成该任务时的平均宠物等级
-- 数据库：nvwa_cbt1
-- 引擎：Spark SQL（无 WITH 语法，使用子查询）
-- 筛选条件：注册日期 20260129~20260130，IP 区域为 BR 或 ID；任务顺序见 TaskMainPet.csv
-- 宠物等级：严格按任务完成时间戳截断，只计该时间戳之前（含）的 petlevelup 中，各 pet_id 的 pet_level 最大值，再取该玩家所有宠物的最大等级

SELECT
    t.task_id as `任务ID`,
    case when agg.`完成该任务的玩家数` is not null then agg.`完成该任务的玩家数` else 0 end as `完成该任务的玩家数`,
    round(case when agg.`玩家完成该任务时的平均宠物等级` is not null then agg.`玩家完成该任务时的平均宠物等级` else 0 end, 2) as `玩家完成该任务时的平均宠物等级`
FROM (
    SELECT 1010403 as task_id, 1 as sort_idx UNION ALL
    SELECT 10104042, 2 UNION ALL SELECT 1010605, 3 UNION ALL SELECT 10107031, 4 UNION ALL SELECT 10109021, 5 UNION ALL SELECT 1011004, 6 UNION ALL SELECT 1011305, 7 UNION ALL SELECT 1011503, 8 UNION ALL
    SELECT 1011902, 9 UNION ALL SELECT 1012004, 10 UNION ALL SELECT 1012402, 11 UNION ALL SELECT 1012504, 12 UNION ALL SELECT 1012802, 13 UNION ALL SELECT 1012904, 14
) t
LEFT JOIN (
    SELECT
        task_id,
        count(distinct account_id) as `完成该任务的玩家数`,
        avg(pet_level_at_completion) as `玩家完成该任务时的平均宠物等级`
    FROM (
        SELECT account_id, task_id, max(per_pet_max) as pet_level_at_completion
        FROM (
            SELECT
                c.account_id,
                c.task_id,
                c.completion_ts,
                h.pet_id,
                max(h.pet_level) as per_pet_max
            FROM (
                SELECT tc.account_id, tc.task_id, tc.completion_ts
                FROM (
                    SELECT account_id, task_id, min(local_dt_srv) as completion_ts
                    FROM nvwa_cbt1.taskaction
                    WHERE local_dt_srv >= '20260129' AND task_action = 2
                    GROUP BY account_id, task_id
                ) tc
                INNER JOIN (
                    SELECT account_id
                    FROM nvwa_cbt1.accountregister
                    WHERE dt BETWEEN '20260129' AND '20260130' AND ip_region IN ('BR', 'ID')
                ) p ON tc.account_id = p.account_id
            ) c
            LEFT JOIN (
                SELECT account_id, pet_id, local_dt_srv, pet_level
                FROM nvwa_cbt1.petlevelup
                WHERE local_dt_srv >= '20260129'
            ) h ON c.account_id = h.account_id AND h.local_dt_srv <= c.completion_ts
            GROUP BY c.account_id, c.task_id, c.completion_ts, h.pet_id
        ) per_pet
        GROUP BY account_id, task_id, completion_ts
    ) detail
    GROUP BY task_id
) agg ON t.task_id = agg.task_id
ORDER BY t.sort_idx ASC;

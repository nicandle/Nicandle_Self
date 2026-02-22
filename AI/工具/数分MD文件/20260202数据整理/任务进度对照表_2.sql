-- 目标：任务进度对照表_2——按「最后完成任务」维度，统计每任务作为最后完成的玩家数及分日平均孵化次数
-- 数据库：nvwa_cbt1 (原始日志), nvwa_cooked_cbt1 (留存底表)
-- 引擎：Spark SQL（无 WITH 语法，使用子查询）
-- 筛选条件：注册日期 20260129~20260130，IP 区域为 BR 或 ID；首日=注册当日，次日=注册次日

SELECT
    t.task_id as `任务ID`,
    case when agg.`最后完成该任务的玩家数` is not null then agg.`最后完成该任务的玩家数` else 0 end as `最后完成该任务的玩家数`,
    case when agg.`次留人数` is not null then agg.`次留人数` else 0 end as `次留人数`,
    round(case when agg.`次留率` is not null then agg.`次留率` else 0 end, 4) as `次留率`,
    round(case when agg.`首日平均孵化次数` is not null then agg.`首日平均孵化次数` else 0 end, 2) as `首日平均孵化次数`,
    round(case when agg.`留存玩家平均孵化数` is not null then agg.`留存玩家平均孵化数` else 0 end, 2) as `留存玩家平均孵化数`
FROM (
    SELECT 1010101 as task_id, 1 as sort_idx UNION ALL SELECT 1010102, 2 UNION ALL SELECT 1010201, 3 UNION ALL SELECT 10102011, 4 UNION ALL SELECT 10102012, 5 UNION ALL SELECT 10102013, 6 UNION ALL SELECT 1010202, 7 UNION ALL SELECT 1010301, 8 UNION ALL SELECT 1010302, 9 UNION ALL SELECT 1010303, 10 UNION ALL
    SELECT 1010402, 11 UNION ALL SELECT 1010403, 12 UNION ALL SELECT 10104031, 13 UNION ALL SELECT 1010404, 14 UNION ALL SELECT 10104041, 15 UNION ALL SELECT 10104042, 16 UNION ALL SELECT 10104043, 17 UNION ALL SELECT 1010501, 18 UNION ALL SELECT 1010502, 19 UNION ALL SELECT 1010503, 20 UNION ALL SELECT 1010504, 21 UNION ALL
    SELECT 1010601, 22 UNION ALL SELECT 1010602, 23 UNION ALL SELECT 1010603, 24 UNION ALL SELECT 1010604, 25 UNION ALL SELECT 1010605, 26 UNION ALL SELECT 1010701, 27 UNION ALL SELECT 1010702, 28 UNION ALL SELECT 1010703, 29 UNION ALL SELECT 10107031, 30 UNION ALL SELECT 10107032, 31 UNION ALL
    SELECT 1010801, 32 UNION ALL SELECT 1010802, 33 UNION ALL SELECT 1010803, 34 UNION ALL SELECT 1010901, 35 UNION ALL SELECT 1010902, 36 UNION ALL SELECT 10109021, 37 UNION ALL SELECT 10109022, 38 UNION ALL SELECT 1010903, 39 UNION ALL SELECT 1010904, 40 UNION ALL SELECT 1010905, 41 UNION ALL
    SELECT 1011001, 42 UNION ALL SELECT 1011002, 43 UNION ALL SELECT 1011003, 44 UNION ALL SELECT 1011004, 45 UNION ALL SELECT 1011101, 46 UNION ALL SELECT 10111011, 47 UNION ALL SELECT 1011102, 48 UNION ALL SELECT 1011103, 49 UNION ALL SELECT 1011104, 50 UNION ALL SELECT 1011105, 51 UNION ALL
    SELECT 1011201, 52 UNION ALL SELECT 1011202, 53 UNION ALL SELECT 1011203, 54 UNION ALL SELECT 1011301, 55 UNION ALL SELECT 1011302, 56 UNION ALL SELECT 1011303, 57 UNION ALL SELECT 1011304, 58 UNION ALL SELECT 1011305, 59 UNION ALL SELECT 10113051, 60 UNION ALL SELECT 1011306, 61 UNION ALL
    SELECT 1011401, 62 UNION ALL SELECT 1011402, 63 UNION ALL SELECT 1011403, 64 UNION ALL SELECT 1011404, 65 UNION ALL SELECT 1011405, 66 UNION ALL SELECT 1011501, 67 UNION ALL SELECT 1011502, 68 UNION ALL SELECT 1011503, 69 UNION ALL SELECT 10115031, 70 UNION ALL
    SELECT 1011601, 71 UNION ALL SELECT 1011602, 72 UNION ALL SELECT 1011603, 73 UNION ALL SELECT 1011604, 74 UNION ALL SELECT 1011605, 75 UNION ALL SELECT 1011606, 76 UNION ALL SELECT 1011701, 77 UNION ALL SELECT 10117011, 78 UNION ALL SELECT 1011702, 79 UNION ALL SELECT 1011703, 80 UNION ALL SELECT 1011704, 81 UNION ALL SELECT 1011705, 82 UNION ALL
    SELECT 1011801, 83 UNION ALL SELECT 1011802, 84 UNION ALL SELECT 1011803, 85 UNION ALL SELECT 1011804, 86 UNION ALL SELECT 1011805, 87 UNION ALL SELECT 1011901, 88 UNION ALL SELECT 1011902, 89 UNION ALL SELECT 10119021, 90 UNION ALL SELECT 1011903, 91 UNION ALL SELECT 1011904, 92 UNION ALL SELECT 1011905, 93 UNION ALL SELECT 1011906, 94 UNION ALL
    SELECT 1012001, 95 UNION ALL SELECT 1012002, 96 UNION ALL SELECT 1012003, 97 UNION ALL SELECT 1012004, 98 UNION ALL SELECT 10120041, 99 UNION ALL
    SELECT 1012101, 100 UNION ALL SELECT 1012102, 101 UNION ALL SELECT 1012103, 102 UNION ALL SELECT 1012104, 103 UNION ALL SELECT 1012105, 104 UNION ALL SELECT 1012201, 105 UNION ALL SELECT 1012202, 106 UNION ALL
    SELECT 1012301, 107 UNION ALL SELECT 1012302, 108 UNION ALL SELECT 1012303, 109 UNION ALL SELECT 1012304, 110 UNION ALL SELECT 1012305, 111 UNION ALL SELECT 1012401, 112 UNION ALL SELECT 1012402, 113 UNION ALL SELECT 10124021, 114 UNION ALL SELECT 1012403, 115 UNION ALL SELECT 1012404, 116 UNION ALL SELECT 1012405, 117 UNION ALL
    SELECT 1012501, 118 UNION ALL SELECT 1012502, 119 UNION ALL SELECT 1012503, 120 UNION ALL SELECT 10125031, 121 UNION ALL SELECT 1012504, 122 UNION ALL SELECT 1012601, 123 UNION ALL SELECT 1012602, 124 UNION ALL SELECT 1012603, 125 UNION ALL SELECT 1012604, 126 UNION ALL SELECT 1012605, 127 UNION ALL SELECT 1012606, 128 UNION ALL
    SELECT 1012701, 129 UNION ALL SELECT 1012702, 130 UNION ALL SELECT 1012703, 131 UNION ALL SELECT 1012704, 132 UNION ALL SELECT 1012705, 133 UNION ALL SELECT 1012801, 134 UNION ALL SELECT 1012802, 135 UNION ALL SELECT 1012803, 136 UNION ALL SELECT 1012804, 137 UNION ALL SELECT 1012805, 138 UNION ALL
    SELECT 1012901, 139 UNION ALL SELECT 1012902, 140 UNION ALL SELECT 1012903, 141 UNION ALL SELECT 1012904, 142 UNION ALL SELECT 1013001, 143 UNION ALL SELECT 1013002, 144 UNION ALL SELECT 1013003, 145 UNION ALL SELECT 1013004, 146 UNION ALL
    SELECT 1013101, 147 UNION ALL SELECT 1013102, 148 UNION ALL SELECT 1013103, 149 UNION ALL SELECT 1013104, 150 UNION ALL SELECT 1013105, 151
) t
LEFT JOIN (
    SELECT
        task_id,
        count(distinct account_id) as `最后完成该任务的玩家数`,
        count(distinct case when is_r2 = 1 then account_id end) as `次留人数`,
        count(distinct case when is_r2 = 1 then account_id end) * 1.0 / nullif(count(distinct account_id), 0) as `次留率`,
        avg(hatch_day1) as `首日平均孵化次数`,
        avg(case when is_r2 = 1 then hatch_day1 + hatch_day2 end) as `留存玩家平均孵化数`
    FROM (
        SELECT
            lt.account_id,
            lt.task_id,
            case when cast(ret.is_r2 as string) in ('1', 'true') then 1 else 0 end as is_r2,
            case when h1.hatch_cnt is not null then h1.hatch_cnt else 0 end as hatch_day1,
            case when h2.hatch_cnt is not null then h2.hatch_cnt else 0 end as hatch_day2
        FROM (
            SELECT account_id, task_id, completion_dt
            FROM (
                SELECT
                    account_id,
                    task_id,
                    substring(cast(local_dt_srv as string), 1, 8) as completion_dt,
                    row_number() over (partition by account_id order by local_dt_srv desc) as rn
                FROM nvwa_cbt1.taskaction
                WHERE local_dt_srv >= '20260129' AND task_action = 2
            ) x
            WHERE rn = 1
        ) lt
        INNER JOIN (
            SELECT account_id, dt as register_dt
            FROM nvwa_cbt1.accountregister
            WHERE dt BETWEEN '20260129' AND '20260130' AND ip_region IN ('BR', 'ID')
        ) p ON lt.account_id = p.account_id
        LEFT JOIN (
            SELECT account_id, local_dt, is_r2
            FROM nvwa_cooked_cbt1.dws_user_register_account_retention_d_i
            WHERE local_dt IN ('20260129', '20260130')
        ) ret ON lt.account_id = ret.account_id AND p.register_dt = ret.local_dt
        LEFT JOIN (
            SELECT account_id, substring(cast(local_dt_srv as string), 1, 8) as dt, count(*) as hatch_cnt
            FROM nvwa_cbt1.PetCreateCustom
            WHERE local_dt_srv >= '20260129'
            GROUP BY account_id, substring(cast(local_dt_srv as string), 1, 8)
        ) h1 ON lt.account_id = h1.account_id AND h1.dt = p.register_dt
        LEFT JOIN (
            SELECT account_id, substring(cast(local_dt_srv as string), 1, 8) as dt, count(*) as hatch_cnt
            FROM nvwa_cbt1.PetCreateCustom
            WHERE local_dt_srv >= '20260129'
            GROUP BY account_id, substring(cast(local_dt_srv as string), 1, 8)
        ) h2 ON lt.account_id = h2.account_id AND h2.dt = date_format(date_add(to_date(p.register_dt, 'yyyyMMdd'), 1), 'yyyyMMdd')
    ) detail
    GROUP BY task_id
) agg ON t.task_id = agg.task_id
ORDER BY t.sort_idx ASC;

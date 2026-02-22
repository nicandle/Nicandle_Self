-- 目标：查看特定玩家 ID 的生命源质（Item ID 列表）产销记录
-- 数据库：nvwa_cbt1
-- 日志表：exchangeitems
-- 引擎要求：Spark SQL

SELECT 
    account_id as `账号ID`,
    reason as `原因值(reason)`,
    sub_reason as `子原因值(sub_reason)`,
    local_dt_srv as `日期`,
    -- 展开结构体以查看具体的 item_id 和数量（可选，方便核对）
    item_change
FROM nvwa_cbt1.exchangeitems
-- 针对特定玩家 ID 进行筛选
WHERE account_id IN (10000635, 10000014, 10000077, 10000396, 10000055)
-- 筛选包含生命源质相关 Item ID 的记录
AND (
    array_contains(transform(item_change, x -> x.item_id), 4001001)
    OR array_contains(transform(item_change, x -> x.item_id), 4002001)
    OR array_contains(transform(item_change, x -> x.item_id), 4003001)
    OR array_contains(transform(item_change, x -> x.item_id), 4004001)
    OR array_contains(transform(item_change, x -> x.item_id), 4005001)
)
ORDER BY account_id, local_dt_srv ASC;

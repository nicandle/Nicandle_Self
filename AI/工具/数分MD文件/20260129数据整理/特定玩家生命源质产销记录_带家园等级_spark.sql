-- 目标：查看特定玩家 ID 的生命源质产销记录，并关联其家园等级
-- 逻辑：1. 锁定账号 -> 2. 关联家园等级 (building_type=101) -> 3. 筛选特定物品日志

with target_users as (
    -- 第一步：定义目标账号列表
    SELECT explode(array(10000635, 10000014, 10000077, 10000396, 10000055)) as account_id
),
home_level_info as (
    -- 第二步：提取这些玩家的最高家园等级 (building_type=101)
    SELECT 
        account_id,
        max(building_level) as home_level
    FROM nvwa_cbt1.homebuild
    WHERE account_id IN (10000635, 10000014, 10000077, 10000396, 10000055)
      AND building_type = 101
    GROUP BY account_id
),
target_logs as (
    -- 第三步：获取这些账号的所有 exchangeitems 日志
    SELECT *
    FROM nvwa_cbt1.exchangeitems
    WHERE account_id IN (10000635, 10000014, 10000077, 10000396, 10000055)
)
-- 第四步：关联家园等级并筛选符合物品 ID 标准的记录
SELECT 
    l.account_id as `账号ID`,
    coalesce(h.home_level, 1) as `家园等级`, -- 无日志则默认为初始1级
    l.reason as `原因值(reason)`,
    l.sub_reason as `子原因值(sub_reason)`,
    l.local_dt_srv as `日期`,
    l.item_change
FROM target_logs l
LEFT JOIN home_level_info h ON l.account_id = h.account_id
WHERE (
    array_contains(transform(l.item_change, x -> x.item_id), 4001001)
    OR array_contains(transform(l.item_change, x -> x.item_id), 4002001)
    OR array_contains(transform(l.item_change, x -> x.item_id), 4003001)
    OR array_contains(transform(l.item_change, x -> x.item_id), 4004001)
    OR array_contains(transform(l.item_change, x -> x.item_id), 4005001)
)
ORDER BY l.account_id, l.local_dt_srv ASC;

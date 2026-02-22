with avg_ping_fps as (
        -- 第一步：计算每个用户每天的平均网络指标（延迟和帧率）
        SELECT
            local_dt_srv as local_dt, -- 服务器本地日期
            account_id,               -- 玩家账号ID
            avg(ping) as avg_ping,    -- 计算当日平均延迟(Ping)
            avg(fps) as avg_fps       -- 计算当日平均帧率(FPS)
        FROM nvwa_cbt1.GameHeartbeat  -- 来源：游戏心跳原始日志表
        WHERE local_dt_srv  BETWEEN '20260127' AND '20260129' -- 筛选时间范围
        GROUP BY 1, 2                 -- 按日期和账号分组
    ),
    avg_ping_tag as (
        -- 第二步：将平均延迟数值转化为区间标签，方便后续按网络质量分类统计
        SELECT
            local_dt,
            account_id,
            case when avg_ping >= 0 and avg_ping < 50 then '[0-50)'
             when avg_ping >= 50 and avg_ping < 100 then '[50-100)'
             when avg_ping >= 100 and avg_ping < 150 then '[100-150)'
             when avg_ping >= 150 and avg_ping < 200 then '[150-200)'
             when avg_ping >= 200 and avg_ping < 250 then '[200-250)'
             when avg_ping >= 250 and avg_ping < 300 then '[250-300)'
             when avg_ping >= 300 and avg_ping < 350 then '[300-350)'
             when avg_ping >= 350 and avg_ping < 400 then '[350-400)'
             when avg_ping >= 400 and avg_ping < 450 then '[400-450)'
             when avg_ping >= 450 and avg_ping < 500 then '[450-500)'
             when avg_ping >= 500 and avg_ping < 550 then '[500-550)'
             when avg_ping >= 550 and avg_ping < 600 then '[550-600)'
             when avg_ping >= 600  then '[600,+∞)'
             end as avg_ping_tag      -- 延迟区间标签
        FROM avg_ping_fps
    ),
    retention_day as (
        -- 第三步：提取用户基础留存数据（预计算好的留存标志位）
        SELECT 
            local_dt
            ,region                   -- 游戏大区
            ,ip_region                -- IP所属地理位置
            ,account_id
            ,is_r2                    -- 次日留存标志（1为留存，0为未留存）
            ,is_r3                    -- 3日留存标志
            ,is_r4                    -- 4日留存标志
            ,is_r5                    -- 5日留存标志
            ,is_r6                    -- 6日留存标志
            ,is_r7                    -- 7日留存标志
            ,is_r14                   -- 14日留存标志
            ,is_r30                   -- 30日留存标志
        FROM {cooked_db}.dws_user_register_account_retention_d_i -- 来源：用户注册留存日增量表
        WHERE local_dt in (
            '20260129',
            '20260127','20260128'
        ))
            -- 第四步：最终聚合统计，计算不同维度下的留存人数
            SELECT 
            string(to_date(t1.local_dt, 'yyyyMMdd')) as local_dt -- 格式化日期
            ,coalesce(t1.region,'Unknown') as region             -- 填充大区空值
            ,coalesce(t1.ip_region,'Unknown') as ip_region       -- 填充IP地区空值
            ,coalesce(t2.avg_ping_tag,'Unknown') as avg_ping_tag -- 填充延迟标签空值（无心跳数据的用户）
            ,count(distinct t1.account_id) as new_user           -- 统计当日新增用户总数
            -- 使用条件计数法统计各阶段留存人数
            ,count(distinct case when t1.is_r2 = 1 then t1.account_id end) as r2   -- 次日留存数
            ,count(distinct case when t1.is_r3 = 1 then t1.account_id end) as r3   -- 3日留存数
            ,count(distinct case when t1.is_r4 = 1 then t1.account_id end) as r4   -- 4日留存数
            ,count(distinct case when t1.is_r5 = 1 then t1.account_id end) as r5   -- 5日留存数
            ,count(distinct case when t1.is_r6 = 1 then t1.account_id end) as r6   -- 6日留存数
            ,count(distinct case when t1.is_r7 = 1 then t1.account_id end) as r7   -- 7日留存数
            ,count(distinct case when t1.is_r14 = 1 then t1.account_id end) as r14 -- 14日留存数
            ,count(distinct case when t1.is_r30 = 1 then t1.account_id end) as r30 -- 30日留存数
        FROM retention_day t1 LEFT JOIN avg_ping_tag t2 ON t1.account_id = t2.account_id 
        and t1.local_dt = t2.local_dt
        GROUP BY 1, 2, 3, 4
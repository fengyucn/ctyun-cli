#!/usr/bin/env python3
"""列出所有监控API"""

# 从源码中提取方法名和文档
methods = [
    ("query_custom_item_trendmetricdata", "查询自定义监控项的时序指标趋势监控数据"),
    ("query_dcaas_traffic", "查询云专线流量监控数据"),
    ("list_dcaas_devices", "查询云专线设备列表"),
    ("query_cpu_top", "查询CPU使用率最高的云主机Top-N"),
    ("query_mem_top", "查询内存使用率最高的云主机Top-N"),
    ("query_disk_top", "查询磁盘使用率最高的云主机Top-N"),
    ("query_monitor_items", "查询监控项列表"),
    ("query_sys_services", "查询系统服务列表"),
    ("describe_monitor_board", "查询监控面板详情"),
    ("list_monitor_boards", "查询监控面板列表"),
    ("describe_monitor_view", "查询监控视图详情"),
    ("query_view_data", "查询监控视图数据"),
    ("query_resource_groups", "查询资源分组列表"),
    ("describe_resource_group", "查询资源分组详情"),
    ("query_latest_metric_data", "查询最新监控数据"),
    ("query_history_metric_data", "查询历史监控数据"),
    ("query_event_services", "查询事件服务列表"),
    ("count_event_data", "统计事件数据"),
    ("query_event_list", "查询事件列表"),
    ("query_event_detail", "查询事件详情"),
    ("query_events", "查询指定服务的事件"),
    ("query_custom_events", "查询自定义事件列表"),
    ("query_custom_event_data", "查询自定义事件数据"),
    ("describe_custom_event_alarm_rule", "查看自定义事件告警规则详情"),
    ("query_alert_history", "查询告警历史"),
    ("query_alert_history_info", "查询告警历史详情"),
    ("query_alarm_top_dimension", "查询告警Top维度"),
    ("query_alarm_top_resource", "查询告警Top资源"),
    ("query_alarm_top_metric", "查询告警Top指标"),
    ("query_alarm_top_event", "查询告警Top事件"),
    ("query_alarm_rules", "查询告警规则列表"),
    ("describe_alarm_rule", "查询告警规则详情"),
    ("query_contacts", "查询联系人列表"),
    ("query_contact_groups", "查询联系人组列表"),
    ("query_custom_item_historymetricdata", "查询自定义监控项历史数据"),
    ("query_custom_item_dimension_values", "查询自定义监控项维度值"),
    ("query_custom_items", "查询自定义监控项列表"),
    ("query_custom_alarm_rules", "查询自定义监控告警规则列表"),
    ("describe_custom_alarm_rule", "查询自定义监控告警规则详情"),
    ("query_notice_templates", "查询通知模板列表"),
    ("describe_notice_template", "查询通知模板详情"),
    ("query_notice_template_variable", "查询通知模板变量"),
    ("describe_alarm_template", "查询告警模板详情"),
    ("query_alarm_templates", "查询告警模板列表"),
    ("describe_contact", "查询联系人详情"),
    ("describe_contact_group", "查询联系人组详情"),
    ("query_alarm_blacklists", "查询告警黑名单"),
    ("query_message_records", "查询消息通知记录"),
    ("query_inspection_task_overview", "查询巡检任务结果总览"),
    ("query_inspection_task_detail", "查询巡检任务结果详情"),
    ("query_inspection_items", "查询巡检项列表"),
    ("query_inspection_history_list", "查询巡检历史列表"),
    ("query_inspection_history_detail", "查询巡检历史详情"),
]

# 分类
categories = {
    '1. 云专线监控': [],
    '2. Top-N查询': [],
    '3. 监控项与服务': [],
    '4. 监控面板与视图': [],
    '5. 资源分组': [],
    '6. 指标数据查询': [],
    '7. 事件管理': [],
    '8. 告警历史': [],
    '9. 告警Top统计': [],
    '10. 告警规则': [],
    '11. 联系人管理': [],
    '12. 自定义监控': [],
    '13. 通知模板': [],
    '14. 告警模板': [],
    '15. 告警黑名单': [],
    '16. 消息记录': [],
    '17. 巡检功能': [],
}

for method_name, doc in methods:
    # 分类
    if 'dcaas' in method_name:
        categories['1. 云专线监控'].append((method_name, doc))
    elif 'top' in method_name and ('cpu' in method_name or 'mem' in method_name or 'disk' in method_name):
        categories['2. Top-N查询'].append((method_name, doc))
    elif 'monitor_items' in method_name or 'sys_service' in method_name:
        categories['3. 监控项与服务'].append((method_name, doc))
    elif 'board' in method_name or 'view' in method_name:
        categories['4. 监控面板与视图'].append((method_name, doc))
    elif 'resource_group' in method_name:
        categories['5. 资源分组'].append((method_name, doc))
    elif 'metric_data' in method_name and 'custom' not in method_name:
        categories['6. 指标数据查询'].append((method_name, doc))
    elif 'event' in method_name and 'alarm' not in method_name:
        categories['7. 事件管理'].append((method_name, doc))
    elif 'alert_history' in method_name:
        categories['8. 告警历史'].append((method_name, doc))
    elif 'alarm_top' in method_name:
        categories['9. 告警Top统计'].append((method_name, doc))
    elif 'alarm_rule' in method_name and 'custom' not in method_name:
        categories['10. 告警规则'].append((method_name, doc))
    elif 'contact' in method_name:
        categories['11. 联系人管理'].append((method_name, doc))
    elif 'custom' in method_name:
        categories['12. 自定义监控'].append((method_name, doc))
    elif 'notice_template' in method_name or 'template_variable' in method_name:
        categories['13. 通知模板'].append((method_name, doc))
    elif 'alarm_template' in method_name:
        categories['14. 告警模板'].append((method_name, doc))
    elif 'blacklist' in method_name:
        categories['15. 告警黑名单'].append((method_name, doc))
    elif 'message_record' in method_name:
        categories['16. 消息记录'].append((method_name, doc))
    elif 'inspection' in method_name:
        categories['17. 巡检功能'].append((method_name, doc))

print('=' * 100)
print('天翼云监控服务 - 所有监控API列表'.center(96))
print('=' * 100)
print()

total = 0
for category, methods_list in categories.items():
    if methods_list:
        print(f'{category}（{len(methods_list)}个API）')
        print('-' * 100)
        for i, (name, doc) in enumerate(methods_list, 1):
            print(f'  {i}. {name:<45} - {doc}')
            total += 1
        print()

print('=' * 100)
print(f'总计: {total} 个监控API'.center(96))
print('=' * 100)

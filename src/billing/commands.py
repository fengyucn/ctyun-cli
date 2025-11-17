"""
账务中心命令行接口
"""

import click
from functools import wraps
from typing import Optional
from src.client import CTYUNAPIError
from src.utils.helpers import OutputFormatter, ValidationUtils, logger
from src.billing.client import BillingClient


def handle_error(func):
    """错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CTYUNAPIError as e:
            click.echo(f"API错误 [{e.code}]: {e.message}", err=True)
            if e.request_id:
                click.echo(f"请求ID: {e.request_id}", err=True)
            import sys
            sys.exit(1)
        except Exception as e:
            click.echo(f"错误: {e}", err=True)
            import sys
            sys.exit(1)
    return wrapper


def format_output(data, output_format='table'):
    """格式化输出"""
    if output_format == 'json':
        click.echo(OutputFormatter.format_json(data))
    elif output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
        except ImportError:
            click.echo("错误: 需要安装PyYAML库", err=True)
            import sys
            sys.exit(1)
    else:
        if isinstance(data, list) and data:
            headers = list(data[0].keys()) if isinstance(data[0], dict) else []
            table = OutputFormatter.format_table(data, headers)
            click.echo(table)
        elif isinstance(data, dict):
            headers = ['字段', '值']
            table_data = []
            for key, value in data.items():
                table_data.append([key, value])
            table = OutputFormatter.format_table(table_data, headers)
            click.echo(table)
        else:
            click.echo(data)


@click.group()
def billing():
    """账务中心管理"""
    pass


@billing.command()
@click.pass_context
@handle_error
def balance(ctx):
    """查询账户余额"""
    client = ctx.obj['client']
    billing_client = BillingClient(client)
    
    result = billing_client.query_account_balance()
    
    if result.get('returnCode') == '000000':
        data = {
            '账户总余额': result.get('balance', '0.00'),
            '现金余额': result.get('cashBalance', '0.00'),
            '信用余额': result.get('creditBalance', '0.00')
        }
        format_output(data, ctx.obj.get('output_format', 'table'))
    else:
        click.echo(f"查询失败: {result.get('returnMessage', '未知错误')}", err=True)


@billing.command()
@click.argument('bill_cycle')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--bill-type', help='账单类型')
@click.option('--product-code', help='产品编码')
@click.option('--contract-id', help='合同ID')
@click.pass_context
@handle_error
def cycle_product(ctx, bill_cycle, page, page_size, bill_type, product_code, contract_id):
    """
    查询包周期账单明细（按产品汇总）
    
    BILL_CYCLE: 账期，格式：YYYYMM，如：202508
    """
    if not ValidationUtils.validate_bill_cycle(bill_cycle):
        click.echo("错误: 账期格式不正确，应为YYYYMM格式，如：202508", err=True)
        import sys
        sys.exit(1)
    
    client = ctx.obj['client']
    billing_client = BillingClient(client)
    
    result = billing_client.query_cycle_bill_by_product(
        bill_cycle=bill_cycle,
        page_no=page,
        page_size=page_size,
        bill_type=bill_type,
        product_code=product_code,
        contract_id=contract_id
    )
    
    if result.get('statusCode') == '800':
        return_obj = result.get('returnObj', {})
        bill_list = return_obj.get('result', [])
        
        if bill_list:
            total_count = return_obj.get('totalCount', 0)
            click.echo(f"\n账期 {bill_cycle} 包周期账单（按产品汇总，共 {total_count} 条）：")
            
            # 简化显示关键字段
            simplified_list = []
            for item in bill_list:
                # 计费模式映射
                bill_mode_map = {'1': '包周期', '2': '按需'}
                # 账单类型映射
                bill_type_map = {
                    '1': '新购', '2': '续订', '3': '变更',
                    '4': '退订', '5': '退款降级', '6': '其他', '7': '使用'
                }
                # 支付方式映射
                pay_method_map = {'1': '预付费', '2': '后付费'}
                
                simplified_list.append({
                    '产品名称': item.get('productName', ''),
                    '资源类型': item.get('resourceType', ''),
                    '计费模式': bill_mode_map.get(item.get('billMode', ''), item.get('billMode', '')),
                    '账单类型': bill_type_map.get(item.get('billType', ''), item.get('billType', '')),
                    '支付方式': pay_method_map.get(item.get('payMethod', ''), item.get('payMethod', '')),
                    '消费时间': item.get('consumeDate', ''),
                    '官网价': item.get('price', '0'),
                    '优惠金额': item.get('discountAmount', '0'),
                    '应付金额': item.get('payableAmount', '0'),
                    '实付金额': item.get('amount', '0')
                })
            
            format_output(simplified_list, ctx.obj.get('output_format', 'table'))
        else:
            click.echo(f"账期 {bill_cycle} 没有包周期账单记录")
    else:
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)


@billing.command()
@click.argument('bill_cycle')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--contract-id', help='合同号')
@click.option('--project-id', help='项目ID')
@click.option('--product-code', help='产品编码')
@click.option('--bill-type', help='账单类型')
@click.option('--pay-method', help='支付方式')
@click.option('--order-id', help='主订单号')
@click.pass_context
@handle_error
def ondemand_flow(ctx, bill_cycle, page, page_size, contract_id, project_id,
                  product_code, bill_type, pay_method, order_id):
    """
    查询按需流水账单
    
    BILL_CYCLE: 账期，格式：YYYYMM，如：202508
    """
    if not ValidationUtils.validate_bill_cycle(bill_cycle):
        click.echo("错误: 账期格式不正确，应为YYYYMM格式，如：202508", err=True)
        import sys
        sys.exit(1)
    
    client = ctx.obj['client']
    billing_client = BillingClient(client)
    
    result = billing_client.query_ondemand_bill_flow(
        bill_cycle=bill_cycle,
        page_no=page,
        page_size=page_size,
        contract_id=contract_id,
        project_id=project_id,
        product_code=product_code,
        bill_type=bill_type,
        pay_method=pay_method,
        master_order_id=order_id
    )
    
    if result.get('statusCode') == '800':
        return_obj = result.get('returnObj', {})
        bill_list = return_obj.get('result', [])
        
        if bill_list:
            total_count = return_obj.get('totalCount', 0)
            click.echo(f"\n账期 {bill_cycle} 按需流水账单（共 {total_count} 条）：")
            
            # 简化显示关键字段
            simplified_list = []
            for item in bill_list:
                # 计费模式映射
                bill_mode_map = {'1': '包周期', '2': '按需'}
                # 账单类型映射
                bill_type_map = {
                    '1': '新购', '2': '续订', '3': '变更',
                    '4': '退订', '5': '退款降级', '6': '其他', '7': '使用'
                }
                
                simplified_list.append({
                    '资源ID': item.get('resourceId', '')[:20],
                    '产品名称': item.get('productName', ''),
                    '订单号': item.get('orderNo', '-'),
                    '计费模式': bill_mode_map.get(item.get('billMode', ''), item.get('billMode', '')),
                    '账单类型': bill_type_map.get(item.get('billType', ''), item.get('billType', '')),
                    '消费时间': item.get('consumeDate', ''),
                    '官网价': item.get('price', '0'),
                    '应付金额': item.get('payableAmount', '0'),
                    '实付金额': item.get('amount', '0'),
                    '支付状态': item.get('payStatus', '-')
                })
            
            format_output(simplified_list, ctx.obj.get('output_format', 'table'))
        else:
            click.echo(f"账期 {bill_cycle} 没有按需流水账单记录")
    else:
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)


@billing.command()
@click.argument('bill_cycle')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--resource-id', help='资源ID')
@click.option('--product-code', help='产品编码')
@click.option('--contract-id', help='合同ID')
@click.pass_context
@handle_error
def cycle_bill(ctx, bill_cycle, page, page_size, resource_id, product_code, contract_id):
    """
    查询包周期订单账单详情
    
    BILL_CYCLE: 账期，格式：YYYYMM，如：202311
    """
    if not ValidationUtils.validate_bill_cycle(bill_cycle):
        click.echo("错误: 账期格式不正确，应为YYYYMM格式，如：202311", err=True)
        import sys
        sys.exit(1)
    
    client = ctx.obj['client']
    billing_client = BillingClient(client)
    
    result = billing_client.query_cycle_bill_detail(
        bill_cycle=bill_cycle,
        page_no=page,
        page_size=page_size,
        resource_id=resource_id,
        product_code=product_code,
        contract_id=contract_id
    )
    
    if result.get('statusCode') == '800':
        return_obj = result.get('returnObj', {})
        bill_list = return_obj.get('result', [])
        
        if bill_list:
            total_count = return_obj.get('totalCount', 0)
            click.echo(f"\n账期 {bill_cycle} 包周期账单详情（共 {total_count} 条）：")
            
            # 简化显示关键字段
            simplified_list = []
            for item in bill_list:
                # 计费模式映射
                bill_mode_map = {'1': '包周期', '2': '按需'}
                # 账单类型映射
                bill_type_map = {
                    '1': '新购', '2': '续订', '3': '变更',
                    '4': '退订', '5': '退款降级', '6': '其他', '7': '使用'
                }
                
                simplified_list.append({
                    '资源ID': item.get('resourceId', '')[:20],
                    '产品名称': item.get('productName', ''),
                    '订单号': item.get('masterOrderNo', ''),
                    '计费模式': bill_mode_map.get(item.get('billMode', ''), item.get('billMode', '')),
                    '账单类型': bill_type_map.get(item.get('billType', ''), item.get('billType', '')),
                    '消费时间': item.get('consumeDate', ''),
                    '官网价': item.get('price', '0'),
                    '优惠金额': item.get('discountAmount', '0'),
                    '应付金额': item.get('payableAmount', '0'),
                    '实付金额': item.get('amount', '0')
                })
            
            format_output(simplified_list, ctx.obj.get('output_format', 'table'))
        else:
            click.echo(f"账期 {bill_cycle} 没有包周期账单记录")
    else:
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)


@billing.command()
@click.argument('bill_cycle')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--product-code', help='产品编码')
@click.option('--resource-id', help='资源ID')
@click.pass_context
@handle_error
def bill_list(ctx, bill_cycle, page, page_size, product_code, resource_id):
    """
    查询账单明细（按需）
    
    BILL_CYCLE: 账期，格式：YYYYMM，如：202311
    """
    if not ValidationUtils.validate_bill_cycle(bill_cycle):
        click.echo("错误: 账期格式不正确，应为YYYYMM格式，如：202311", err=True)
        import sys
        sys.exit(1)
    
    client = ctx.obj['client']
    billing_client = BillingClient(client)
    
    result = billing_client.query_bill_list(
        bill_cycle=bill_cycle,
        page_no=page,
        page_size=page_size,
        product_code=product_code,
        resource_id=resource_id
    )
    
    if result.get('statusCode') == '800':
        return_obj = result.get('returnObj', {})
        bill_list = return_obj.get('result', [])
        
        if bill_list:
            total_count = return_obj.get('totalCount', 0)
            click.echo(f"\n账期 {bill_cycle} 账单明细（共 {total_count} 条）：")
            
            # 简化显示关键字段
            simplified_list = []
            for item in bill_list:
                simplified_list.append({
                    '资源ID': item.get('resourceId', '')[:20],
                    '产品名称': item.get('productName', ''),
                    '消费时间': item.get('consumeDate', '').split('_')[0] if item.get('consumeDate') else '',
                    '官网价': item.get('price', '0'),
                    '优惠金额': item.get('discountAmount', '0'),
                    '应付金额': item.get('payableAmount', '0'),
                    '实付金额': item.get('amount', '0'),
                    '资源池': item.get('regionCode', '')
                })
            
            format_output(simplified_list, ctx.obj.get('output_format', 'table'))
        else:
            click.echo(f"账期 {bill_cycle} 没有账单记录")
    else:
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)


@billing.command()
@click.argument('bill_id')
@click.pass_context
@handle_error
def bill_detail(ctx, bill_id):
    """
    查询账单详情
    
    BILL_ID: 账单ID
    """
    client = ctx.obj['client']
    billing_client = BillingClient(client)
    
    result = billing_client.query_bill_detail(bill_id)
    
    if result.get('returnCode') == '000000':
        click.echo(f"\n账单 {bill_id} 详情：")
        format_output(result, ctx.obj.get('output_format', 'table'))
    else:
        click.echo(f"查询失败: {result.get('returnMessage', '未知错误')}", err=True)


@billing.command()
@click.pass_context
@handle_error
def arrears(ctx):
    """查询欠费信息"""
    client = ctx.obj['client']
    billing_client = BillingClient(client)
    
    result = billing_client.query_arrears_info()
    
    if result.get('returnCode') == '000000':
        is_arrears = result.get('isArrears', False)
        arrears_amount = result.get('arrearsAmount', '0.00')
        
        if is_arrears:
            click.echo(f"⚠️  账户存在欠费: {arrears_amount} 元", err=True)
            if ctx.obj.get('output_format') != 'table':
                format_output(result, ctx.obj.get('output_format'))
        else:
            click.echo("✓ 账户无欠费")
    else:
        click.echo(f"查询失败: {result.get('returnMessage', '未知错误')}", err=True)


@billing.command()
@click.argument('bill_cycle')
@click.option('--contract-id', help='合同ID')
@click.pass_context
@handle_error
def bill_summary(ctx, bill_cycle, contract_id):
    """
    查询消费类型汇总
    
    BILL_CYCLE: 账期，格式：YYYYMM，如：202311
    """
    if not ValidationUtils.validate_bill_cycle(bill_cycle):
        click.echo("错误: 账期格式不正确，应为YYYYMM格式，如：202311", err=True)
        import sys
        sys.exit(1)
    
    client = ctx.obj['client']
    billing_client = BillingClient(client)
    
    result = billing_client.query_bill_summary_by_type(
        bill_cycle=bill_cycle,
        contract_id=contract_id
    )
    
    if result.get('statusCode') == '800':
        return_obj = result.get('returnObj', {})
        
        # 显示汇总信息
        click.echo(f"\n账期 {bill_cycle} 消费汇总：")
        click.echo(f"应付总金额: {return_obj.get('totalAmount', '0.00')} 元")
        click.echo(f"现金支付: {return_obj.get('totalCashAmount', '0.00')} 元")
        click.echo(f"代金券抵扣: {return_obj.get('totalCouponAmount', '0.00')} 元")
        
        # 显示分类明细
        result_list = return_obj.get('result', [])
        if result_list:
            click.echo(f"\n消费类型明细：")
            
            simplified_list = []
            for item in result_list:
                simplified_list.append({
                    '消费类型': item.get('billTypeName', ''),
                    '应付金额': item.get('amount', '0.00'),
                    '现金支付': item.get('cashAmount', '0.00'),
                    '代金券抵扣': item.get('couponAmount', '0.00')
                })
            
            format_output(simplified_list, ctx.obj.get('output_format', 'table'))
    else:
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)


@billing.command()
@click.argument('bill_cycle')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--product-code', help='产品编码')
@click.option('--bill-type', help='账单类型')
@click.option('--contract-id', help='合同ID')
@click.option('--group-by-day', help='是否按天查询，1为按天，0或不传为按账期')
@click.pass_context
@handle_error
def ondemand_product(ctx, bill_cycle, page, page_size, product_code, bill_type, contract_id, group_by_day):
    """
    查询按需账单明细（按产品汇总）
    
    BILL_CYCLE: 账期，格式：YYYYMM，如：202212
    """
    if not ValidationUtils.validate_bill_cycle(bill_cycle):
        click.echo("错误: 账期格式不正确，应为YYYYMM格式，如：202212", err=True)
        import sys
        sys.exit(1)
    
    client = ctx.obj['client']
    billing_client = BillingClient(client)
    
    result = billing_client.query_ondemand_bill_by_product(
        bill_cycle=bill_cycle,
        page_no=page,
        page_size=page_size,
        product_code=product_code,
        bill_type=bill_type,
        contract_id=contract_id,
        group_by_day=group_by_day
    )
    
    if result.get('statusCode') == '800':
        return_obj = result.get('returnObj', {})
        bill_list = return_obj.get('result', [])
        
        if bill_list:
            total_count = return_obj.get('totalCount', 0)
            click.echo(f"\n账期 {bill_cycle} 按需账单（按产品汇总，共 {total_count} 条）：")
            
            simplified_list = []
            for item in bill_list:
                bill_mode_map = {'1': '包周期', '2': '按需'}
                bill_type_map = {
                    '1': '新购', '2': '续订', '3': '变更',
                    '4': '退订', '5': '退款降级', '6': '其他', '7': '使用'
                }
                
                simplified_list.append({
                    '产品名称': item.get('productName', ''),
                    '资源类型': item.get('resourceType', ''),
                    '计费模式': bill_mode_map.get(item.get('billMode', ''), item.get('billMode', '')),
                    '账单类型': bill_type_map.get(item.get('billType', ''), item.get('billType', '')),
                    '消费时间': item.get('consumeDate', ''),
                    '官网价': item.get('price', '0'),
                    '优惠金额': item.get('discountAmount', '0'),
                    '应付金额': item.get('payableAmount', '0'),
                    '实付金额': item.get('amount', '0'),
                    '代金券抵扣': item.get('coupon', '0')
                })
            
            format_output(simplified_list, ctx.obj.get('output_format', 'table'))
        else:
            click.echo(f"账期 {bill_cycle} 没有按需账单记录")
    else:
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)


@billing.command()
@click.argument('bill_cycle')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.option('--product-code', help='产品编码')
@click.option('--project-id', help='项目ID')
@click.option('--bill-type', help='账单类型')
@click.option('--contract-id', help='合同ID')
@click.option('--order-id', help='主订单ID')
@click.pass_context
@handle_error
def cycle_flow(ctx, bill_cycle, page, page_size, product_code, project_id,
               bill_type, contract_id, order_id):
    """
    查询包周期流水账单
    
    BILL_CYCLE: 账期，格式：YYYYMM，如：202212
    """
    if not ValidationUtils.validate_bill_cycle(bill_cycle):
        click.echo("错误: 账期格式不正确，应为YYYYMM格式，如：202212", err=True)
        import sys
        sys.exit(1)
    
    client = ctx.obj['client']
    billing_client = BillingClient(client)
    
    result = billing_client.query_cycle_bill_flow(
        bill_cycle=bill_cycle,
        page_no=page,
        page_size=page_size,
        product_code=product_code,
        project_id=project_id,
        bill_type=bill_type,
        contract_id=contract_id,
        master_order_id=order_id
    )
    
    if result.get('statusCode') == '800':
        return_obj = result.get('returnObj', {})
        bill_list = return_obj.get('result', [])
        
        if bill_list:
            total_count = return_obj.get('totalCount', 0)
            click.echo(f"\n账期 {bill_cycle} 包周期流水账单（共 {total_count} 条）：")
            
            simplified_list = []
            for item in bill_list:
                bill_mode_map = {'1': '包周期', '2': '按需'}
                bill_type_map = {
                    '1': '新购', '2': '续订', '3': '变更',
                    '4': '退订', '5': '退款降级', '6': '其他', '7': '使用'
                }
                pay_method_map = {'1': '预付费', '2': '后付费'}
                pay_status_map = {'1': '已支付', '2': '未支付'}
                
                simplified_list.append({
                    '订单号': item.get('orderNo', ''),
                    '产品名称': item.get('productName', ''),
                    '计费模式': bill_mode_map.get(item.get('billMode', ''), item.get('billMode', '')),
                    '账单类型': bill_type_map.get(item.get('billType', ''), item.get('billType', '')),
                    '支付方式': pay_method_map.get(item.get('payMethod', ''), item.get('payMethod', '')),
                    '消费时间': item.get('consumeDate', ''),
                    '官网价': item.get('price', '0'),
                    '应付金额': item.get('payableAmount', '0'),
                    '实付金额': item.get('amount', '0'),
                    '支付状态': pay_status_map.get(item.get('payStatus', ''), item.get('payStatus', ''))
                })
            
            format_output(simplified_list, ctx.obj.get('output_format', 'table'))
        else:
            click.echo(f"账期 {bill_cycle} 没有包周期流水账单记录")
    else:
        click.echo(f"查询失败: {result.get('message', '未知错误')}", err=True)


@billing.command()
@click.argument('bill_cycle')
@click.option('--account-id', '-a', multiple=True, required=True, help='账户ID（可多次指定）')
@click.pass_context
@handle_error
def account_bill(ctx, bill_cycle, account_id):
    """
    查询账户账单
    
    BILL_CYCLE: 账期，格式：YYYYMM，如：202206
    """
    if not ValidationUtils.validate_bill_cycle(bill_cycle):
        click.echo("错误: 账期格式不正确，应为YYYYMM格式，如：202206", err=True)
        import sys
        sys.exit(1)
    
    if not account_id:
        click.echo("错误: 至少需要指定一个账户ID", err=True)
        import sys
        sys.exit(1)
    
    client = ctx.obj['client']
    billing_client = BillingClient(client)
    
    result = billing_client.query_account_bill_by_account_id(
        bill_cycle=bill_cycle,
        account_ids=list(account_id)
    )
    
    if result.get('statusCode') == 800:
        bill_objs = result.get('billObj', [])
        
        if bill_objs:
            click.echo(f"\n账期 {bill_cycle} 账户账单（共 {len(bill_objs)} 个账户）：")
            
            simplified_list = []
            for item in bill_objs:
                simplified_list.append({
                    '账户ID': item.get('accountId', ''),
                    '总花费': item.get('allCost', '0.00'),
                    '总费用': item.get('billingCharge', '0.00'),
                    '退订费用': item.get('unsubscribeCharge', '0.00')
                })
            
            format_output(simplified_list, ctx.obj.get('output_format', 'table'))
        else:
            click.echo(f"账期 {bill_cycle} 没有找到账户账单记录")
    else:
        click.echo(f"查询失败: {result.get('msg', '未知错误')}", err=True)


@billing.command()
@click.option('--start-date', required=True, help='开始日期，格式：YYYY-MM-DD')
@click.option('--end-date', required=True, help='结束日期，格式：YYYY-MM-DD')
@click.option('--product-type', help='产品类型（可选）')
@click.option('--page', default=1, type=int, help='页码')
@click.option('--page-size', default=10, type=int, help='每页数量')
@click.pass_context
@handle_error
def consumption(ctx, start_date, end_date, product_type, page, page_size):
    """查询消费明细"""
    if not ValidationUtils.validate_date_format(start_date):
        click.echo("错误: 开始日期格式不正确，应为YYYY-MM-DD格式", err=True)
        import sys
        sys.exit(1)
    
    if not ValidationUtils.validate_date_format(end_date):
        click.echo("错误: 结束日期格式不正确，应为YYYY-MM-DD格式", err=True)
        import sys
        sys.exit(1)
    
    client = ctx.obj['client']
    billing_client = BillingClient(client)
    
    result = billing_client.query_consumption_details(
        start_date=start_date,
        end_date=end_date,
        page_no=page,
        page_size=page_size,
        product_type=product_type
    )
    
    if result.get('returnCode') == '000000':
        consumption_list = result.get('consumptionList', [])
        if consumption_list:
            click.echo(f"\n消费明细（{start_date} 至 {end_date}，共 {result.get('totalCount', 0)} 条）：")
            format_output(consumption_list, ctx.obj.get('output_format', 'table'))
        else:
            click.echo(f"时间段 {start_date} 至 {end_date} 没有消费记录")
    else:
        click.echo(f"查询失败: {result.get('returnMessage', '未知错误')}", err=True)

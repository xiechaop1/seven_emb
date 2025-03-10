import itertools
import time

# from gevent import time

global ct

def is_valid_expression(expr):
    """ 检查表达式是否合法 """
    # 不能有前导0的数字
    tokens = expr.replace('+', ' ').replace('-', ' ').replace('*', ' ').replace('/', ' ').split()
    if any(tok.startswith('0') and tok != "0" for tok in tokens):
        return False
    # 不能有除0操作
    try:
        if "/0" in expr:
            return False
        eval(expr)  # 检查是否可以正确计算
    except:
        return False
    return True


def generate_expressions(expression, positions):
	# """ 递归生成所有可能的算式 """
	results = []
	choices = '09+-*/'  # 可能的填充字符
	for replacements in itertools.product(choices, repeat=len(positions)):
		expr_list = list(expression)
		for pos, val in zip(positions, replacements):
			expr_list[pos] = val
		new_expr = "".join(expr_list)
		if is_valid_expression(new_expr):
			results.append(new_expr)
	return results


def solve_math_expression(expression):
    # 找出所有的 * 位置
    positions = [i for i, ch in enumerate(expression) if ch == '*']

    # 生成所有可能的表达式
    possible_expressions = generate_expressions(expression, positions)

    # 计算所有可能表达式的值
    values = []
    for expr in possible_expressions:
        try:
            values.append(eval(expr))
        except:
            continue  # 可能存在非法计算，跳过

    if not values:
        return "Error"

    max_val = max(values)
    min_val = min(values)

    # 计算平均值并保留两位小数
    result = (max_val + min_val) / 2
    return f"{expression}, {max_val}, {min_val},{result:.2f}"


# 示例测试
expression = "1*1+9-2*3/1"

time1 = time.time()
print(solve_math_expression(expression))
time2 = time.time()

print(time2 - time1)
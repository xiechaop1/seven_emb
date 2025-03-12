import itertools
import re
from decimal import Decimal, ROUND_HALF_UP


def is_valid(expression: str) -> bool:
    """检查表达式是否合法，防止前导零、除以零等问题"""
    try:
        # print(expression)
        tokens = re.findall(r'\d+|[-+*/()]', expression)
        for i in range(len(tokens) - 1):
            if tokens[i] in '+-*/' and tokens[i + 1] in '+*/':
                return False  # 避免 **, */, *+ 之类的非法情况
            if tokens[i] == '/' and tokens[i + 1] == '0':
                return False  # 除数不能为 0
        eval(expression)  # 额外的语法检查
        return True
    except:
        return False


def evaluate_expression(expression: str) -> float:
    """安全计算表达式的值"""
    try:
        return eval(expression)
    except:
        return float('inf')


def find_max_min_average(expression: str) -> str:
    """寻找表达式可能的最大值和最小值，并返回其平均值（保留两位小数）"""
    possible_values = set()
    missing_positions = [i for i, ch in enumerate(expression) if ch == '*']
    possible_replacements = '09+-*/'

    for replacements in itertools.product(possible_replacements, repeat=len(missing_positions)):
        new_expr = list(expression)
        for pos, repl in zip(missing_positions, replacements):
            new_expr[pos] = repl
        new_expr = ''.join(new_expr)

        if is_valid(new_expr):
            possible_values.add(evaluate_expression(new_expr))

    if possible_values:
        max_val = max(possible_values)
        min_val = min(possible_values)
        avg_val = (max_val + min_val) / 2
        return str(Decimal(avg_val).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))
    else:
        return "0.00"


# 示例测试
expr = "1*1+3+(*4*0)-2*3/1"
print(find_max_min_average(expr))
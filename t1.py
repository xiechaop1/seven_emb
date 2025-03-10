import itertools


def is_valid(expression):
    """ 检查表达式是否合法 """
    try:
        eval(expression)
        return True
    except ZeroDivisionError:
        return False
    except:
        return False


def generate_expressions(s):
    """ 生成所有可能的填充表达式 """
    chars = list(s)
    stars = [i for i, c in enumerate(chars) if c == '*']

    possible_chars = '0123456789+-*/'
    results = set()

    for repl in itertools.product(possible_chars, repeat=len(stars)):
        for i, ch in zip(stars, repl):
            chars[i] = ch
        expr = "".join(chars)
        if is_valid(expr):
            results.add(eval(expr))

    return results


def solve(expression):
    possible_values = generate_expressions(expression)
    max_val = max(possible_values)
    min_val = min(possible_values)
    avg_val = (max_val + min_val) / 2
    print(f"{avg_val:.2f}")


# 示例测试
solve("1*1+9-2*3/1")
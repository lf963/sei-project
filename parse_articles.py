import custom_exception as ex
import re
import sys

def parse(key_words):
    word_result = []
    operator_result = []

    # find string inside parentheses
    start = 0
    while True:
        start = key_words.find('(', start)
        if start == -1:
            break
        start += 1  # skip the bracket, move to the next character
        end = key_words.find(')', start)
        word_result.append(key_words[start:end])
        start += 1

    # find operator
    start = 0
    while True:
        start = key_words.find(')', start)
        if start == -1:
            break
        end = key_words.find('(', start)
        if end == -1:
            break
        operator_result.append(key_words[start + 1:end])
        start = end

    return word_result, operator_result


def is_balance_parentheses(s):
    my_stack = []
    for ch in s:
        if ch == '(':
            my_stack.append(ch)
        elif ch == ')':
            if len(my_stack) == 0:
                raise ex.BalanceParenthesesException("Parentheses are not balanced")
            my_stack.pop()
    if len(my_stack) != 0:
        raise ex.BalanceParenthesesException("Parentheses are not balanced")


def is_valid_operator(s):
    start = 0
    while True:
        start = s.find(')', start)
        if start == -1:
            break
        end = s.find('(', start)
        if end == -1:
            break
        if s[start+1:end] != "&" and s[start+1:end] != "|":
            raise ex.OperatorException("Operator should be & or |, cannot be %s" %s[start+1:end])
        start = end


def is_positive_window_size(size):
    if size < 1:
        raise ex.NegativeWindowSizException("Window size should be larger than zero")


def is_valid_window_size(window_size, rule_list):
    if window_size == -1:
        return
    for rule in rule_list:
        i = 0
        for j, ch in enumerate(rule):
            if ch == '+' or ch == '-':
                if j - i > int(window_size):
                    raise ex.WindowTooSmallException("Window size should be larger than all of your searched words")
                i = j + 1
        if len(rule[i:]) > int(window_size):
            raise ex.WindowTooSmallException("Window size should be larger than all of your searched words")


def has_parentheses(s):
    start = s.find("(")
    if start == -1:
        raise ex.HasParenthesesException("Cannot find parentheses")

    for i, ch in enumerate(s):
        if ch == '&' or ch == '|':
            if s[i-1] != ")" or s[i+1] != "(":
                raise ex.HasParenthesesException("Missing parentheses near %s" % s[i:i+2])


def parse_main():
    print("What you want to search:")
    rule = input()
    key_words = re.sub('[\s]', '', rule)  # remove white space

    if key_words.find(",") == -1:   # if user didn't define window size, set it as -1
        window_size = -1
        content = key_words
    else:
        try:
            is_positive_window_size(int(key_words.split(",")[0]))   # window size should be positive
        except ex.NegativeWindowSizException as err:
            sys.exit(err)
        content = key_words.split(",")[1]
        window_size = key_words.split(",")[0]

    try:
        is_balance_parentheses(content)   # parentheses should be balanced
    except ex.BalanceParenthesesException as err:
        sys.exit(err)

    try:
        is_valid_operator(content)  # operator should be & or |
    except ex.OperatorException as err:
        sys.exit(err)

    try:
        has_parentheses(content)  # every word should be inside parentheses
    except ex.HasParenthesesException as err:
        sys.exit(err)

    word_result, operator_result = parse(content)

    try:
        is_valid_window_size(window_size, word_result)  # windows size should be larger than every word
    except ex.WindowTooSmallException as err:
        sys.exit(err)

    return window_size, word_result, operator_result


if __name__ == '__main__':
    window_size, rule_list, operator_list = parse_main()
    print("----------------------------------------------------")
    print(window_size)
    print(rule_list)
    print(operator_list)
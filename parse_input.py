import and_or_operation
import custom_exception as ex
import re
import search_wildcard
import sys
import sliding_windows
import produce_graph_upper


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

    # find & | operator
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
                raise ex.MyException("Parentheses are not balanced")
            my_stack.pop()
    if len(my_stack) != 0:
        raise ex.MyException("Parentheses are not balanced")


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
            raise ex.MyException("Operator should be & or |, cannot be %s" %s[start+1:end])
        start = end


def is_positive_window_size(size):
    if int(size) < 1:
        raise ex.MyException("Window size should be a positive integer")


def is_valid_window_size(window_size, rule_list):
    if window_size == -1:
        return
    for rule in rule_list:
        i = 0
        for j, ch in enumerate(rule):
            if ch == '+' or ch == '-':
                if j - i > int(window_size):
                    raise ex.MyException("Window size should be larger than all of your searched words")
                i = j + 1
        if len(rule[i:]) > int(window_size):
            raise ex.MyException("Window size should be larger than all of your searched words")


def has_parentheses(s):
    start = s.find("(")
    if start == -1:
        raise ex.MyException("Cannot find parentheses")

    for i, ch in enumerate(s):
        if ch == '&' or ch == '|':
            if s[i-1] != ")" or s[i+1] != "(":
                raise ex.MyException("Missing parentheses near %s" % s[i:i+2])

def input_is_not_empty(key_words):
    if len(key_words) == 0:
        raise ex.MyException("Input cannot be empty")

def parse_main(search=0):
    print("What you want to search:")
    if search == 0:
        rule = input()
    else:
        rule = search
    key_words = re.sub('[\s]', '', rule)  # remove white space
    try:
        input_is_not_empty(key_words)
    except ex.MyException as err:
        sys.exit(err)

    if key_words.find(",") == -1:   # if user didn't define window size, set it as -1
        window_size = -1
        content = key_words
    else:
        try:
            print(key_words.split(",")[0])
            is_positive_window_size(key_words.split(",")[0])   # window size should be positive integer
        except ex.MyException as err:
            sys.exit(err)
        content = key_words.split(",")[1]
        window_size = int(key_words.split(",")[0])

    try:
        is_balance_parentheses(content)   # parentheses should be balanced
        is_valid_operator(content)  # operator should be & or |
        has_parentheses(content)  # every word should be inside parentheses
    except ex.MyException as err:
        sys.exit(err)

    word_result, operator_result = parse(content)

    try:
        is_valid_window_size(window_size, word_result)  # windows size should be larger than every word
    except ex.MyException as err:
        sys.exit(err)

    return window_size, word_result, operator_result, rule


if __name__ == '__main__':
    print("loding data..................")
    wiki = sliding_windows.load_data()
    while True:
        window_size, rule_list, operator_list, rule = parse_main()

        print("Call parse_input.py")
        print("Window size = %s" % window_size)
        print(rule_list)
        print(operator_list)
        print("----------------------------------------------------")
        print("call search_wildcard.py")
        if window_size == -1:
            final_result, graph_result, sentence = search_wildcard.step_1(window_size, rule_list)
        else:
            final_result, graph_result = search_wildcard.step_1(window_size, rule_list)
            print("sliding_windows.main()..............")
            final_result, sentence = sliding_windows.main(final_result, wiki)

        dot, last_node, result = and_or_operation.and_or(final_result, operator_list)
        produce_graph_upper.draw(window_size, rule, rule_list, graph_result, final_result, dot, last_node, result)

        # for key in sentence:
        #     print(key)
        #     print(sentence[key])

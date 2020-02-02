#!/usr/bin/env python3

import re


def _max_subarray_lr(lst, low, mid, high):
    left_total = 0
    max_left = max_right = 0
    current_total = 0
    for i in range(mid, low-1, -1):
        current_total += lst[i].get('profit')
        if current_total > left_total:
            left_total = current_total
            max_left = i

    right_total = 0
    current_total = 0
    for i in range(mid+1, high+1, 1):
        current_total += lst[i].get('profit')
        if current_total > right_total:
            right_total = current_total
            max_right = i

    return left_total+right_total, max_left, max_right


def maxProfit_divide_conquer(lst, low, high):
    if low == high:
        return lst[low].get('profit'), low, high
    else:
        mid = (low + high) // 2
        left_total, left_low, left_high = maxProfit_divide_conquer(lst, low, mid)
        right_total, right_low, right_high = maxProfit_divide_conquer(lst, mid+1, high)
        lr_total, lr_low, lr_high = _max_subarray_lr(lst, low, mid, high)

        if left_total >= right_total and left_total >= lr_total:
            return left_total, left_low, left_high
        elif right_total >= left_total and right_total >= lr_total:
            return right_total, right_low, right_high
        else:
            return lr_total, lr_low, lr_high


def maxProfit_iterative(lst):
    profit = 0
    buy_day = min_day = 0
    sell_day = 1

    for i in range(1, len(lst)):
        if lst[i].get('price') - lst[min_day].get('price') > profit:
            profit = lst[i].get('price') - lst[min_day].get('price')
            sell_day = i
            buy_day = min_day
        if lst[i].get('price') <= lst[min_day].get('price'):
            min_day = i

    return profit, buy_day, sell_day



def main():

    infile = 'inputPS5.txt'
    lst = list()

    with open(infile, "r") as f:
        for line in f:
            if re.match('[0-9]+ */ *[0-9]+', line):
                (day, price) = re.split(r' */ *', line.rstrip())
                day = int(day)
                price = int(price)
                lst.append({'day': day, 'price': price, 'profit': 0})

    for i in range(1, len(lst)):
        lst[i]['profit'] = lst[i].get('price') - lst[i-1].get('price')


    outfile = 'outputPS5.txt'
    with open(outfile, 'w+') as f:

        # some checks.
        if len(lst) < 2:
            f.write("ERROR: Too few entries.\n")
            return


        # find maximum subarray for divide and conquer approach.
        # buy_day will be 1 day before the first profit day.
        (profit_by_dc, profit_start_day, profit_end_day) = maxProfit_divide_conquer(lst, 0, len(lst)-1)

        # find maximum profit with iterative approach.
        (profit_by_iter, buy_day, sell_day) = maxProfit_iterative(lst)

        assert(profit_by_dc == profit_by_iter)

        if profit_by_dc <= 0:
            f.write("NOTICE: No profit can be earned by buying and selling a stock.\n")
        else:
            f.write("""Maximum Profit(Divide & Conquer): {}
Day to buy: {}
Day to sell: {}
""".format(profit_by_dc, lst[profit_start_day-1].get('day'), lst[profit_end_day].get('day')))

            f.write("""Maximum Profit(Iterative Solution): {}
Day to buy: {}
Day to sell: {}
""".format(profit_by_iter, lst[buy_day].get('day'), lst[sell_day].get('day')))


main()
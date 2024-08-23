from decimal import Decimal # используем специальный тип данных, чтобы не терять точность в числах с плавающей точкой


def round_price(price: Decimal, count) -> Decimal:
    return int(price * (10 ** count)) / Decimal(10 ** count)

def can_up(ind):
    return type(package_price_rounded[ind]) == Decimal and (Decimal("0.01") * package_count[ind] + sum_costs) <= min(contract_sum, sum_max_position_cost * Decimal("1.1")) and package_price_rounded[ind] < max_price[ind]

n = 0
names = []
vital_price = [] # ЖВ цена, если не жв, то прописать None
package_count = [] # кол-во упаковок
units_count = [] # кол-во ед изм в одной упаковке
status = [] # статус: 0 - нет КН, 1 - склад, 2 - есть КН (Кредит Нота)
farm_type = [] # 0 - не ЖВ лекарство, 1 - ЖВ лекарство 
purchasing_price = [] # закупочная цена, без НДС
selling_price = [] # цена ФОЦП, без НДС, если не жв, то прописать None
contract_sum = Decimal("0") # сумма контракта

algorithm_type = True # разные алгоритмы (влияет на разбиение)
for i in range(n):
    if farm_type[i] == 0:
        status[i] = 2
        vital_price[i] = 10000000
        selling_price[i] = 10000000

cost_price = [] # себестоимость ед товара
for i in range(n):
    cost_price.append(purchasing_price[i] * Decimal("1.1"))

all_cost_price = [] # себестоимость всего
for i in range(n):
    all_cost_price.append(package_count[i] * cost_price[i])
average_margin = contract_sum / sum(all_cost_price) - Decimal("1")

max_percent_margin = [] # максимальный процент наценки
for i in range(n):
    price = selling_price[i]
    if price <= 100:
        max_percent_margin.append(Decimal("0.2"))
    elif price > 500:
        max_percent_margin.append(Decimal("0.12"))
    else:
        max_percent_margin.append(Decimal("0.15"))

fixed_price = [] # фиксированная цена продажи за упаковку (без НДС)
for i in range(n):
    if status[i] in [0, 1]:
        fixed_price.append(purchasing_price[i] + min(selling_price[i], vital_price[i]) * max_percent_margin[i])
    else:
        fixed_price.append(0)

fixed_cost = [] # фиксированная стоимость (без НДС)
for i in range(n):
    if status[i] in [0, 1]:
        fixed_cost.append(fixed_price[i] * package_count[i])
    else:
        fixed_cost.append(0)

max_price_with_cn = [] # максимальная цена с кредит нотой (Без НДС)
for i in range(n):
    if status[i] == 2:
        max_price_with_cn.append(min(vital_price[i], selling_price[i]) * (1 + max_percent_margin[i]))
    else:
        max_price_with_cn.append(0)

max_cost_with_cn = [] # максимальная стоимость с КН (без НДС)
for i in range(n):
    max_cost_with_cn.append(package_count[i] * max_price_with_cn[i])

max_package_price = [] # макс цена упаковки (без НДС)
for i in range(n):
    if status[i] == 2:
        max_package_price.append(max_price_with_cn[i])
    else:
        max_package_price.append(fixed_price[i])

max_position_cost = [] # макс стоимость позиции (без НДС)
for i in range(n):
    max_position_cost.append(max_package_price[i] * package_count[i])
sum_max_position_cost = round_price(sum(max_position_cost), 2)

max_margin = [] # макс маржа
for i in range(n):
    if purchasing_price[i] == 0:
        max_margin.append(None)
    else:
        max_margin.append(max_package_price[i] / purchasing_price[i] - 1)

margin_maxmin_by_average = [] # Маржа больше/меньше относ сред
remaining_price_over_avg_margin = [] # Остаток цены сверх сред маржи (Без НДС)
price_without_avg_margin = [] # Цена после вычита сверх сред маржи (Без НДС)

for i in range(n):
    if max_margin[i] != None and max_margin[i] >= average_margin:
        remaining_price_over_avg_margin.append((max_margin[i] - average_margin) * purchasing_price[i])
        price_without_avg_margin.append(max_package_price[i] - remaining_price_over_avg_margin[i])
    else:
        remaining_price_over_avg_margin.append(0)
        price_without_avg_margin.append(0)

result_price = price_without_avg_margin.copy()

for _ in range(n):
    start_price = result_price.copy()
    result_price = []
    cost_price_can = [] # Себестоимость позиций, где можно увел цену
    specific_weight = [] # Удельный вес позиции
    position_cost = [] # Стоимость позиций (Без НДС)
    cost_position_up = [] # Увел стоимости позиции (Без НДС)
    price_position_up = [] # Увел цены позиции (Без НДС)
    
    for i in range(n):
        position_cost.append(start_price[i] * package_count[i])
        price = start_price[i]

        if price < max_package_price[i]:
            cost_price_can.append(all_cost_price[i])
        else:
            cost_price_can.append(0)

    sum_cost_price_can = sum(cost_price_can)
    sum_position_cost = sum(position_cost)

    for i in range(n):
        if sum_cost_price_can == 0:
            specific_weight.append(0)
        else:
            specific_weight.append(cost_price_can[i] / sum_cost_price_can)
    
    for i in range(n):
        cost_position_up.append((min(contract_sum / Decimal("1.1"), sum_max_position_cost) - sum_position_cost) * specific_weight[i])
        if package_count[i] == 0:
            price_position_up.append(0)
        else:
            price_position_up.append(cost_position_up[i] / package_count[i])
        if start_price[i] + price_position_up[i] > max_package_price[i]:
            result_price.append(max_package_price[i])
        else:
            result_price.append((start_price[i] + price_position_up[i]))

package_price_rounded = [] # Цена за упак (с НДС, округлённая)
for i in range(n):
    price = round_price(result_price[i] * Decimal("1.1"), 2)
    package_price_rounded.append(price)

cost_after_round = [] # Стоимость после округления (с НДС)
for i in range(n):
    cost_after_round.append(package_price_rounded[i] * package_count[i])

max_price = [] # Макс цена на товар (С НДС)
for i in range(n):
    if status[i] == 2:
        price = selling_price[i] * (Decimal("1") + max_percent_margin[i]) * Decimal("1.1")
    else:
        price = (purchasing_price[i] + selling_price[i] * max_percent_margin[i]) * Decimal("1.1")
    max_price.append(round_price(price, 2))
max_cost = min(contract_sum, sum_max_position_cost)
sum_costs = sum(cost_after_round)

can_up_price = [] # можно ли увеличить цену

for i in range(n):
    can_up_price.append(can_up(i))

while True in can_up_price:
    for i in range(n):
        if can_up_price[i]:
            package_price_rounded[i] += Decimal("0.01")
            cost_after_round[i] = package_price_rounded[i] * package_count[i]
            sum_costs = sum(cost_after_round)
            for j in range(n):
                can_up_price[j] = can_up(j)

if algorithm_type:
    for i in range(n):
        price = package_price_rounded[i] / units_count[i]
        if price != round_price(price, 2):
            price = round_price(price, 2)
            if (price + Decimal("0.01")) * units_count[i] <= max_price[i]:
                x = 100 * package_count[i] * price + package_count[i] - 100 / Decimal(units_count[i]) * package_count[i] * package_price_rounded[i]
                if x != int(x):
                    x = int(x) + 1
                y = package_count[i] - x
                if y == 0:
                    continue
                package_count[i] = x
                package_count.append(y)
                package_price_rounded[i] = round_price(price * units_count[i], 2)
                cost_after_round[i] = package_price_rounded[i] * package_count[i]
                package_price_rounded.append(round_price((price + Decimal("0.01")) * units_count[i], 2))
                names.append(names[i])
                max_price.append(max_price[i])
                units_count.append(units_count[i])
                max_package_price.append(max_package_price[i])
                cost_after_round.append(package_price_rounded[-1] * package_count[-1])
                sum_costs = sum(cost_after_round)
                n += 1
            else:
                package_price_rounded[i] = price * units_count[i]
else:
    for i in range(n):
        price = round_price(package_price_rounded[i] / units_count[i], 2)
        max_ = [0, None]
        for j in range(1, units_count[i]):
            if price * j + (price + Decimal("0.01")) * (units_count[i] - j) <= package_price_rounded[i] and max_[0] < price * j + (price + Decimal("0.01")) * (units_count[i] - j):
                max_ = [price * j + (price + Decimal("0.01")) * (units_count[i] - j), j]
        if max_[-1] is not None:
            units_count[i] = [j, units_count[i] - j]
            package_price_rounded[i] = [price * units_count[i][0], (price + Decimal("0.01")) * units_count[i][1]]

can_up_price = [] # можно ли увеличить цену

for i in range(n):
    can_up_price.append(can_up(i))

while True in can_up_price:
    for i in range(n):
        if can_up_price[i]:
            package_price_rounded[i] += Decimal("0.01")
            cost_after_round[i] = package_price_rounded[i] * package_count[i]
            sum_costs = sum(cost_after_round)
            for j in range(n):
                can_up_price[j] = can_up(j)
'''
итоговые цены лежат в package_price_rounded
'''
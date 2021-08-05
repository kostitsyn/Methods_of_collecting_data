# import chardet
#
# my_str = 'Привет мир!'
# encode_str = my_str.encode('utf-8')
# print(chardet.detect(encode_str))

import re

# my_str = '160 000 — 200 000 руб./месяц'
my_str = '200 000 руб./месяц'
# my_str = 'от 100 000 руб./месяц'
# my_str = 'По договоренности'

# res = re.match('\D+\s\D+', my_str)
# print(res)


# is_interval = re.match('.+ — .+', my_str)
# print(is_interval)

salary = int(''.join(re.findall('^(\d+)\s(\d*)', my_str)[0]))
print(salary)

# is_fixed_salary = re.match('^.*^(—).*$', my_str)
# print(is_fixed_salary)


# max_salary = int(''.join(re.findall('\s(\d+)\s(\d*)', my_str)[0]))
# print(max_salary)
#
# min_salary = ''.join(re.findall('(^\d+)\s(\d*)', my_str)[0])
# print(f'Минимальная зп: {int(min_salary)}')
#
# max_salary = ''.join(re.findall('—\s(\d+)\s(\d*)', my_str)[0])
# print(f'Максимальная зп: {int(max_salary)}')
#
currency = re.findall('\s(\D+\.)', my_str)[0]
print(currency)
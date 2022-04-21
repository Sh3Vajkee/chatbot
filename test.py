from datetime import datetime, date
import random
import datetime

print(date.today().month)
print(random.randint(1, 210))

a = date.today().month
print(type(a))
# n = datetime.now()
# m = datetime.fromtimestamp(datetime.now().timestamp())

# print(n)
# print(m)
# print(n.day)
# print(n.month)
# print(datetime.utcnow())
# print(int(n.timestamp()))
# print(m)

# d = n - m
# print(d)
# strd = str(n - m).split(', ')
# if len(strd) > 1:
#     days = strd[0].split()[0]
#     hours = strd[1][:strd[1].index(':')]
# else:
#     days = '0'
#     hours = strd[0][:strd[0].index(':')]
# print(d)
# print(f'{days} дней, {hours} часа(ов)')

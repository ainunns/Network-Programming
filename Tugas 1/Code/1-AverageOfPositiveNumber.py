n = int(input())
sum = 0
count = 0

for i in range(n):
  x = int(input())
  if x > 0:
    sum += x
    count += 1

if count == 0:
  print("No positive numbers")
else:
  print("{:.2f}".format(sum/count))
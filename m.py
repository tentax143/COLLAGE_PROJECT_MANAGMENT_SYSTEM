arr=[1,2,3,7,5]
target=12
sn= set()
for num in arr:
    cmp=target-num
    if cmp in sn:
        print(num,cmp)
        break
    sn.add(num)


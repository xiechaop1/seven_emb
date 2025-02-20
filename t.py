r = 25
g = 12
b = 12
m = max(r, g, b)
r1 = r
g1 = g
b1 = b
for i in range(m):
	if r1 > 0:
		r1 = r1 - 1
	if g1 > 0:
		g1 = g1 - 1
	if b1 > 0:
		b1 = b1 - 1
	print("rgb:", r1, g1, b1)

# for r1 in range(r, -1, -1):
# 	for g1 in range(g, -1, -1):
# 		for b1 in range(b, -1, -1):
# 			print("rgb:",r1,g1,b1)
# 			continue
# 		continue


print("end")

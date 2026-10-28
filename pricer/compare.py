import random
from black_scholes import bs_call
from monte_carlo import mc_call

random.seed(42)

print("Black-Scholes:", round(bs_call(100, 100, 1.0, 0.05, 0.20), 4))

for n in [100, 1000, 10000, 100000]:
    price = mc_call(100, 100, 1.0, 0.05, 0.20, n)
    print(n, "futures ->", round(price[0], 4))
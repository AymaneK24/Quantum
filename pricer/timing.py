import time
import random
from monte_carlo import mc_call

random.seed(42)
n = 10000000

start = time.time()
price, error = mc_call(100, 100, 1.0, 0.05, 0.20, n)
seconds = time.time() - start

print("futures:", n)
print("price:", round(price, 4), "give or take", round(error, 4))
print("seconds:", round(seconds, 1))
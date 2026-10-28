import matplotlib.pyplot as plt
from black_scholes import bs_call, call_payoff

K = 100
share_prices = []
payoffs = []
paper_prices = []

for S in range(60, 141):
    share_prices.append(S)
    payoffs.append(call_payoff(S, K))
    paper_prices.append(bs_call(S, K, 1.0, 0.05, 0.20))

plt.plot(share_prices, payoffs, label="Payoff at deadline")
plt.plot(share_prices, paper_prices, label="Price today (Black-Scholes)")
plt.xlabel("Share price S")
plt.ylabel("Value of the paper")
plt.title("Call option, K = 100")
plt.legend()
plt.grid(True)
plt.show()
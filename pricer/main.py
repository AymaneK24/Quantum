from black_scholes import bs_call, call_payoff

price = bs_call(100, 100, 1.0, 0.05, 0.20)
print("Price of the call paper today:", round(price, 4))

print("Payoff if phone ends at 130:", call_payoff(130, 100))
print("Payoff if phone ends at 80:", call_payoff(80, 100))
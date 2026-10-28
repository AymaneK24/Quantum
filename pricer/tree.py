from black_scholes import bs_call
from black_scholes import call_payoff, put_payoff
from math import exp, sqrt

def tree_price(S, K, T, r, sigma, n_steps, payoff, american=False):
    dt = T / n_steps
    up = exp(sigma * sqrt(dt))
    down = 1 / up
    p = (exp(r * dt) - down) / (up - down)
    shrink = exp(-r * dt)

    values = []
    for j in range(n_steps + 1):
        final_price = S * up ** j * down ** (n_steps - j)
        values.append(payoff(final_price, K))

    for step in range(n_steps - 1, -1, -1):
        new_values = []
        for j in range(step + 1):
            wait = shrink * (p * values[j + 1] + (1 - p) * values[j])
            if american:
                price_here = S * up ** j * down ** (step - j)
                use_now = payoff(price_here, K)
                new_values.append(max(wait, use_now))
            else:
                new_values.append(wait)
        values = new_values

    return values[0]




if __name__ == "__main__":
   
    print("Black-Scholes call:", round(bs_call(100, 100, 1.0, 0.05, 0.20), 4))
    for n in [2, 10, 50, 100, 500]:
        price = tree_price(100, 100, 1.0, 0.05, 0.20, n, call_payoff)
        print(n, "steps ->", round(price, 4))

    print()
    euro_put = tree_price(100, 100, 1.0, 0.05, 0.20, 500, put_payoff)
    amer_put = tree_price(100, 100, 1.0, 0.05, 0.20, 500, put_payoff, american=True)
    print("European put:", round(euro_put, 4))
    print("American put:", round(amer_put, 4))


   

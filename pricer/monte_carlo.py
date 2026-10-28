from black_scholes import call_payoff,  put_payoff
import random
from math import exp , sqrt
import time
  

def simulate_final_price(S, T, r, sigma): #σ (sigma) is the volatility  # σ² (sigma × sigma) is the variance
    luck = random.gauss(0, 1)
    steady_push = (r - 0.5 * sigma ** 2) * T
    random_move = sigma * sqrt(T) * luck
    return S * exp(steady_push + random_move)


def mc_call(S, K, T, r, sigma, n_futures):
    payoffs = []
    for i in range(n_futures):
        future_price = simulate_final_price(S, T, r, sigma)
        payoffs.append(call_payoff(future_price, K))

    average = sum(payoffs) / n_futures

    spread = 0
    for p in payoffs:
        spread = spread + (p - average) ** 2
    spread = spread / (n_futures - 1)

    error = sqrt(spread) / sqrt(n_futures)

    shrink = exp(-r * T)
    return average * shrink, error * shrink



def mc_put(S, K, T, r, sigma, n_futures):
    payoffs = []
    for i in range(n_futures):
        future_price = simulate_final_price(S, T, r, sigma)
        payoffs.append( put_payoff(future_price, K))

    average = sum(payoffs) / n_futures

    spread = 0
    for p in payoffs:
        spread = spread + (p - average) ** 2
    spread = spread / (n_futures - 1)

    error = sqrt(spread) / sqrt(n_futures)

    shrink = exp(-r * T)
    return average * shrink, error * shrink





def testit(L):
    for i in range(len(L)):
        print("for number of futures : " , L[i])
        start = time.time()
        x  = mc_call(100, 100, 1, 0.05, 0.2, L[i])
        end = time.time()
        print("price:", round(x[0], 4), "error:", round(x[1] / x[0] * 100, 2), "%")
        print("seconds taken :",round(end - start,4))
    return 0    


if __name__ == "__main__":
    print("Testing it with [10,100,1000,1000000]:")
    testit([10,100,1000,10000000])





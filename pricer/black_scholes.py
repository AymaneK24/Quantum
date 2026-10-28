from math import log, sqrt, exp , erf



def norm_cdf(x):
    return 0.5 * (1 + erf(x / sqrt(2)))

def call_payoff(S,K):
    return max(S-K,0)

def put_payoff(S,K):
    return max(K-S,0)

def bs_call(S,K,T,r,sigma):
    if T <= 0:
        return call_payoff(S,K)
    d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    what_you_receive = S * norm_cdf(d1)
    what_you_pay = K * exp(-r * T) * norm_cdf(d2)

    return what_you_receive - what_you_pay



def bs_put(S, K, T, r, sigma):
    if T <= 0:
        return put_payoff(S, K)
    d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    what_you_receive = K * exp(-r * T) * norm_cdf(-d2)
    what_you_pay = S * norm_cdf(-d1)

    return what_you_receive - what_you_pay



price = bs_call(100, 100, 1.0, 0.05, 0.20)
print("Price of the call paper today:", round(price, 4))

print("Payoff if phone ends at 130:", call_payoff(130, 100))
print("Payoff if phone ends at 80:", call_payoff(80, 100))



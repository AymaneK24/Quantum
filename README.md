# Option Pricer

An option pricing library built from scratch in **Python** and **C++17**, implementing three independent pricing methods and cross-validating them against each other.

| Method                            | Options supported                      | Idea                                                          |
| --------------------------------- | -------------------------------------- | ------------------------------------------------------------- |
| Black-Scholes (closed form)       | European call and put                  | Exact analytical formula                                      |
| Monte Carlo simulation            | European call and put                  | Simulate many futures, average the discounted payoffs         |
| Cox-Ross-Rubinstein binomial tree | European and **American** call and put | Backward induction on a recombining tree, with early exercise |

The goal of the project is to understand how bank pricing libraries work: the math, the numerical methods, testing a model against an independent reference, and performance.

## Results

All results use the same contract: S = 100, K = 100, T = 1 year, r = 5%, σ = 20%.

### The three methods agree

| Option        | Black-Scholes | Monte Carlo (10M paths) | Binomial tree (500 steps) |
| ------------- | ------------- | ----------------------- | ------------------------- |
| European call | 10.4506       | 10.4530 ± 0.0047        | 10.4466                   |
| European put  | 5.5735        |                         | 5.5695                    |
| American call |               |                         | 10.4466                   |
| American put  |               |                         | **6.0888**                |

- **American put > European put.** The right to exercise early is worth about 0.52 here (the early-exercise premium): deep in the money, taking K − S now and earning interest on it beats waiting.
- **American call = European call.** On a stock without dividends, exercising a call early is never optimal, because it means paying the strike sooner and giving up the optionality.

### Convergence

**Monte Carlo:** the standard error falls as **1/√N**. To halve the error, you need 4× more paths; to be 10× more precise, 100× more paths. This was verified empirically: going from 1,000 to 10,000,000 paths (×10,000) cut the error by ~96× (theory: √10,000 = 100).

**Binomial tree:** the error falls roughly as **1/N**, with an odd/even oscillation.

| Steps | Tree price | Error vs Black-Scholes |
| ----- | ---------- | ---------------------- |
| 10    | 10.2534    | 0.197                  |
| 100   | 10.4306    | 0.020                  |
| 500   | 10.4466    | 0.004                  |

## Benchmarks

Monte Carlo, European call, 10,000,000 paths:

| Implementation               | Threads | Time               | Speedup vs Python |
| ---------------------------- | ------- | ------------------ | ----------------- |
| Python (pure)                | 1       | 16.1 s (best of 3) | 1×                |
| C++17 (`-O2`)                | 1       | _to be measured_   |                   |
| C++17 (`-O2`), `std::thread` | _N_     | _to be measured_   |                   |

## Testing

Every method is checked against an independent reference with `pytest`:

- Black-Scholes against textbook values (call 10.4506, put 5.5735)
- Payoff edge cases and the "an option is never worth less than 0" rule
- **Put-call parity:** C − P = S − K·e^(−rT)
- **Monte Carlo vs Black-Scholes:** must agree within 3 standard errors
- **Binomial tree vs Black-Scholes:** must agree within 0.01 at 500 steps
- American put ≥ European put, and American call = European call

## How it works

**Black-Scholes**
`C = S·N(d1) − K·e^(−rT)·N(d2)`: the expected value of receiving the stock, minus the discounted expected value of paying the strike, under the risk-neutral measure.

**Monte Carlo**

1. Simulate one terminal price: `S_T = S·exp((r − ½σ²)T + σ√T·Z)`, with Z ~ N(0, 1)
2. Compute the payoff in that future
3. Repeat N times and average
4. Discount the average to today with `e^(−rT)`
5. Report the price **with its standard error**

**Binomial tree (CRR)**
`u = e^(σ√dt)`, `d = 1/u`, risk-neutral probability `p = (e^(r·dt) − d) / (u − d)`. Start from the payoffs at expiry and walk backward; at each node, value = discounted expectation of the two children. For American options, take `max(continuation, exercise now)` at every node.

**Multithreaded Monte Carlo (C++)**
The paths are split across threads. Each thread has its **own random generator** (sharing one would be a data race) and writes to its **own result slot**, so no locks are needed. The main thread joins all workers and combines the partial sums.

## Project structure

```
pricer/
    black_scholes.py        payoffs, Black-Scholes call and put
    monte_carlo.py          Monte Carlo pricer with standard error
    tree.py                 CRR binomial tree, European and American
    test_black_scholes.py   pytest suite
    timing.py               benchmark script
C++-Version/
    payoff.h                abstract Payoff class, CallPayoff, PutPayoff
    black_scholes.h/.cpp    Black-Scholes in C++
    mc_threaded.cpp         multithreaded Monte Carlo benchmark
```

## How to run

**Python** (from the `pricer` folder):

```
pip install pytest matplotlib
python -m pytest
python timing.py
```

**C++** (from the `C++-Version` folder):

```
g++ -std=c++17 -O2 -Wall -Wextra main.cpp black_scholes.cpp -o pricer
g++ -std=c++17 -O2 -Wall -Wextra -pthread mc_threaded.cpp -o mc_threaded
```

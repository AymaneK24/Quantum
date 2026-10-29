#include <iomanip>
#include <iostream>

#include "black_scholes.h"
#include "payoff.h"

int main() {
    double S = 100.0, K = 100.0, T = 1.0, r = 0.05, sigma = 0.20;

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "BS call: " << bs_call(S, K, T, r, sigma) << "\n";
    std::cout << "BS put:  " << bs_put(S, K, T, r, sigma) << "\n";

    CallPayoff call(K);
    PutPayoff put(K);
    std::cout << "Call payoff at 130: " << call(130.0) << "\n";
    std::cout << "Put payoff at 60:   " << put(60.0) << "\n";

    const Payoff& some_payoff = put;
    std::cout << "Through a Payoff&:  " << some_payoff(60.0) << "\n";
    return 0;
}
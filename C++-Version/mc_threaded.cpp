// Milestone 5: Multithreaded Monte Carlo pricer for a European call.
//
// Idea: split the N futures between several threads. Each thread simulates
// its own share of futures with its OWN random generator, and writes its
// results into its OWN slot of a vector. The main thread waits for everyone
// (join), then adds the slots together. No two threads ever write to the
// same variable, so there is no data race and no mutex is needed.
//
// Build:  g++ -std=c++17 -O2 -Wall -Wextra -pthread mc_threaded.cpp -o mc_threaded
// Run:    .\mc_threaded.exe   (Windows)   or   ./mc_threaded   (Linux/macOS)

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <random>
#include <thread>
#include <vector>

// What one thread sends back: enough to compute the average AND the error.
struct PartialResult {
    double sum = 0.0;          // sum of payoffs
    double sum_squares = 0.0;  // sum of payoffs squared (for the error)
    std::int64_t count = 0;    // how many futures this thread simulated
};

struct McResult {
    double price;
    double std_error;
};

// The work of ONE thread: simulate `n_futures` futures and fill `out`.
void simulate_chunk(double S, double K, double T, double r, double sigma,
                    std::int64_t n_futures, std::uint64_t seed,
                    PartialResult& out) {
    // Each thread owns its generator. Sharing one generator between threads
    // would be a data race (and would also be slow because of contention).
    std::mt19937_64 generator(seed);
    std::normal_distribution<double> luck(0.0, 1.0);

    // Constants computed once, outside the loop (same as the Python version).
    const double steady_push = (r - 0.5 * sigma * sigma) * T;
    const double luck_scale = sigma * std::sqrt(T);

    // Local variables: fast, private to this thread.
    double sum = 0.0;
    double sum_squares = 0.0;

    for (std::int64_t i = 0; i < n_futures; ++i) {
        const double future_price = S * std::exp(steady_push + luck_scale * luck(generator));
        const double payoff = std::max(future_price - K, 0.0);
        sum += payoff;
        sum_squares += payoff * payoff;
    }

    // Write to the shared vector only ONCE, at the end, in this thread's own slot.
    out.sum = sum;
    out.sum_squares = sum_squares;
    out.count = n_futures;
}

McResult mc_call_threaded(double S, double K, double T, double r, double sigma,
                          std::int64_t n_futures, int n_threads,
                          std::uint64_t seed = 42) {
    std::vector<PartialResult> partials(n_threads);  // one slot per thread
    std::vector<std::thread> workers;
    workers.reserve(n_threads);

    // Split the work: every thread gets n / n_threads futures,
    // and the first `remainder` threads get one extra.
    const std::int64_t base = n_futures / n_threads;
    const std::int64_t remainder = n_futures % n_threads;

    for (int t = 0; t < n_threads; ++t) {
        const std::int64_t my_share = base + (t < remainder ? 1 : 0);
        const std::uint64_t my_seed = seed + 1000003ULL * static_cast<std::uint64_t>(t);
        // std::ref: pass the slot by reference, so the thread writes into the vector.
        workers.emplace_back(simulate_chunk, S, K, T, r, sigma, my_share, my_seed,
                             std::ref(partials[t]));
    }

    // Wait for every thread to finish before reading the results.
    for (std::thread& w : workers) {
        w.join();
    }

    // Combine the partial results (single-threaded, so no race here).
    double sum = 0.0;
    double sum_squares = 0.0;
    std::int64_t count = 0;
    for (const PartialResult& p : partials) {
        sum += p.sum;
        sum_squares += p.sum_squares;
        count += p.count;
    }

    const double n = static_cast<double>(count);
    const double average = sum / n;
    const double variance = (sum_squares - n * average * average) / (n - 1.0);
    const double std_error = std::sqrt(variance / n);
    const double shrink = std::exp(-r * T);

    return {average * shrink, std_error * shrink};
}

double norm_cdf(double x) {
    return 0.5 * std::erfc(-x / std::sqrt(2.0));
}

double bs_call(double S, double K, double T, double r, double sigma) {
    const double d1 = (std::log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * std::sqrt(T));
    const double d2 = d1 - sigma * std::sqrt(T);
    return S * norm_cdf(d1) - K * std::exp(-r * T) * norm_cdf(d2);
}

int main() {
    const double S = 100.0, K = 100.0, T = 1.0, r = 0.05, sigma = 0.20;
    const std::int64_t n_futures = 10'000'000;

    const unsigned cores = std::thread::hardware_concurrency();
    std::cout << "Logical cores on this machine: " << cores << "\n";
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Black-Scholes reference: " << bs_call(S, K, T, r, sigma) << "\n\n";

    std::cout << "threads |   price  |  error  | seconds | speedup\n";
    std::cout << "--------+----------+---------+---------+--------\n";

    double one_thread_seconds = 0.0;
    for (int n_threads : {1, 2, 4, 8}) {
        const auto start = std::chrono::steady_clock::now();
        const McResult result = mc_call_threaded(S, K, T, r, sigma, n_futures, n_threads);
        const auto stop = std::chrono::steady_clock::now();
        const double seconds = std::chrono::duration<double>(stop - start).count();

        if (n_threads == 1) {
            one_thread_seconds = seconds;
        }

        std::cout << std::setw(7) << n_threads << " | "
                  << std::setw(8) << result.price << " | "
                  << std::setw(7) << result.std_error << " | "
                  << std::setw(7) << std::setprecision(3) << seconds << " | "
                  << std::setw(5) << std::setprecision(2) << one_thread_seconds / seconds << "x\n"
                  << std::setprecision(4);
    }
    return 0;
}
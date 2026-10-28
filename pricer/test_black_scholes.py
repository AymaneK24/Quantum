from black_scholes import bs_call, call_payoff, put_payoff, bs_put
import random
from monte_carlo import mc_call, mc_put
from tree import tree_price 

def test_call_payoff():
    assert call_payoff(130, 100) == 30
    assert call_payoff(80, 100) == 0


def test_put_payoff():
    assert put_payoff(60, 100) == 40
    assert put_payoff(120, 100) == 0


def test_bs_call_known_value():
    price = bs_call(100, 100, 1.0, 0.05, 0.20)
    assert abs(price - 10.4506) < 0.0001


def test_bs_put_known_value():
    price = bs_put(100, 100, 1.0, 0.05, 0.20)
    assert abs(price - 5.5735) < 0.0001


def test_put_is_never_negative():
    assert bs_put(100, 100, 1.0, 0.05, 0.20) >= 0
    assert bs_put(150, 100, 1.0, 0.05, 0.20) >= 0
    assert bs_put(50, 100, 1.0, 0.05, 0.20) >= 0


def test_mc_call_agrees_with_black_scholes():
    random.seed(42)
    exact = bs_call(100, 100, 1.0, 0.05, 0.20)
    price, error = mc_call(100, 100, 1.0, 0.05, 0.20, 100000)
    assert abs(price - exact) < 3 * error


def test_mc_put_agrees_with_black_scholes():
    random.seed(42)
    exact = bs_put(100, 100, 1.0, 0.05, 0.20)
    price, error = mc_put(100, 100, 1.0, 0.05, 0.20, 100000)
    assert abs(price - exact) < 3 * error


def test_tree_call_agrees_with_black_scholes():
    tree = tree_price(100, 100, 1.0, 0.05, 0.20, 500, call_payoff)
    exact = bs_call(100, 100, 1.0, 0.05, 0.20)
    assert abs(tree - exact) < 0.01


def test_american_put_worth_at_least_european():
    euro = tree_price(100, 100, 1.0, 0.05, 0.20, 500, put_payoff)
    amer = tree_price(100, 100, 1.0, 0.05, 0.20, 500, put_payoff, american=True)
    assert amer >= euro


def test_american_call_equals_european_call():
    euro = tree_price(100, 100, 1.0, 0.05, 0.20, 500, call_payoff,  False)
    amer = tree_price(100, 100, 1.0, 0.05, 0.20, 500, call_payoff, american=True)
    assert abs(amer - euro) < 1e-9

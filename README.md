# Market Simulation: Randomized Order Book Dynamics

This project provides a **high-level simulation** of a continuous-limit order book using **randomly generated orders**. Unlike traditional market simulators that rely on an external or “true” price feed, this approach **originates prices** from the **random interplay of limit and market orders**. In other words, **the order book itself** (with its evolving bids and asks) determines the trading prices, rather than referencing any exogenous data.

---

## Overview

1. **Purely Stochastic Price Formation** 
   - New orders (both **buys** and **sells**) arrive according to **Poisson processes**, parameterized by an arrival rate ($\gamma$).  
   - Each order can be either **limit** or **market**, with probabilities set by a configurable ratio ($\rho$).  
   - There is no continuous “true” midprice feeding the simulation. Instead, the **limit orders** collectively create a **range** of possible trading prices, and market orders interact within that range.

2. **Limit Order Book Mechanics**  
   - The simulation maintains separate queues for **bids** (buy orders) and **asks** (sell orders).  
   - Orders are executed under **price-time priority**: the best-priced orders trade first, and if prices tie, the oldest orders match first.  
   - **Market orders** match immediately against the current best bid or ask, while **limit orders** may rest in the book if they do not find an immediate match.

3. **Cancellation and Lifetime**  
   - Each limit order has a **random lifetime** drawn from an exponential distribution with a **hazard rate** \$\mu$.  
   - When the order’s lifetime ends, it is removed from the book if it hasn’t already executed. This keeps the simulated order book dynamic, constantly adding new orders and removing old ones.

4. **Parameter Tuning**  
   - **Arrival Rate** ($\gamma$): How frequently new orders are generated.  
   - **Hazard Rate** ($\mu$): Governs the typical lifetime of orders.  
   - **Buy-to-Sell Ratio** ($\beta$): Proportion of buy orders vs. sell orders.  
   - **Limit-to-Market Ratio** ($\rho$): The chance that a new order is a limit order rather than a market order.  
   - **Limit order exponential factor** ($\lambda_L$): Determines the shape of the exponentaial function for limit order amounts.
   - **Market order exponential factor** ($\lambda_M$): Determines the shape of the exponentaial function for market order amounts.
   - **Maximum halfspread** ($\sigma$): Caps the maximum spread-to-mid at which limit orders can be submitted

5. **Why Use It**  
   - Offers a **lightweight** way to see how an order book evolves **without** external price quotes.  
   - Ideal for experimenting with different arrival intensities, order sizes, or cancellation dynamics, and observing **emergent** price formation.

---

This project ultimately demonstrates how an **order-driven market** can generate its own simulated prices through the **random arrivals** and **executions** of buy and sell orders, providing a purely **endogenous** perspective on price discovery.

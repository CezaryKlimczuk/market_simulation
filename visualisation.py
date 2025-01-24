import plotly.graph_objects as go

from orderbook import OrderBook, OrderSide


def plot_orderbook(orderbook: OrderBook, depth: int = 5) -> go.Figure:
    """
    Plots the top `depth` bid and ask price levels of the given OrderBook
    on a numeric y-axis spaced by instrument.min_tick_size.
    
    :param orderbook: An OrderBook instance containing bids and asks.
    :param depth: Number of bid price levels (highest) and ask price levels (lowest) to display.
    :return: A Plotly Figure object.
    """

    # Taking the bids from the top `depth` rungs
    bid_prices = sorted(list(set([order.price for order in orderbook.bids])), reverse=True)
    top_bids = sorted([order for order in orderbook.bids if order.price > bid_prices[depth]], key=lambda o: o.price, reverse=True)


    # Taking the asks from the top `depth` rungs
    ask_prices = sorted(list(set([order.price for order in orderbook.asks])))
    top_asks = sorted([order for order in orderbook.asks if order.price < ask_prices[depth]], key=lambda o: o.price)

    # Combining them into a single list for iteration
    display_orders = top_bids + top_asks

    if not display_orders:
        fig = go.Figure()
        fig.update_layout(title="OrderBook is empty")
        return fig

    prices = [o.price for o in display_orders if o.price is not None]
    min_price = min(prices)
    max_price = max(prices)
    tick_size = orderbook.instrument.min_tick_size

    # Add each order as its own trace.
    # x = volume (amount)
    # y = numeric price
    # orientation = 'h' (horizontal bars)
    # barmode='stack' is set at layout level
    # Separating bids and asks via offsetgroup so they don't stack together.
    fig = go.Figure()
    for order in display_orders:
        if order.price is None:
            continue
        
        # Distinguishing color & offset group by side
        if order.side == OrderSide.BUY:
            bar_color = "green"
            offsetgrp = "bid"
        else:
            bar_color = "red"
            offsetgrp = "ask"

        fig.add_trace(
            go.Bar(
                x=[order.amount],        # Bar length is the volume
                y=[order.price],         # Numeric price
                orientation='h',
                name=f"{order.side.name} {order.counterpart_id}",
                marker_color=bar_color,
                offsetgroup=offsetgrp,
                hovertemplate=(
                    "Counterparty: %{customdata[0]}<br>"
                    "Amount: %{x}<br>"
                    "Price: %{y}<extra></extra>"
                ),
                # Passing extra info in customdata for easy reference in hovertemplate
                customdata=[[order.counterpart_id]],
            )
        )

    # Configure layout
    fig.update_layout(
        title=f"Order Book (Depth = {depth}) for {orderbook.instrument.code}",
        xaxis_title="Volume (Amount)",
        yaxis_title="Price",
        barmode='stack',
        hovermode='closest',
    )

    # Make y-axis numeric with step = min_tick_size
    # #xplicitly setting a small margin on min/max so bars don't get cut off
    fig.update_yaxes(
        range=[min_price - tick_size, max_price + tick_size],
        tick0=min_price,          # where the first tick should start
        dtick=tick_size,          # distance between ticks
        tickformat=".2f",         # show prices with 2 decimal places or as appropriate
        showgrid=True,
        zeroline=False
    )

    return fig

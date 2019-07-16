#  Drakkar-Software OctoBot-Trading
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import asyncio
import logging
from asyncio import sleep

from cli import get_should_display_callbacks_logs
from octobot_trading.channels import TICKER_CHANNEL, RECENT_TRADES_CHANNEL, ORDER_BOOK_CHANNEL, KLINE_CHANNEL, \
    OHLCV_CHANNEL, BALANCE_CHANNEL, TRADES_CHANNEL, POSITIONS_CHANNEL, ORDERS_CHANNEL
from octobot_trading.channels.exchange_channel import ExchangeChannels
from octobot_trading.exchanges.exchange_manager import ExchangeManager
from octobot_trading.traders.trader import Trader
from octobot_trading.traders.trader_simulator import TraderSimulator


async def ticker_callback(exchange, symbol, ticker):
    if get_should_display_callbacks_logs():
        logging.info(f"TICKER : EXCHANGE = {exchange} || SYMBOL = {symbol} || TICKER = {ticker}")


async def order_book_callback(exchange, symbol, asks, bids):
    if get_should_display_callbacks_logs():
        logging.info(f"ORDERBOOK : EXCHANGE = {exchange} || SYMBOL = {symbol} || ASKS = {asks} || BIDS = {bids}")


async def ohlcv_callback(exchange, symbol, time_frame, candle):
    if get_should_display_callbacks_logs():
        logging.info(
            f"OHLCV : EXCHANGE = {exchange} || SYMBOL = {symbol} || TIME FRAME = {time_frame} || CANDLE = {candle}")


async def recent_trades_callback(exchange, symbol, recent_trades):
    if get_should_display_callbacks_logs():
        logging.info(f"RECENT TRADE : EXCHANGE = {exchange} || SYMBOL = {symbol} || RECENT TRADE = {recent_trades}")


async def kline_callback(exchange, symbol, time_frame, kline):
    if get_should_display_callbacks_logs():
        logging.info(
            f"KLINE : EXCHANGE = {exchange} || SYMBOL = {symbol} || TIME FRAME = {time_frame} || KLINE = {kline}")


async def balance_callback(exchange, balance):
    if get_should_display_callbacks_logs():
        logging.info(f"BALANCE : EXCHANGE = {exchange} || BALANCE = {balance}")


async def trades_callback(exchange, symbol, trade):
    if get_should_display_callbacks_logs():
        logging.info(f"TRADES : EXCHANGE = {exchange} || SYMBOL = {symbol} || TRADE = {trade}")


async def orders_callback(exchange, symbol, order, is_closed, is_updated, is_from_bot):
    if get_should_display_callbacks_logs():
        logging.info(f"ORDERS : EXCHANGE = {exchange} || SYMBOL = {symbol} || ORDER = {order} "
                     f"|| CLOSED = {is_closed} || UPDATED = {is_updated} || FROM_BOT = {is_from_bot}")


async def positions_callback(exchange, symbol, position, is_closed, is_updated, is_from_bot):
    if get_should_display_callbacks_logs():
        logging.info(f"POSITIONS : EXCHANGE = {exchange} || SYMBOL = {symbol} || POSITIONS = {position}"
                     f"|| CLOSED = {is_closed} || UPDATED = {is_updated} || FROM_BOT = {is_from_bot}")


async def handle_new_exchange(config, exchange_name, sandboxed=False):
    simulation = True

    exchange = ExchangeManager(config, exchange_name, is_simulated=simulation, is_backtesting=False, rest_only=True)
    await exchange.initialize()

    # print(dir(ccxt.bitmex()))

    if simulation:
        trader = TraderSimulator(config, exchange)
    else:
        trader = Trader(config, exchange)
    await trader.initialize()

    # set sandbox mode
    exchange.exchange.client.setSandboxMode(sandboxed)

    # consumers
    ExchangeChannels.get_chan(TICKER_CHANNEL, exchange_name).new_consumer(ticker_callback)
    ExchangeChannels.get_chan(RECENT_TRADES_CHANNEL, exchange_name).new_consumer(recent_trades_callback)
    ExchangeChannels.get_chan(ORDER_BOOK_CHANNEL, exchange_name).new_consumer(order_book_callback)
    ExchangeChannels.get_chan(KLINE_CHANNEL, exchange_name).new_consumer(kline_callback)
    ExchangeChannels.get_chan(OHLCV_CHANNEL, exchange_name).new_consumer(ohlcv_callback)

    ExchangeChannels.get_chan(BALANCE_CHANNEL, exchange_name).new_consumer(balance_callback)
    ExchangeChannels.get_chan(TRADES_CHANNEL, exchange_name).new_consumer(trades_callback)
    ExchangeChannels.get_chan(POSITIONS_CHANNEL, exchange_name).new_consumer(positions_callback)
    ExchangeChannels.get_chan(ORDERS_CHANNEL, exchange_name).new_consumer(orders_callback)

    return exchange


def create_cli_exchange(config, exchange_name, sandboxed=False):
    current_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(current_loop)
    should_stop = False
    exchange = current_loop.run_until_complete(handle_new_exchange(config, exchange_name, sandboxed))
    while not should_stop:
        current_loop.run_until_complete(sleep(1))
# cython: language_level=3
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
from octobot_trading.util.initializable cimport Initializable


cdef class PricesManager(Initializable):
    cdef object logger
    cdef object exchange_manager

    cdef public object valid_price_received_event

    cdef public double mark_price
    cdef public double mark_price_set_time

    cdef dict mark_price_from_sources

    cdef void _set_mark_price_value(self, double mark_price)
    cdef void _reset_prices(self)
    cdef void _ensure_price_validity(self)
    cdef bint _are_other_sources_valid(self, str mark_price_source)

    cpdef bint set_mark_price(self, double mark_price, str mark_price_source)

cpdef double calculate_mark_price_from_recent_trade_prices(list recent_trade_prices)

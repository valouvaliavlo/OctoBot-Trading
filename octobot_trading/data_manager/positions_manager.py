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
from collections import OrderedDict

from octobot_commons.logging.logging_util import get_logger

from octobot_trading.data.position import Position
from octobot_trading.enums import ExchangeConstantsPositionColumns
from octobot_trading.util.initializable import Initializable


class PositionsManager(Initializable):
    MAX_POSITIONS_COUNT = 2000

    def __init__(self, config, trader, exchange_manager):
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)
        self.config, self.trader, self.exchange_manager = config, trader, exchange_manager

        self.positions = OrderedDict()

    async def initialize_impl(self):
        self._reset_positions()

    def get_all_positions(self, symbol=None, since=None, limit=None):
        return self._select_positions(symbol=symbol, since=since, limit=limit)

    def get_open_positions(self, symbol=None, since=None, limit=None):
        return self._select_positions(True, symbol, since, limit)

    def get_closed_positions(self, symbol=None, since=None, limit=None):
        return self._select_positions(False, symbol, since, limit)

    def upsert_position(self, position_id, raw_position) -> (bool, bool, bool):
        if position_id not in self.positions:
            self.positions[position_id] = self._create_position_from_raw(raw_position)
            self._check_positions_size()
            return True, not self.positions[position_id].is_open, False

        updated: bool = self._update_position_from_raw(self.positions[position_id], raw_position)
        return updated, not self.positions[position_id].is_open, updated

    # private
    def _check_positions_size(self):
        if len(self.positions) > self.MAX_POSITIONS_COUNT:
            self._remove_oldest_positions(int(self.MAX_POSITIONS_COUNT / 2))

    def _create_position_from_raw(self, raw_position):
        position = Position(self.trader)
        position.update(**self._parse_position_from_raw(raw_position))
        return position

    def _update_position_from_raw(self, position, raw_position):
        return position.update(**self._parse_position_from_raw(raw_position))

    def _parse_position_from_raw(self, raw_position) -> dict:
        currency, market = self.exchange_manager.get_exchange_quote_and_base(
            raw_position[ExchangeConstantsPositionColumns.SYMBOL.value])
        return {
            "symbol": self.exchange_manager.get_exchange_symbol(raw_position[ExchangeConstantsPositionColumns.SYMBOL.value]),
            "currency": currency,
            "market": market,
            "entry_price": raw_position[ExchangeConstantsPositionColumns.ENTRY_PRICE.value],
            "quantity": raw_position[ExchangeConstantsPositionColumns.QUANTITY.value],
            "liquidation_price": raw_position[ExchangeConstantsPositionColumns.LIQUIDATION_PRICE.value],
            "position_id": None,
            "timestamp": raw_position[ExchangeConstantsPositionColumns.TIMESTAMP.value],
            "unrealised_pnl": raw_position[ExchangeConstantsPositionColumns.UNREALISED_PNL.value],
            "leverage": raw_position[ExchangeConstantsPositionColumns.LEVERAGE.value],
            "is_open": raw_position[ExchangeConstantsPositionColumns.IS_OPEN.value],
            "mark_price": raw_position[ExchangeConstantsPositionColumns.MARK_PRICE.value]
        }

    def _select_positions(self, is_open=None, symbol=None, since=None, limit=None):
        positions = [
            position
            for position in self.positions.values()
            if (
                    (is_open is None or position.is_open == is_open) and
                    (symbol is None or (symbol and position.symbol == symbol)) and
                    (since is None or (since and position.timestamp < since))
            )
        ]
        return positions if limit is None else positions[0:limit]

    def _reset_positions(self):
        self.positions = OrderedDict()

    def _remove_oldest_positions(self, nb_to_remove):
        for _ in range(nb_to_remove):
            self.positions.popitem(last=False)
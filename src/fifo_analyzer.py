from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass
class Lot:
    symbol: str
    quantity: Decimal
    price: Decimal
    date: datetime
    commission: Decimal = Decimal('0')


@dataclass
class SellMatch:
    sell_date: datetime
    symbol: str
    currency: str
    quantity: Decimal
    proceeds: Decimal
    cost_basis: Decimal
    commission: Decimal
    gain_loss: Decimal


@dataclass
class DividendRecord:
    date: datetime
    symbol: str
    currency: str
    amount: Decimal
    withholding: Decimal = Decimal('0')
    net_amount: Decimal = Decimal('0')


class FIFOAnalyzer:
    def __init__(self):
        self._lots: dict[str, list[Lot]] = defaultdict(list)
        self._dividends: list[DividendRecord] = []
        self._withholdings: list[dict] = []
        self._sell_matches: list[SellMatch] = []
        self.unmatched_sells: list[dict] = []

    def ingest_trades(self, trades: list[dict[str, Any]]) -> None:
        for trade in trades:
            self._process_trade(trade)

    def ingest_dividends(self, dividends: list[dict[str, Any]]) -> None:
        for div in dividends:
            currency = div.get('Currency', '')
            if 'Total' in currency or 'Total' in str(div.get('Description', '')):
                continue

            date_str = div.get('Date')
            if date_str:
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                except Exception:
                    date = datetime.now()
            else:
                date = datetime.now()

            symbol = self._extract_symbol_from_description(div.get('Description', ''))

            amount = div.get('Amount')
            if isinstance(amount, str):
                amount = Decimal(amount.replace(',', ''))
            elif amount is None:
                amount = Decimal('0')

            withholding = self._match_withholding(symbol, date_str)
            net_amount = amount + withholding

            self._dividends.append(DividendRecord(
                date=date,
                symbol=symbol,
                currency=div.get('Currency', 'USD'),
                amount=amount,
                withholding=withholding,
                net_amount=net_amount
            ))

    def ingest_withholdings(self, withholdings: list[dict[str, Any]]) -> None:
        filtered = []
        for wh in withholdings:
            if 'Total' in str(wh.get('Description', '')) or not wh.get('Description'):
                continue
            filtered.append(wh)
        self._withholdings = filtered

    def _match_withholding(self, symbol: str, date_str: str) -> Decimal:
        for wh in self._withholdings:
            wh_desc = str(wh.get('Description', ''))
            wh_date = str(wh.get('Date', ''))
            if symbol in wh_desc and wh_date == date_str:
                amount = wh.get('Amount')
                if isinstance(amount, str):
                    return Decimal(amount.replace(',', ''))
                elif amount is not None:
                    return Decimal(str(amount))
        return Decimal('0')

    def _process_trade(self, trade: dict[str, Any]) -> None:
        asset_category = trade.get('Asset Category', '')
        if asset_category != 'Stocks':
            return

        quantity = trade.get('Quantity')
        if quantity is None:
            return

        symbol = trade.get('Symbol', '')
        if not symbol:
            symbol = self._extract_symbol_from_description(trade.get('Description', ''))

        price = trade.get('T. Price')
        if price is None:
            return

        commission = trade.get('Comm/Fee')
        if commission is None:
            commission = Decimal('0')
        elif isinstance(commission, str):
            commission = Decimal(commission.replace(',', ''))
        elif isinstance(commission, Decimal):
            commission = commission

        date = trade.get('DateTime')
        if date is None:
            return

        if quantity > 0:
            lot = Lot(
                symbol=symbol,
                quantity=quantity,
                price=price,
                date=date,
                commission=abs(commission)
            )
            self._lots[symbol].append(lot)
            self._lots[symbol].sort(key=lambda x: x.date)

        elif quantity < 0:
            currency = trade.get('Currency', 'USD')
            self._match_sell(symbol, abs(quantity), price, date, abs(commission), trade, currency)

    def _match_sell(self, symbol: str, quantity: Decimal, price: Decimal,
                    date: datetime, commission: Decimal, trade: dict, currency: str) -> None:
        proceeds = quantity * price - commission
        cost_basis = Decimal('0')
        remaining = quantity

        lots = self._lots.get(symbol, [])

        while remaining > 0 and lots:
            lot = lots[0]
            if lot.quantity <= remaining:
                cost_basis += lot.quantity * lot.price + lot.commission
                remaining -= lot.quantity
                lots.pop(0)
            else:
                ratio = Decimal(remaining) / Decimal(lot.quantity)
                cost_basis += remaining * lot.price + ratio * lot.commission
                lot.quantity -= remaining
                lot.commission -= ratio * lot.commission
                remaining = Decimal('0')

        gain_loss = proceeds - cost_basis

        if remaining > 0:
            self.unmatched_sells.append({
                'symbol': symbol,
                'quantity': str(remaining),
                'date': date.isoformat(),
                'price': str(price),
                'proceeds': str(proceeds),
                'cost_basis': str(cost_basis),
                'gain_loss': str(gain_loss)
            })
        else:
            self._sell_matches.append(SellMatch(
                sell_date=date,
                symbol=symbol,
                currency=currency,
                quantity=quantity,
                proceeds=proceeds,
                cost_basis=cost_basis,
                commission=commission,
                gain_loss=gain_loss
            ))

    def _extract_symbol_from_description(self, description: str) -> str:
        if not description:
            return ''
        parts = description.split()
        if parts:
            return parts[0].strip()
        return ''

    def annual_report(self) -> dict[str, Any]:
        report: dict[str, Any] = {
            'realized_gains': [],
            'dividends': [],
            'withholdings': [],
            'summary': {}
        }

        gains_by_year_currency = defaultdict(lambda: {'short_term': Decimal('0'), 'long_term': Decimal('0'), 'currency': ''})
        for match in self._sell_matches:
            year = match.sell_date.year
            key = (year, match.currency)
            gains_by_year_currency[key]['currency'] = match.currency
            if (match.sell_date - self._find_purchase_date(match.symbol)).days > 365:
                gains_by_year_currency[key]['long_term'] += match.gain_loss
            else:
                gains_by_year_currency[key]['short_term'] += match.gain_loss

            report['realized_gains'].append({
                'symbol': match.symbol,
                'currency': match.currency,
                'quantity': str(match.quantity),
                'sell_date': match.sell_date.isoformat(),
                'proceeds': str(match.proceeds),
                'cost_basis': str(match.cost_basis),
                'gain_loss': str(match.gain_loss)
            })

        dividends_by_year_currency = defaultdict(lambda: {'gross': Decimal('0'), 'withholding': Decimal('0'), 'net': Decimal('0'), 'currency': ''})
        for div in self._dividends:
            year = div.date.year
            key = (year, div.currency)
            dividends_by_year_currency[key]['currency'] = div.currency
            dividends_by_year_currency[key]['gross'] += div.amount
            dividends_by_year_currency[key]['withholding'] += div.withholding
            dividends_by_year_currency[key]['net'] += div.net_amount
            report['dividends'].append({
                'symbol': div.symbol,
                'date': div.date.isoformat(),
                'currency': div.currency,
                'amount': str(div.amount),
                'withholding': str(div.withholding),
                'net_amount': str(div.net_amount)
            })

        for wh in self._withholdings:
            date_str = wh.get('Date', '')
            amount = wh.get('Amount')
            if isinstance(amount, str):
                amount = Decimal(amount.replace(',', ''))
            report['withholdings'].append({
                'date': date_str,
                'description': wh.get('Description', ''),
                'amount': str(amount) if amount else '0'
            })

        for (year, currency), gains in gains_by_year_currency.items():
            total = gains['short_term'] + gains['long_term']
            if str(year) not in report['summary']:
                report['summary'][str(year)] = {}
            report['summary'][str(year)][currency] = {
                'short_term_gain': str(gains['short_term']),
                'long_term_gain': str(gains['long_term']),
                'total_gain': str(total),
                'currency': currency
            }

        for (year, currency), divs in dividends_by_year_currency.items():
            if str(year) not in report['summary']:
                report['summary'][str(year)] = {}
            report['summary'][str(year)][currency] = report['summary'][str(year)].get(currency, {
                'short_term_gain': '0',
                'long_term_gain': '0',
                'total_gain': '0',
                'currency': currency
            })
            report['summary'][str(year)][currency]['dividend_gross'] = str(divs['gross'])
            report['summary'][str(year)][currency]['dividend_withholding'] = str(divs['withholding'])
            report['summary'][str(year)][currency]['dividend_net'] = str(divs['net'])

        return report

    def _find_purchase_date(self, symbol: str) -> datetime:
        lots = self._lots.get(symbol, [])
        if lots:
            return lots[0].date
        return datetime.now()

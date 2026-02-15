"""Parser for IBKR Activity Statement CSV (sectioned CSV as in provided example).
Returns structured lists for Trades, Dividends, and Withholding Tax.
This parser keeps amounts in their native currencies (no conversion).
"""
from __future__ import annotations

import csv
from datetime import datetime
from decimal import Decimal
from typing import Any

from src.data_loader import DataLoader


def _to_decimal(s: str | None) -> Decimal | str | None:
    if s is None:
        return None
    s = str(s).strip()
    if s == '':
        return None
    s = s.replace(',', '')
    try:
        return Decimal(s)
    except Exception:
        return s


class IBKRDataLoader(DataLoader):
    def load(self, csv_path: str) -> dict[str, list[dict[str, Any]]]:
        """Parse the IBKR activity CSV and extract trades, dividends, withholding, and forex rows.

        Returns a dict with keys 'trades','dividends','withholdings','forex_rows'.
        Numeric fields are parsed to Decimal where possible; Date/Time parsed to datetime.
        """
        trades: list[dict[str, Any]] = []
        dividends: list[dict[str, Any]] = []
        withholdings: list[dict[str, Any]] = []
        forex_rows: list[dict[str, Any]] = []

        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            section: str | None = None
            header: list[str] | None = None
            for row in reader:
                if not row:
                    continue
                first = row[0].strip() if len(row) > 0 else ''
                second = row[1].strip() if len(row) > 1 else ''

                if first and second == 'Header':
                    section = first
                    header = [h.strip() for h in row[2:]]
                    continue

                if first and second in ('Data',):
                    values = row[2:]
                    if header is None:
                        continue
                    while len(values) < len(header):
                        values.append('')
                    item: dict[str, Any] = {h: v.strip() for h, v in zip(header, values)}

                    if section == 'Trades':
                        if 'Quantity' in item:
                            q = item.get('Quantity', '')
                            q = str(q).replace(',', '')
                            try:
                                item['Quantity'] = Decimal(q)
                            except Exception:
                                item['Quantity'] = None
                        for k in ('T. Price', 'Proceeds', 'Comm/Fee', 'Basis', 'Realized P/L'):
                            if k in item:
                                item[k] = _to_decimal(item.get(k))
                        dt_raw = item.get('Date/Time') or item.get('Date/Time ')
                        if dt_raw:
                            try:
                                item['DateTime'] = datetime.strptime(dt_raw, '%Y-%m-%d, %H:%M:%S')
                            except Exception:
                                try:
                                    item['DateTime'] = datetime.strptime(dt_raw, '%Y-%m-%d %H:%M:%S')
                                except Exception:
                                    item['DateTime'] = None
                        trades.append(item)

                    elif section == 'Dividends':
                        d: dict[str, Any] = {
                            'Currency': item.get('Currency'),
                            'Date': item.get('Date'),
                            'Description': item.get('Description'),
                            'Amount': _to_decimal(item.get('Amount'))
                        }
                        dividends.append(d)

                    elif section == 'Withholding Tax':
                        w: dict[str, Any] = {
                            'Currency': item.get('Currency'),
                            'Date': item.get('Date'),
                            'Description': item.get('Description'),
                            'Amount': _to_decimal(item.get('Amount'))
                        }
                        withholdings.append(w)

                    elif section == 'Forex Balances':
                        forex_rows.append(item)

        return {
            'trades': trades,
            'dividends': dividends,
            'withholdings': withholdings,
            'forex_rows': forex_rows,
        }


def parse_ibkr_activity(csv_path: str) -> dict[str, list[dict[str, Any]]]:
    """Parse the IBKR activity CSV. Deprecated, use IBKRDataLoader instead."""
    loader = IBKRDataLoader()
    return loader.load(csv_path)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('Usage: python -m src.ibkr_parser <activity_csv>')
    else:
        loader = IBKRDataLoader()
        out = loader.load(sys.argv[1])
        print(
            'Parsed: trades=%d, dividends=%d, withholdings=%d, forex_rows=%d' % (
                len(out['trades']), len(out['dividends']), len(out['withholdings']), len(out['forex_rows'])
            )
        )

"""
Parser for IBKR Activity Statement CSV (sectioned CSV as in provided example).
Returns structured lists for Trades, Dividends, and Withholding Tax.
This parser keeps amounts in their native currencies (no conversion).
"""
import csv
from datetime import datetime
from decimal import Decimal

def _to_decimal(s):
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

def parse_ibkr_activity(csv_path):
    """Parse the IBKR activity CSV and extract trades, dividends, withholding, and forex rows.

    Returns a dict:
      {
        'trades': [ {..}, ... ],
        'dividends': [ {..}, ... ],
        'withholdings': [ {..}, ... ],
        'forex_rows': [ {..}, ... ]
      }

    Notes:
    - Fields are kept as strings or Decimal for numeric fields.
    - Quantity is Decimal (positive for buy, negative for sell per IBKR).
    - T. Price, Proceeds, Comm/Fee, Basis, Realized P/L parsed to Decimal when possible.
    - Date/Time parsed to datetime when possible and stored as 'DateTime'.
    """
    trades = []
    dividends = []
    withholdings = []
    forex_rows = []

    with open(csv_path, newline='') as f:
        reader = csv.reader(f)
        section = None
        header = None
        for row in reader:
            if not row:
                continue
            first = row[0].strip() if len(row) > 0 else ''
            second = row[1].strip() if len(row) > 1 else ''

            # Section header detection: e.g. 'Trades,Header,...'
            if first and second == 'Header':
                section = first
                header = [h.strip() for h in row[2:]]
                continue

            # Data rows: second column usually 'Data' or 'SubTotal'
            if first and second in ('Data', 'SubTotal', 'SubTotal,', 'SubTotal,,'):
                values = row[2:]
                # normalize values length to header
                if header is None:
                    continue
                while len(values) < len(header):
                    values.append('')
                item = {h: v.strip() for h, v in zip(header, values)}

                if section == 'Trades':
                    # parse numeric fields
                    if 'Quantity' in item:
                        q = item.get('Quantity', '')
                        q = q.replace(',', '')
                        try:
                            item['Quantity'] = Decimal(q)
                        except Exception:
                            item['Quantity'] = None
                    for k in ('T. Price', 'Proceeds', 'Comm/Fee', 'Basis', 'Realized P/L'):
                        if k in item:
                            val = item.get(k)
                            item[k] = _to_decimal(val)
                    # parse Date/Time
                    dt_raw = item.get('Date/Time') or item.get('Date/Time ')
                    if dt_raw:
                        # Expected format in sample: "2026-01-20, 21:43:42"
                        try:
                            item['DateTime'] = datetime.strptime(dt_raw, '%Y-%m-%d, %H:%M:%S')
                        except Exception:
                            # fallback: try other common formats
                            try:
                                item['DateTime'] = datetime.strptime(dt_raw, '%Y-%m-%d %H:%M:%S')
                            except Exception:
                                item['DateTime'] = None
                    trades.append(item)

                elif section == 'Dividends':
                    d = {
                        'Currency': item.get('Currency'),
                        'Date': item.get('Date'),
                        'Description': item.get('Description'),
                        'Amount': _to_decimal(item.get('Amount'))
                    }
                    dividends.append(d)

                elif section == 'Withholding Tax':
                    w = {
                        'Currency': item.get('Currency'),
                        'Date': item.get('Date'),
                        'Description': item.get('Description'),
                        'Amount': _to_decimal(item.get('Amount'))
                    }
                    withholdings.append(w)

                elif section == 'Forex Balances':
                    # keep the raw row for possible later use
                    forex_rows.append(item)

                # other sections ignored for now
    return {
        'trades': trades,
        'dividends': dividends,
        'withholdings': withholdings,
        'forex_rows': forex_rows,
    }

# If run directly for a quick parse
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python -m src.ibkr_parser <activity_csv>')
    else:
        out = parse_ibkr_activity(sys.argv[1])
        print('Parsed: trades=%d, dividends=%d, withholdings=%d, forex_rows=%d' % (
            len(out['trades']), len(out['dividends']), len(out['withholdings']), len(out['forex_rows'])
        ))
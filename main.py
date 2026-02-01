#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from src.ibkr_parser import parse_ibkr_activity
from src.fifo_analyzer import FIFOAnalyzer
from src.report_generator import write_reports

def _serialize_unmatched(u):
    """Serialize unmatched sell entries for JSON output (convert Decimal/datetime to strings)."""
    from decimal import Decimal
    from datetime import datetime
    res = dict(u)
    for k, v in list(res.items()):
        if isinstance(v, Decimal):
            res[k] = str(v)
        if isinstance(v, datetime):
            res[k] = v.isoformat()
    return res

def run(csv_path, out_dir='outputs'):
    parsed = parse_ibkr_activity(csv_path)
    trades = parsed.get('trades', [])
    dividends = parsed.get('dividends', [])
    withholdings = parsed.get('withholdings', [])

    analyzer = FIFOAnalyzer()
    analyzer.ingest_trades(trades)
    analyzer.ingest_dividends(dividends)
    analyzer.ingest_withholdings(withholdings)

    report = analyzer.annual_report()
    out = write_reports(report, out_dir=out_dir)
    print('Reports written:', out)

    if analyzer.unmatched_sells:
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        unmatched_path = Path(out_dir) / 'unmatched_sells.json'
        with open(unmatched_path, 'w', encoding='utf-8') as f:
            json.dump([_serialize_unmatched(u) for u in analyzer.unmatched_sells], f, ensure_ascii=False, indent=2)
        print(f'Warning: there are unmatched sell transactions. Details written to {unmatched_path}')

def main():
    parser = argparse.ArgumentParser(description='Run FIFO analysis on an IBKR activity CSV file.')
    parser.add_argument('csv', help='Path to the IBKR activity CSV file')
    parser.add_argument('-o', '--outdir', default='outputs', help='Output directory for reports (default: outputs)')
    args = parser.parse_args()
    run(args.csv, out_dir=args.outdir)

if __name__ == '__main__':
    main()
import csv
from pathlib import Path
from typing import Any


def generate_annual_income_report(year):
    pass


def _format_decimal(value: str) -> str:
    try:
        num = float(value)
        return f"{num:.2f}"
    except (ValueError, TypeError):
        return value


def write_reports(report: dict[str, Any], out_dir: str = 'outputs') -> dict[str, str]:
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    result = {}

    realized_gains = report.get('realized_gains', [])
    if realized_gains:
        gains_path = Path(out_dir) / 'realized_gains.csv'
        with open(gains_path, 'w', encoding='utf-8', newline='') as f:
            if realized_gains:
                fieldnames = ['symbol', 'quantity', 'sell_date', 'proceeds', 'cost_basis', 'gain_loss']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in realized_gains:
                    writer.writerow({
                        'symbol': row.get('symbol', ''),
                        'quantity': row.get('quantity', ''),
                        'sell_date': row.get('sell_date', ''),
                        'proceeds': _format_decimal(row.get('proceeds', '0')),
                        'cost_basis': _format_decimal(row.get('cost_basis', '0')),
                        'gain_loss': _format_decimal(row.get('gain_loss', '0'))
                    })
        result['realized_gains'] = str(gains_path)

    dividends = report.get('dividends', [])
    if dividends:
        div_path = Path(out_dir) / 'dividends.csv'
        with open(div_path, 'w', encoding='utf-8', newline='') as f:
            if dividends:
                fieldnames = ['symbol', 'date', 'currency', 'amount']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in dividends:
                    writer.writerow({
                        'symbol': row.get('symbol', ''),
                        'date': row.get('date', ''),
                        'currency': row.get('currency', ''),
                        'amount': _format_decimal(row.get('amount', '0'))
                    })
        result['dividends'] = str(div_path)

    withholdings = report.get('withholdings', [])
    if withholdings:
        wh_path = Path(out_dir) / 'withholdings.csv'
        with open(wh_path, 'w', encoding='utf-8', newline='') as f:
            if withholdings:
                fieldnames = ['date', 'description', 'amount']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in withholdings:
                    writer.writerow({
                        'date': row.get('date', ''),
                        'description': row.get('description', ''),
                        'amount': _format_decimal(row.get('amount', '0'))
                    })
        result['withholdings'] = str(wh_path)

    summary = report.get('summary', {})
    if summary:
        summary_path = Path(out_dir) / 'summary.csv'
        with open(summary_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['year', 'short_term_gain', 'long_term_gain', 'total_gain']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for year, data in sorted(summary.items()):
                writer.writerow({
                    'year': year,
                    'short_term_gain': _format_decimal(data.get('short_term_gain', '0')),
                    'long_term_gain': _format_decimal(data.get('long_term_gain', '0')),
                    'total_gain': _format_decimal(data.get('total_gain', '0'))
                })
        result['summary'] = str(summary_path)

    return result


if __name__ == '__main__':
    year_to_generate = 2026
    generate_annual_income_report(year_to_generate)

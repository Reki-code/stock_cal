import datetime
import json
from pathlib import Path
from typing import Any


def generate_annual_income_report(year):
    pass


def write_reports(report: dict[str, Any], out_dir: str = 'outputs') -> dict[str, str]:
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    result = {}

    realized_gains = report.get('realized_gains', [])
    if realized_gains:
        gains_path = Path(out_dir) / 'realized_gains.json'
        with open(gains_path, 'w', encoding='utf-8') as f:
            json.dump(realized_gains, f, ensure_ascii=False, indent=2)
        result['realized_gains'] = str(gains_path)

    dividends = report.get('dividends', [])
    if dividends:
        div_path = Path(out_dir) / 'dividends.json'
        with open(div_path, 'w', encoding='utf-8') as f:
            json.dump(dividends, f, ensure_ascii=False, indent=2)
        result['dividends'] = str(div_path)

    withholdings = report.get('withholdings', [])
    if withholdings:
        wh_path = Path(out_dir) / 'withholdings.json'
        with open(wh_path, 'w', encoding='utf-8') as f:
            json.dump(withholdings, f, ensure_ascii=False, indent=2)
        result['withholdings'] = str(wh_path)

    summary = report.get('summary', {})
    if summary:
        summary_path = Path(out_dir) / 'summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        result['summary'] = str(summary_path)

    return result


if __name__ == '__main__':
    year_to_generate = 2026
    generate_annual_income_report(year_to_generate)
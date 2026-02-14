import pytest
from decimal import Decimal
from datetime import datetime
from src.fifo_analyzer import FIFOAnalyzer, Lot, SellMatch, DividendRecord


class TestFIFOAnalyzer:
    def test_ingest_trades_basic(self):
        analyzer = FIFOAnalyzer()
        trades = [
            {
                'Asset Category': 'Stocks',
                'Symbol': 'AAPL',
                'Quantity': 10,
                'T. Price': Decimal('150.00'),
                'Comm/Fee': Decimal('-1.00'),
                'DateTime': datetime(2025, 1, 1)
            }
        ]
        analyzer.ingest_trades(trades)
        assert 'AAPL' in analyzer._lots
        assert len(analyzer._lots['AAPL']) == 1

    def test_buy_and_sell(self):
        analyzer = FIFOAnalyzer()
        trades = [
            {
                'Asset Category': 'Stocks',
                'Symbol': 'AAPL',
                'Quantity': 10,
                'T. Price': Decimal('100.00'),
                'Comm/Fee': Decimal('-1.00'),
                'DateTime': datetime(2025, 1, 1)
            },
            {
                'Asset Category': 'Stocks',
                'Symbol': 'AAPL',
                'Quantity': -5,
                'T. Price': Decimal('120.00'),
                'Comm/Fee': Decimal('-1.00'),
                'DateTime': datetime(2025, 6, 1),
                'Currency': 'USD'
            }
        ]
        analyzer.ingest_trades(trades)
        report = analyzer.annual_report()

        assert len(report['realized_gains']) == 1
        gain = report['realized_gains'][0]
        assert gain['symbol'] == 'AAPL'
        assert gain['currency'] == 'USD'

    def test_ingest_dividends(self):
        analyzer = FIFOAnalyzer()
        dividends = [
            {
                'Date': '2025-12-15',
                'Currency': 'USD',
                'Description': 'AAPL Dividend',
                'Amount': '1.00'
            }
        ]
        analyzer.ingest_dividends(dividends)
        assert len(analyzer._dividends) == 1
        assert analyzer._dividends[0].symbol == 'AAPL'

    def test_annual_report_by_currency(self):
        analyzer = FIFOAnalyzer()
        trades = [
            {
                'Asset Category': 'Stocks',
                'Symbol': 'AAPL',
                'Quantity': 10,
                'T. Price': Decimal('100.00'),
                'Comm/Fee': Decimal('-1.00'),
                'DateTime': datetime(2025, 1, 1),
                'Currency': 'USD'
            },
            {
                'Asset Category': 'Stocks',
                'Symbol': '0700.HK',
                'Quantity': 100,
                'T. Price': Decimal('300.00'),
                'Comm/Fee': Decimal('-10.00'),
                'DateTime': datetime(2025, 2, 1),
                'Currency': 'HKD'
            },
            {
                'Asset Category': 'Stocks',
                'Symbol': 'AAPL',
                'Quantity': -5,
                'T. Price': Decimal('120.00'),
                'Comm/Fee': Decimal('-1.00'),
                'DateTime': datetime(2025, 6, 1),
                'Currency': 'USD'
            },
            {
                'Asset Category': 'Stocks',
                'Symbol': '0700.HK',
                'Quantity': -50,
                'T. Price': Decimal('350.00'),
                'Comm/Fee': Decimal('-10.00'),
                'DateTime': datetime(2025, 7, 1),
                'Currency': 'HKD'
            }
        ]
        analyzer.ingest_trades(trades)
        report = analyzer.annual_report()

        assert '2025' in report['summary']
        assert 'USD' in report['summary']['2025']
        assert 'HKD' in report['summary']['2025']

    def test_dividend_with_withholding(self):
        analyzer = FIFOAnalyzer()
        withholdings = [
            {
                'Date': '2025-12-15',
                'Description': 'AAPL Dividend',
                'Amount': '-0.15'
            }
        ]
        dividends = [
            {
                'Date': '2025-12-15',
                'Currency': 'USD',
                'Description': 'AAPL Dividend',
                'Amount': '1.00'
            }
        ]
        analyzer.ingest_withholdings(withholdings)
        analyzer.ingest_dividends(dividends)

        assert len(analyzer._dividends) == 1
        div = analyzer._dividends[0]
        assert div.amount == Decimal('1.00')
        assert div.withholding == Decimal('-0.15')
        assert div.net_amount == Decimal('0.85')


class TestLot:
    def test_lot_creation(self):
        lot = Lot(
            symbol='AAPL',
            quantity=Decimal('10'),
            price=Decimal('100.00'),
            date=datetime(2025, 1, 1),
            commission=Decimal('1.00')
        )
        assert lot.symbol == 'AAPL'
        assert lot.quantity == Decimal('10')


class TestDividendRecord:
    def test_dividend_record_creation(self):
        div = DividendRecord(
            date=datetime(2025, 12, 15),
            symbol='AAPL',
            currency='USD',
            amount=Decimal('1.00'),
            withholding=Decimal('-0.15'),
            net_amount=Decimal('0.85')
        )
        assert div.symbol == 'AAPL'
        assert div.currency == 'USD'

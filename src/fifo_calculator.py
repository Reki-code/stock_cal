# FIFO Calculator

"""
This script calculates the cost basis using the First-In, First-Out (FIFO) method.
"""

class FIFOCalculator:
    def __init__(self):
        self.transactions = []

    def add_transaction(self, quantity, price_per_unit):
        self.transactions.append((quantity, price_per_unit))

    def calculate_cost_basis(self, quantity_to_sell):
        total_cost = 0
        quantity_sold = 0

        for quantity, price in self.transactions:
            if quantity_sold >= quantity_to_sell:
                break
            if quantity + quantity_sold > quantity_to_sell:
                total_cost += (quantity_to_sell - quantity_sold) * price
                quantity_sold = quantity_to_sell
            else:
                total_cost += quantity * price
                quantity_sold += quantity

        return total_cost

# Example usage:
# calculator = FIFOCalculator()
# calculator.add_transaction(10, 5.0)  # bought 10 at $5 each
# calculator.add_transaction(5, 6.0)   # bought 5 at $6 each
# cost_basis = calculator.calculate_cost_basis(7)
# print(cost_basis)  # this would show the cost basis for selling 7 units

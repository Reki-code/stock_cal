def calculate_capital_gains_tax(purchase_price, selling_price, shares):
    """
    Calculate the capital gains tax based on purchase price, selling price, and number of shares.
    """
    gain = (selling_price - purchase_price) * shares
    if gain > 0:
        tax = gain * 0.15  # Assuming a 15% capital gains tax rate
    else:
        tax = 0
    return tax


def calculate_dividend_tax(dividend_amount, shares):
    """
    Calculate the dividend tax based on the dividend amount for a given number of shares.
    """
    total_dividend = dividend_amount * shares
    tax = total_dividend * 0.1  # Assuming a 10% dividend tax rate
    return tax


# Example usage:
if __name__ == '__main__':
    print(calculate_capital_gains_tax(10, 15, 100))  # Example capital gains tax
    print(calculate_dividend_tax(2, 50))              # Example dividend tax

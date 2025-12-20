def predict_savings(income, expenses):
    """
    income: float (monthly income)
    expenses: list of floats (expense amounts)
    """

    total_expense = sum(expenses)

    savings = income - total_expense

    # Health score logic (simple + realistic)
    if income <= 0:
        health_score = 0
    else:
        savings_rate = savings / income

        if savings_rate >= 0.4:
            health_score = 90
        elif savings_rate >= 0.3:
            health_score = 80
        elif savings_rate >= 0.2:
            health_score = 70
        elif savings_rate >= 0.1:
            health_score = 60
        else:
            health_score = 40

    return round(savings, 2), health_score

import statistics

def detect_anomalies(expenses):
    alerts = []

    if len(expenses) < 3:
        return alerts

    amounts = [e.amount for e in expenses]
    mean = statistics.mean(amounts)
    std = statistics.stdev(amounts)

    for e in expenses:
        if e.amount > mean + 2 * std:
            alerts.append(
                f"⚠️ Unusual expense detected: ₹{e.amount} (Avg: ₹{round(mean,2)})"
            )

    return alerts


def generate_tips(expenses, income):
    tips = []

    if not expenses or not income:
        return tips

    total_spent = sum(e.amount for e in expenses)
    savings = income - total_spent
    savings_rate = savings / income if income > 0 else 0

    if savings_rate < 0.2:
        tips.append("💡 Your savings rate is below 20%. Try reducing non-essential expenses.")

    category_spend = {}
    for e in expenses:
        category_spend[e.category] = category_spend.get(e.category, 0) + e.amount

    for cat, amt in category_spend.items():
        if amt > total_spent * 0.4:
            tips.append(f"📊 You are spending heavily on {cat}. Consider setting a stricter budget.")

    if not tips:
        tips.append("✅ Your spending looks balanced. Keep it up!")

    return tips

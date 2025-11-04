from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from item.models import Item, Category
from django.db.models import Sum, Count
import matplotlib.pyplot as plt
import io
import urllib, base64
from datetime import datetime, timedelta


def generate_chart(fig):
    """Converts Matplotlib figure to base64 string for embedding in HTML."""
    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    buf.close()
    return uri


@login_required
@user_passes_test(lambda u: u.is_staff)
def analytics_dashboard(request):
    # Basic stats
    total_users = User.objects.count()
    total_staff = User.objects.filter(is_staff=True).count()
    total_customers = total_users - total_staff
    total_items = Item.objects.count()
    sold_items = Item.objects.filter(is_sold=True).count()
    unsold_items = total_items - sold_items
    total_revenue = Item.objects.filter(is_sold=True).aggregate(total=Sum('price'))['total'] or 0

    # User Registrations Chart
    today = datetime.today()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    date_labels = [d.strftime('%b %d') for d in dates]
    user_counts = [User.objects.filter(date_joined__date=d.date()).count() for d in dates]

    plt.switch_backend('AGG')
    fig1, ax1 = plt.subplots(figsize=(5, 3))
    ax1.plot(date_labels, user_counts, marker='o', color='teal')
    ax1.set_title('User Registrations (Last 7 Days)')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Users')
    chart_user_registrations = generate_chart(fig1)

    # Sales by Category Chart
    category_sales = (
        Item.objects.filter(is_sold=True)
        .values('category__name')
        .annotate(total_sales=Count('id'), revenue=Sum('price'))
        .order_by('-revenue')
    )

    fig2, ax2 = plt.subplots(figsize=(5, 3))
    if category_sales:
        categories = [c['category__name'] for c in category_sales]
        sales = [c['total_sales'] for c in category_sales]
        ax2.bar(categories, sales, color='blue')
        ax2.set_title('Sales by Category')
        ax2.set_xlabel('Category')
        ax2.set_ylabel('Items Sold')
        plt.xticks(rotation=30, ha='right')
    else:
        ax2.text(0.5, 0.5, 'No sales data yet', ha='center', va='center', fontsize=12)
    chart_category_sales = generate_chart(fig2)

    # Revenue Trend (Last 7 Days)
    revenue_trend = []
    for d in dates:
        daily_revenue = (
            Item.objects.filter(is_sold=True, created_at__date=d.date())
            .aggregate(total=Sum('price'))['total'] or 0
        )
        revenue_trend.append(daily_revenue)

    fig3, ax3 = plt.subplots(figsize=(5, 3))
    ax3.plot(date_labels, revenue_trend, marker='o', color='green')
    ax3.set_title('Revenue Trend (Last 7 Days)')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Revenue ($)')
    chart_revenue_trend = generate_chart(fig3)

    # Sold vs Unsold Pie Chart
    
    fig4, ax4 = plt.subplots(figsize=(4, 4))
    ax4.pie(
        [sold_items, unsold_items],
        labels=['Sold', 'Unsold'],
        autopct='%1.1f%%',
        colors=['#2ecc71', '#e74c3c']
    )
    ax4.set_title('Sold vs Unsold Items')
    chart_sold_unsold = generate_chart(fig4)

   
    # Context
    context = {
        'total_users': total_users,
        'total_staff': total_staff,
        'total_customers': total_customers,
        'total_items': total_items,
        'sold_items': sold_items,
        'unsold_items': unsold_items,
        'total_revenue': total_revenue,
        'chart_user_registrations': chart_user_registrations,
        'chart_category_sales': chart_category_sales,
        'chart_revenue_trend': chart_revenue_trend,
        'chart_sold_unsold': chart_sold_unsold,
    }

    return render(request, 'analytics/dashboard.html', context)

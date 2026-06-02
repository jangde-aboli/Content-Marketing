from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import connection
from .decorators import role_required



@login_required
def add_project_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        project_category = request.POST['project_category']
        domain_authority = request.POST['domain_authority']
        domain_rating = request.POST['domain_rating']
        geolocation = request.POST['geolocation']
        targets = request.POST['targets']
        
        # 🧠 Get the list of users from multiple select
        team_allocation_list = request.POST.getlist('team_allocation[]')
        team_allocation_str = ', '.join(team_allocation_list)  # Save as CSV string

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO add_new_project 
                (name, project_category, domain_authority, domain_rating, team_allocation, geolocation, targets)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [
                name, project_category, domain_authority,
                domain_rating, team_allocation_str,
                geolocation, targets
            ])
        return redirect('/dashboard/')

    # fetch all usernames for dropdown
    with connection.cursor() as cursor:
        cursor.execute("SELECT username FROM add_user")
        users = [row[0] for row in cursor.fetchall()]

    return render(request, 'add_project.html', {'users': users})




@login_required
def add_in_existing_project_view(request):
    if request.method == 'POST':
        price_value = request.POST.get('price')
        price_currency = request.POST.get('price_currency')

        # Convert to symbol form
        if price_currency == "INR":
            price = f"₹{price_value}" if price_value else None
        elif price_currency == "USD":
            price = f"${price_value}" if price_value else None
        else:
            price = price_value  # fallback

        data = {
            'username': request.POST.get('username'),
            'month': request.POST.get('month'),
            'project_name': request.POST.get('project_name'),
            'publication_site': request.POST.get('publication_site'),
            'keyword_1': request.POST.get('keyword_1'),
            'url_page_1': request.POST.get('url_page_1'),
            'keyword_2': request.POST.get('keyword_2'),
            'url_page_2': request.POST.get('url_page_2'),
            'live_url': request.POST.get('live_url'),
            'live_url_date': request.POST.get('live_url_date') or None,
            'status': request.POST.get('status'),
            'price': price,
            'invoice_number': request.POST.get('invoice_number'),
            'invoice_link': request.POST.get('invoice_link'),
            'blogger_name': request.POST.get('blogger_name'),
            'est_number': request.POST.get('est_number'),
            'billed_status': request.POST.get('billed_status'),
            'client_invoice_no': request.POST.get('client_invoice_no'),
            'collected_status': request.POST.get('collected_status'),
            'payment_status': request.POST.get('payment_status'),
            'released_date': request.POST.get('released_date') or None,
            'transaction_id': request.POST.get('transaction_id'),
        }

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO add_in_existing_project (
                    username, month, project_name, publication_site,
                    keyword_1, url_page_1, keyword_2, url_page_2,
                    live_url, live_url_date, status, price,
                    invoice_number, invoice_link, blogger_name,
                    est_number, billed_status, client_invoice_no,
                    collected_status, payment_status, released_date,
                    transaction_id
                )
                VALUES (
                    %(username)s, %(month)s, %(project_name)s, %(publication_site)s,
                    %(keyword_1)s, %(url_page_1)s, %(keyword_2)s, %(url_page_2)s,
                    %(live_url)s, %(live_url_date)s, %(status)s, %(price)s,
                    %(invoice_number)s, %(invoice_link)s, %(blogger_name)s,
                    %(est_number)s, %(billed_status)s, %(client_invoice_no)s,
                    %(collected_status)s, %(payment_status)s, %(released_date)s,
                    %(transaction_id)s
                )
            """, data)

        return redirect('/dashboard/')

    # Fetch usernames for dropdown
    with connection.cursor() as cursor:
        cursor.execute("SELECT username FROM add_user")
        users = [row[0] for row in cursor.fetchall()]

    # Fetch project names
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM add_new_project")
        project_names = [row[0] for row in cursor.fetchall()]

    return render(request, 'add_in_existing_project.html', {
        'users': users,
        'project_names': project_names
    })


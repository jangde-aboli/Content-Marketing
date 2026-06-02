from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from django.urls import path
from . import views
import requests
import openai

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def add_user_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email_id = request.POST.get('email_id')

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO add_user (username, email_id)
                VALUES (%s, %s)
            """, [username, email_id])

        return redirect('/dashboard/')

    return render(request, 'add_user.html')



@login_required
def user_dashboard_view(request):
    selected_user = request.GET.get('user', '')
    selected_project = request.GET.get('project', '')
    selected_month = request.GET.get('month', '')

    # --- Handle Edit/Update ---
    if request.method == "POST":
        row_id = request.POST.get("id")  # unique id column in add_in_existing_project

        updates = {
            'project_name': request.POST.get('project_name'),
            'publication_site': request.POST.get('publication_site'),
            'month': request.POST.get('month'),
            'keyword_1': request.POST.get('keyword_1'),
            'url_page_1': request.POST.get('url_page_1'),
            'keyword_2': request.POST.get('keyword_2'),
            'url_page_2': request.POST.get('url_page_2'),
            'status': request.POST.get('status'),
            'live_url': request.POST.get('live_url'),
            'live_url_date': request.POST.get('live_url_date') or None,
            'price': request.POST.get('price'),
            'invoice_number': request.POST.get('invoice_number'),
            'invoice_link': request.POST.get('invoice_link'),
            'blogger_name': request.POST.get('blogger_name'),
            'billed_status': request.POST.get('billed_status'),
            'client_invoice_no': request.POST.get('client_invoice_no'),
            'collected_status': request.POST.get('collected_status'),
            'payment_status': request.POST.get('payment_status'),
            'released_date': request.POST.get('released_date') or None,
            'transaction_id': request.POST.get('transaction_id'),
        }

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE add_in_existing_project
                SET project_name=%s, publication_site=%s, month=%s,
                    keyword_1=%s, url_page_1=%s,
                    keyword_2=%s, url_page_2=%s,
                    status=%s, live_url=%s, live_url_date=%s,
                    price=%s, invoice_number=%s, invoice_link=%s,
                    blogger_name=%s, billed_status=%s,
                    client_invoice_no=%s, collected_status=%s,
                    payment_status=%s, released_date=%s, transaction_id=%s
                WHERE id=%s
            """, [
                updates['project_name'], updates['publication_site'], updates['month'],
                updates['keyword_1'], updates['url_page_1'], updates['keyword_2'], updates['url_page_2'],
                updates['status'], updates['live_url'], updates['live_url_date'], updates['price'],
                updates['invoice_number'], updates['invoice_link'], updates['blogger_name'],
                updates['billed_status'], updates['client_invoice_no'], updates['collected_status'],
                updates['payment_status'], updates['released_date'], updates['transaction_id'],
                row_id
            ])

        return redirect('user-dashboard')  # reload after update

    # --- Fetch dropdown users ---
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT username FROM add_in_existing_project")
        users = [row[0] for row in cursor.fetchall()]

    if not selected_user and users:
        selected_user = users[0]

    # --- Fetch projects for selected user ---
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name
            FROM add_new_project
            WHERE %s = ANY (string_to_array(team_allocation, ','))
        """, [selected_user])
        project_names = [row[0] for row in cursor.fetchall()]

    if not project_names:
        return render(request, 'user_dashboard.html', {
            'users': users,
            'selected_user': selected_user,
            'projects': [],
            'selected_project': '',
            'months': [],
            'selected_month': '',
            'total_projects': 0,
            'allocated_links': 0,
            'live_links': 0,
            'pending_links': 0,
            'bar_chart_data': [],
            'table_data': [],
        })

    # --- Fetch distinct months for dropdown ---
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT month
            FROM add_in_existing_project
            WHERE project_name IN %s
            ORDER BY month
        """, [tuple(project_names)])
        months = [row[0] for row in cursor.fetchall() if row[0]]

    # --- Fetch chart data ---
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                project_name,
                COUNT(*) FILTER (WHERE status IS NOT NULL) AS allocated,
                COUNT(*) FILTER (WHERE status = 'Live') AS live,
                COUNT(*) FILTER (WHERE status = 'Pending') AS pending
            FROM add_in_existing_project
            WHERE project_name IN %s
            GROUP BY project_name
        """, [tuple(project_names)])
        bar_chart_data = cursor.fetchall()

    # --- Fetch table data ---
    where_clauses = ["project_name IN %s"]
    params = [tuple(project_names)]

    if selected_project:
        where_clauses.append("project_name = %s")
        params.append(selected_project)

    if selected_month:
        where_clauses.append("month = %s")
        params.append(selected_month)

    query = f"""
        SELECT id, project_name, publication_site, month, keyword_1, url_page_1, 
               keyword_2, url_page_2, status, live_url, live_url_date,
               price, invoice_number, invoice_link, blogger_name, 
               billed_status, client_invoice_no, collected_status, 
               payment_status, released_date, transaction_id
        FROM add_in_existing_project
        WHERE {" AND ".join(where_clauses)}
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        table_data = [
            dict(zip([col[0] for col in cursor.description], row))
            for row in cursor.fetchall()
        ]

    context = {
        'users': users,
        'selected_user': selected_user,
        'projects': project_names,
        'selected_project': selected_project,
        'months': months,
        'selected_month': selected_month,
        'total_projects': len(project_names),
        'allocated_links': sum(row[1] for row in bar_chart_data),
        'live_links': sum(row[2] for row in bar_chart_data),
        'pending_links': sum(row[3] for row in bar_chart_data),
        'bar_chart_data': bar_chart_data,
        'table_data': table_data,
    }

    return render(request, 'user_dashboard.html', context)




from django.shortcuts import render, redirect
from django.db import connection

def publication_list_view(request):
    # --- Handle Edit/Update ---
    if request.method == "POST":
        site_id = request.POST.get("id")

        updates = {
            'domain': request.POST.get('domain'),
            'category': request.POST.get('category'),
            'dr': request.POST.get('dr'),
            'da': request.POST.get('da'),
            'spam_score': request.POST.get('spam_score'),
            'similarweb_traffic': request.POST.get('similarweb_traffic'),
            'indian_traffic': request.POST.get('indian_traffic'),
            'country': request.POST.get('country'),
            'index_pages': request.POST.get('index_pages'),
            'hm_score': request.POST.get('hm_score'),
            'price': request.POST.get('price'),
            'link_type': request.POST.get('link_type'),
        }

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE publication_sites
                SET domain=%s, category=%s, dr=%s, da=%s, spam_score=%s,
                    similarweb_traffic=%s, indian_traffic=%s,
                    country=%s, index_pages=%s, hm_score=%s, price=%s, link_type=%s
                WHERE id=%s
            """, [
                updates['domain'], updates['category'], updates['dr'], updates['da'], updates['spam_score'],
                updates['similarweb_traffic'], updates['indian_traffic'],
                updates['country'], updates['index_pages'], updates['hm_score'], updates['price'],
                updates['link_type'], site_id
            ])

        return redirect("publication_list")  # reload after saving

    # --- Handle Filtering ---
    category_filter = request.GET.get("category", "")
    limit = int(request.GET.get("limit", 500))  # Default 500 rows

    query = "SELECT * FROM publication_sites"
    params = []

    if category_filter:
        query += " WHERE category = %s"
        params.append(category_filter)

    # Add ordering before limit
    query += " ORDER BY hm_score ASC"
    query += " LIMIT %s"
    params.append(limit)

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    # Updated columns list without traffic_graph
    columns = [
        'id', 'domain', 'category', 'dr', 'da', 'spam_score',
        'similarweb_traffic', 'indian_traffic', 'country',
        'index_pages', 'hm_score', 'price', 'link_type'
    ]
    sites = [dict(zip(columns, row)) for row in rows]

    # Get categories for filter dropdown
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT category FROM publication_sites")
        categories = [row[0] for row in cursor.fetchall() if row[0]]

    return render(request, "publication_list.html", {
        "sites": sites,
        "categories": categories,
        "selected_category": category_filter,
        "selected_limit": limit,
        "limit_options": [100, 200, 500]
    })




import requests
import base64

MOZ_ACCESS_ID = "mozscape-TPeXV2Topt"
MOZ_SECRET_KEY = "fLzurc3O2aQd7r3X1PvpSFNwdHXO4x1c"

def get_moz_metrics(domain):
    url = "https://lsapi.seomoz.com/v2/url_metrics"
    auth_str = f"{MOZ_ACCESS_ID}:{MOZ_SECRET_KEY}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json"
    }
    payload = {"targets": [domain]}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print("Moz raw response:", response.text)  # debug

        if response.status_code == 200:
            data = response.json()
            if data and "results" in data and len(data["results"]) > 0:
                metrics = data["results"][0]  # ✅ FIX HERE
                return {
                    "DA": metrics.get("domain_authority", "N/A"),
                    "PA": metrics.get("page_authority", "N/A"),
                    "Spam Score": metrics.get("spam_score", "N/A")
                }
        else:
            return {"DA": "Error", "PA": "Error", "Spam Score": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"DA": "Error", "PA": "Error", "Spam Score": f"API error: {e}"}




from openai import OpenAI

OPENAI_API_KEY = "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"
client = OpenAI(api_key=OPENAI_API_KEY)

def get_traffic_estimates(domain):
    try:
        prompt = (
            f"Source: Similarweb\n"
            f"Estimate the approximate monthly traffic (number only) "
            f"and Indian share percentage for the website: {domain}.\n"
            f"Respond ONLY as:\n"
            f"Monthly Traffic: <number only>\n"
            f"Indian Share: <percentage only>\n"
        )

        response = client.chat.completions.create(
            model="gpt-5-mini",   # fast + cheap, you can also use gpt-4.1 or gpt-5
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content.strip()
        print("OpenAI raw response:", content)  # 👈 debug

        monthly_traffic, indian_share = "N/A", "N/A"
        for line in content.split("\n"):
            if "Monthly Traffic:" in line:
                monthly_traffic = line.split("Monthly Traffic:")[1].strip()
            elif "Indian Share:" in line:
                indian_share = line.split("Indian Share:")[1].strip()

        return monthly_traffic, indian_share

    except Exception as e:
        print(f"OpenAI error: {e}")
        return "N/A", "N/A"


# Dashboard Django view 
def dashboard_view(request):
    from django.db import connection

    # ---------- Publication Sites ----------
    with connection.cursor() as cursor:
        cursor.execute("SELECT AVG(da) FROM publication_sites")
        avg_da = round(cursor.fetchone()[0] or 0, 2)

        cursor.execute("SELECT AVG(dr) FROM publication_sites")
        avg_dr = round(cursor.fetchone()[0] or 0, 2)

        cursor.execute("SELECT COUNT(domain) FROM publication_sites")
        total_sites = cursor.fetchone()[0] or 0

        # Get unique categories with their counts
        cursor.execute("""
            SELECT TRIM(category) AS clean_category, COUNT(*) AS cat_count
            FROM publication_sites
            WHERE category IS NOT NULL AND TRIM(category) != ''
            GROUP BY clean_category
            ORDER BY cat_count DESC
        """)
        cat_rows = cursor.fetchall()
        categories = [row[0] for row in cat_rows]
        category_counts = [row[1] for row in cat_rows]

    # ---------- User Allocations ----------
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT username, COUNT(*) AS allocations 
            FROM add_in_existing_project 
            GROUP BY username
        """)
        user_rows = cursor.fetchall()
        usernames = [row[0] for row in user_rows]
        user_counts = [row[1] for row in user_rows]

    # ---------- Domain Analysis ----------
    domain_result = None
    if request.method == "POST":
        domain = request.POST.get("domain", "")
        spam_score = get_moz_metrics(domain)
        monthly_traffic, indian_share = get_traffic_estimates(domain)

        domain_result = {
            "domain": domain,
            "spam_score": spam_score,
            "monthly_traffic": monthly_traffic,
            "indian_share": indian_share,
        }

    return render(request, "dashboard.html", {
        "avg_da": avg_da,
        "avg_dr": avg_dr,
        "total_sites": total_sites,
        "categories": categories,
        "category_counts": category_counts,
        "usernames": usernames,
        "user_counts": user_counts,
        "domain_result": domain_result,
    })




from django.shortcuts import render, redirect
from django.db import connections
from .models import Tag, RefTag
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import requests
from decimal import Decimal


# Create your views here.
def convert_decimal_to_float(data):
    return [
        tuple(float(item) if isinstance(item, Decimal) else item for item in row)
        for row in data
    ]


def index(request):
    data = []
    context = {}

    # Clear session data when the page is refreshed
    if request.method == "GET":
        request.session.pop("data", None)
        request.session.pop("search_keys", None)

    # Load session data if exists
    if "data" in request.session:
        data = request.session["data"]

    if request.method == "POST":
        date = request.POST.get("date")
        whouse = request.POST.get("whouse")
        part_no = request.POST.get("part_no")
        module_part = request.POST.get("module_part")

        # Define a unique search key for the new data set
        new_search_key = f"{whouse}_{module_part}_{date}"

        # Check if the search criteria already exists
        existing_search_keys = request.session.get("search_keys", [])

        if new_search_key not in existing_search_keys:
            # Call stored procedure only if new search criteria is not in session data
            try:
                with connections["itc_inwhouse"].cursor() as cursor:
                    query = """
                        EXEC Store_PrintTag_AC %s, %s, %s
                    """
                    cursor.execute(query, [whouse, module_part, date])
                    new_data = cursor.fetchall()
                    new_data = convert_decimal_to_float(
                        new_data
                    )  # Convert Decimal to float
                    data.extend(new_data)  # Append new data to existing data
                    context.update({"message": "ค้นหาข้อมูลสำเร็จ"})
            except Exception as e:
                context.update({"message": str(e)})

            # Add new search key to the session
            existing_search_keys.append(new_search_key)
            request.session["search_keys"] = existing_search_keys
            # Update session data
            request.session["data"] = data

        context.update(
            {
                "date": date,
                "selected_whouse": whouse,
                "part_no": part_no,
                "selected_module_part": module_part,
                "data": data,  # Pass data to template
            }
        )

    with connections["formula_vcst"].cursor() as cursor:
        whouse_query = """
            SELECT FCSKID, FCNAME FROM WHOUSE
        """
        cursor.execute(whouse_query)
        whouse_data = cursor.fetchall()

        module_part_query = """
            SELECT FCSKID, FCNAME FROM PDGRP
        """
        cursor.execute(module_part_query)
        module_part_data = cursor.fetchall()

    context.update(
        {
            "whouse_data": whouse_data,
            "module_part_data": module_part_data,
        }
    )

    return render(request, "home/index.html", context)


@csrf_exempt
def save_selected(request):
    if request.method == "POST":
        selected_indices = request.POST.getlist("selected")

        def print_tags(ref_tag, part_name):
            # URL สำหรับล็อกอิน
            login_url = "http://192.168.20.16:8080/jasperserver/rest_v2/login?j_username=jasperadmin&j_password=jasperadmin"
            login_response = requests.get(login_url)

            if login_response.status_code == 200:
                cookies = login_response.cookies

                # URL ของรายงาน
                report_url = f"http://192.168.20.16:8080/jasperserver/rest_v2/reports/ac_report/print_tag_acc.pdf?ParmID={ref_tag}"
                report_response = requests.get(report_url, cookies=cookies)

                if report_response.status_code == 200:
                    file_name = f"report_{part_name}"
                    response = HttpResponse(
                        report_response.content, content_type="application/pdf"
                    )
                    response["Content-Disposition"] = (
                        f'attachment; filename="{file_name}.pdf"'
                    )
                    return response
                else:
                    return HttpResponse(
                        "Failed to retrieve the report",
                        status=report_response.status_code,
                    )
            else:
                return HttpResponse(
                    "Login to JasperServer failed", status=login_response.status_code
                )

        # ตรวจสอบปุ่มที่ถูกกด
        if "print_tag_qty" in request.POST:
            ref_tag = RefTag.objects.create()

            for index in selected_indices:
                # seq = 0
                # for r in request.POST:
                #     print(f"{seq} ==> {r}")
                #     seq += 1

                index = int(index)
                part_no = request.POST.get(f"part_no_{index}")
                part_code = request.POST.get(f"part_code_{index}")
                part_name = request.POST.get(f"part_name_{index}")
                model_name = request.POST.get(f"model_name_{index}")
                stock_inout = request.POST.get(f"stock_inout_{index}")
                date = request.POST.get(f"date_{index}")
                whouse_code = request.POST.get(f"whouse_code_{index}")
                qr_code = f"{part_no}${stock_inout}"

                Tag.objects.create(
                    part_no=part_no,
                    part_code=part_code,
                    part_name=part_name,
                    model_name=model_name,
                    stock_inout=stock_inout,
                    date=date,
                    whouse_code=whouse_code,
                    qr_code=qr_code,
                    ref_tag=ref_tag,
                )
            return print_tags(ref_tag, part_name)

        if "print_tag_no_qty" in request.POST:
            ref_tag = RefTag.objects.create()

            for index in selected_indices:
                # seq = 0
                # for r in request.POST:
                #     print(f"{seq} ==> {r}")
                #     seq += 1

                index = int(index)
                part_no = request.POST.get(f"part_no_{index}")
                part_code = request.POST.get(f"part_code_{index}")
                part_name = request.POST.get(f"part_name_{index}")
                model_name = request.POST.get(f"model_name_{index}")
                date = request.POST.get(f"date_{index}")
                whouse_code = request.POST.get(f"whouse_code_{index}")
                qr_code = f"{part_no}"

                Tag.objects.create(
                    part_no=part_no,
                    part_code=part_code,
                    part_name=part_name,
                    model_name=model_name,
                    date=date,
                    whouse_code=whouse_code,
                    qr_code=qr_code,
                    ref_tag=ref_tag,
                )
            return print_tags(ref_tag, part_name)

        if "print_tag_blank" in request.POST:
            ref_tag = RefTag.objects.create()

            for i in range(0, 6):
                Tag.objects.create(
                    ref_tag=ref_tag,
                )
            return print_tags(ref_tag, "")

        return redirect("/")

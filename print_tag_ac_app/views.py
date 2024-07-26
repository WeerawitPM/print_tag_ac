from django.shortcuts import render, redirect
from django.db import connections
from .models import Tag, RefTag
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def index(request):
    data = []
    context = {}

    if request.method == "POST":
        date = request.POST.get("date")
        whouse = request.POST.get("whouse")
        part_no = request.POST.get("part_no")
        module_part = request.POST.get("module_part")

        # เรียก stored procedure
        with connections["itc_inwhouse"].cursor() as cursor:
            query = """
                EXEC Store_PrintTag_AC %s, %s, %s
            """
            cursor.execute(query, [whouse, module_part, date])
            data = cursor.fetchall()

        context.update(
            {
                "date": date,
                "selected_whouse": whouse,
                "part_no": part_no,
                "selected_module_part": module_part,
                "data": data,
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
                
            return redirect("/")

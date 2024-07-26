from django.shortcuts import render
from django.db import connections

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
                "data": data
            }
        )
        
        print(data)

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

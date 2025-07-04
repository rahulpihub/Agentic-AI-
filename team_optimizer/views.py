#views.py

import json
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .langgraph_flow import build_graph


@csrf_exempt
def generate_mou_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            graph = build_graph()
            result = graph.invoke(data)

            # Return both draft_text and the list of {clause_id,text}
            return JsonResponse({
                "result": {
                    "draft_text": result.get("draft_text", ""),
                    "retrieved_clauses": result.get("retrieved_clauses", []),
                    "emails_sent": result.get("emails_sent", []),
                    "approval_status": result.get("approval_status", {}), 
                    "overall_mou_status": result.get("overall_mou_status", ""),
                    "version_number": result.get("version_number", ""),
                    "version_diff": result.get("version_diff", "")
                }
            })

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)


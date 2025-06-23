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
            print("🚀 Incoming:", data)

            graph = build_graph()
            result = graph.invoke(data)

            print("✅ LangGraph Output:", result)
            return JsonResponse({"result": result.get("draft_text", "")})

        except Exception as e:
            print("❌ Error:", str(e))
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

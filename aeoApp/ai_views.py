# import google.generativeai as genai
# from django.conf import settings
# from django.utils import timezone
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response

# from .models import PromptHistory, BrandMentionMetric, BrandMentionTimeseries

# from .utils import detect_mentions  # your existing util


# genai.configure(api_key=settings.GEMINI_API_KEY)


# class AEOChatAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         prompt = request.data.get("prompt")

#         AEO_SYSTEM_PROMPT = """
# You are an AEO (Answer Engine Optimization) analysis assistant.

# STRICT RULES:
# - You MUST ONLY use the retrieved search facts provided.
# - You MUST NOT invent brands, websites, or tools.
# - If a brand is NOT in the retrieved data, DO NOT mention it.
# - Clearly distinguish the user's brand and competitors.
# - Be neutral and factual.
# - If the user's brand is not retrieved, say so clearly.

# Your job:
# 1. Answer the user query.
# 2. Mention brands ONLY if they appear in retrieved data.
# 3. Prefer concise, search-style answers.
# """

#         if not prompt:
#             return Response({"error": "Prompt is required"}, status=400)

#         brand_profile = user.brand_profile

#         # -------------------------------------
#         # 1️⃣ SEARCH-GROUNDED RETRIEVAL (FACTS)
#         # -------------------------------------
#         search_model = genai.GenerativeModel(model_name="gemini-2.5-flash")

#         search_response = search_model.generate_content(prompt)

#         retrieved_text = search_response.text or ""

#         grounding_metadata = getattr(
#             search_response.candidates[0], "grounding_metadata", None
#         )

#         source_type = "SEARCH"

#         # -------------------------------------
#         # 2️⃣ DETERMINISTIC BRAND DETECTION
#         # -------------------------------------
#         mentioned_brands, mentioned_domains = detect_mentions(
#             retrieved_text, brand_profile
#         )

#         # -------------------------------------
#         # 3️⃣ ANSWER GENERATION (ANTI-HALLUCINATION)
#         # -------------------------------------
#         answer_model = genai.GenerativeModel(model_name="gemini-2.5-flash")

#         competitor_data = [
#             {"brand": c.brand_name, "domain": c.domain_name}
#             for c in brand_profile.competitors.all()
#         ]

#         generation_prompt = f"""
# SYSTEM:
# {AEO_SYSTEM_PROMPT}

# USER QUERY:
# {prompt}

# RETRIEVED FACTS:
# {retrieved_text}

# USER BRAND:
# - Name: {brand_profile.brand_name}
# - Domain: {brand_profile.domain_name}

# COMPETITORS:
# {competitor_data}

# DETECTED MENTIONS:
# - Brands: {mentioned_brands}
# - Domains: {mentioned_domains}

# Now generate the final answer.
# """

#         final_response = answer_model.generate_content(generation_prompt)
#         ai_response = final_response.text or ""

#         # -------------------------------------
#         # 4️⃣ FINAL MENTION FLAGS
#         # -------------------------------------
#         user_brand_mentioned = brand_profile.brand_name in mentioned_brands
#         competitor_mentioned = any(
#             b != brand_profile.brand_name for b in mentioned_brands
#         )

#         # -------------------------------------
#         # 5️⃣ STORE PROMPT HISTORY
#         # -------------------------------------
#         prompt_entry = PromptHistory.objects.create(
#             brand_profile=brand_profile,
#             prompt=prompt,
#             ai_response=ai_response,
#             user_brand_mentioned=user_brand_mentioned,
#             competitor_mentioned=competitor_mentioned,
#             mentioned_brands=mentioned_brands,
#             mentioned_domains=mentioned_domains,
#             source_type=source_type,
#         )

#         # -------------------------------------
#         # 6️⃣ UPDATE METRICS + TIMESERIES
#         # -------------------------------------
#         today = timezone.now().date()

#         for brand in mentioned_brands:
#             metric, _ = BrandMentionMetric.objects.get_or_create(
#                 brand_profile=brand_profile, brand_name=brand
#             )
#             metric.total_mentions += 1
#             metric.last_mentioned_at = timezone.now()
#             metric.save()

#             ts, _ = BrandMentionTimeseries.objects.get_or_create(
#                 brand_profile=brand_profile, brand_name=brand, date=today
#             )
#             ts.mentions += 1
#             ts.save()

#         # -------------------------------------
#         # 7️⃣ RESPONSE TO FRONTEND
#         # -------------------------------------
#         return Response(
#             {
#                 "prompt": prompt,
#                 "answer": ai_response,
#                 "retrieved_brands": mentioned_brands,
#                 "retrieved_domains": mentioned_domains,
#                 "user_brand_mentioned": user_brand_mentioned,
#                 "competitor_mentioned": competitor_mentioned,
#                 "source_type": source_type,
#                 "created_at": prompt_entry.created_at,
#             }
#         )


import requests
from urllib.parse import urlparse
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import BrandProfile, PromptHistory, BrandMentionMetric, BrandMentionTimeseries
from .utils import normalize


def normalize_domain(domain: str) -> str:
    """
    Normalize domain for matching:
    - lowercase
    - remove 'www.'
    - remove trailing slashes
    """
    if not domain:
        return ""
    domain = domain.lower().strip()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain.rstrip("/")

def detect_mentions_from_serper(web_pages, brand_profile):
    """
    Detect brands and domains in Serper.dev results.
    Checks snippet, title, and domain from URL.
    Handles user brand and competitors.
    """
    mentioned_brands = set()
    mentioned_domains = set()

    # Combine snippet + title text
    combined_text = " ".join([f"{item.get('snippet','')} {item.get('title','')}" for item in web_pages])
    text_norm = normalize(combined_text)

    # Normalize user brand domain
    user_domain_norm = normalize_domain(brand_profile.domain_name)

    # Check user brand in text
    if normalize(brand_profile.brand_name) in text_norm:
        mentioned_brands.add(brand_profile.brand_name)

    # Check user domain in SERP URLs
    for item in web_pages:
        serp_domain = normalize_domain(urlparse(item.get("link", "")).netloc)
        if user_domain_norm and user_domain_norm in serp_domain:
            mentioned_domains.add(brand_profile.domain_name)
            mentioned_brands.add(brand_profile.brand_name)

    # Competitors
    for comp in brand_profile.competitors.all():
        comp_name_norm = normalize(comp.brand_name)
        comp_domain_norm = normalize_domain(comp.domain_name)

        # Check competitor name in text
        if comp_name_norm in text_norm:
            mentioned_brands.add(comp.brand_name)

        # Check competitor domain in SERP URLs
        for item in web_pages:
            serp_domain = normalize_domain(urlparse(item.get("link", "")).netloc)
            if comp_domain_norm and comp_domain_norm in serp_domain:
                mentioned_domains.add(comp.domain_name)
                mentioned_brands.add(comp.brand_name)

    return list(mentioned_brands), list(mentioned_domains)


class AEOChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        prompt = request.data.get("prompt")
        print(prompt)
        print(user)
        if not prompt:
            return Response({"error": "Prompt is required"}, status=400)

        try:
            brand_profile = user.brand_profile
        except BrandProfile.DoesNotExist:
            return Response({"error": "Brand profile not configured"}, status=400)

        # -----------------------------
        # SERP RETRIEVAL (SERPER.DEV)
        # -----------------------------
        headers = {"X-API-KEY": settings.SERPER_API_KEY, "Content-Type": "application/json"}
        payload = {"q": prompt}
        print(settings.SERPER_API_KEY)

        try:
            serp_response = requests.post(
                "https://google.serper.dev/search", headers=headers, json=payload, timeout=10
            )
            serp_response.raise_for_status()
        except requests.RequestException as e:
            return Response({"error": f"Search request failed: {str(e)}"}, status=502)

        data = serp_response.json()
        web_pages = data.get("organic", [])

        serp_results = []
        for idx, item in enumerate(web_pages, start=1):
            url = item.get("link", "")
            parsed = urlparse(url)
            serp_results.append({
                "rank": idx,
                "title": item.get("title"),
                "url": url,
                "snippet": item.get("snippet"),
                "domain": parsed.netloc or ""
            })

        # -----------------------------
        # BRAND DETECTION
        # -----------------------------
        mentioned_brands, mentioned_domains = detect_mentions_from_serper(web_pages, brand_profile)

        user_brand_mentioned = brand_profile.brand_name in mentioned_brands
        competitor_mentioned = any(b != brand_profile.brand_name for b in mentioned_brands)

        # -----------------------------
        # VISIBILITY SCORE
        # -----------------------------
        def calculate_visibility_score(domain):
            score = 0
            for r in serp_results:
                if r["url"] and domain.lower() in r["domain"].lower():
                    score += max(0, 12 - r["rank"])
            return score

        user_score = calculate_visibility_score(brand_profile.domain_name)
        competitor_scores = {c.brand_name: calculate_visibility_score(c.domain_name)
                             for c in brand_profile.competitors.all()}

        # -----------------------------
        # SIMULATED AI ANSWER
        # -----------------------------
        ai_response = (
            f"This answer is a simulation based on public search results.\n\nQuery: {prompt}\n\n"
            "Top sources commonly referenced include:\n"
        )
        for r in serp_results[:3]:
            ai_response += f"- {r['title']} ({r['domain']})\n"

        if user_brand_mentioned:
            ai_response += f"\n{brand_profile.brand_name} appears in search results."
        else:
            ai_response += f"\n{brand_profile.brand_name} does NOT appear prominently."

        source_type = "SEARCH"

        # -----------------------------
        # STORE PROMPT HISTORY
        # -----------------------------
        prompt_entry = PromptHistory.objects.create(
            brand_profile=brand_profile,
            prompt=prompt,
            ai_response=ai_response,
            user_brand_mentioned=user_brand_mentioned,
            competitor_mentioned=competitor_mentioned,
            mentioned_brands=mentioned_brands,
            mentioned_domains=mentioned_domains,
            source_type=source_type,
        )

        # -----------------------------
        # UPDATE METRICS + TIMESERIES
        # -----------------------------
        today = timezone.now().date()
        for brand_name in mentioned_brands:
            metric, _ = BrandMentionMetric.objects.get_or_create(
                brand_profile=brand_profile, brand_name=brand_name
            )
            metric.total_mentions += 1
            metric.last_mentioned_at = timezone.now()
            metric.save()

            ts, _ = BrandMentionTimeseries.objects.get_or_create(
                brand_profile=brand_profile, brand_name=brand_name, date=today
            )
            ts.mentions += 1
            ts.save()

        return Response({
            "prompt": prompt,
            "answer": ai_response,
            "serp_results": serp_results,
            "visibility_score": {"your_brand": user_score, "competitors": competitor_scores},
            "user_brand_mentioned": user_brand_mentioned,
            "mentioned_brands": mentioned_brands,
            "mentioned_domains": mentioned_domains,
            "source_type": source_type,
            "created_at": prompt_entry.created_at,
        })

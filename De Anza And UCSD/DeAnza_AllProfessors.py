# DeAnza_AllProfessors.py
# Purpose:
#   - Collect ALL professors for De Anza College from RateMyProfessors (all departments).
#   - Works without opening a browser: first read the first-page results embedded in HTML (Relay store),
#     then continue via GraphQL pagination until all records are fetched.
#   - For each professor, fetch their latest 5 reviews including ratings, comments, course info, and tags.
#   - Output fields are renamed and formatted per user request.

import re
import json
import time
import csv
from typing import Dict, Any, List, Tuple, Set
import requests

SEARCH_URL = "https://www.ratemyprofessors.com/search/professors/1967?q=*"
GQL_URL = "https://www.ratemyprofessors.com/graphql"

HEADERS = {
    "authority": "www.ratemyprofessors.com",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.ratemyprofessors.com",
    "referer": SEARCH_URL,
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    ),
}

# Base64 identifiers visible in the page / network:
SCHOOL_ID_B64 = "U2Nob29sLTE5Njc="     # "De Anza College"


# ---------------------------- Utility helpers ----------------------------

def balanced_json_after(marker: str, text: str) -> str:
    """
    Find a JSON object literal that immediately follows `marker` inside `text`.
    This handles nested braces and quoted strings to return the exact {...} slice.
    """
    start = text.find(marker)
    if start == -1:
        raise ValueError("marker not found")

    i = start + len(marker)
    # Skip whitespace and optional '='
    while i < len(text) and text[i] in " \t\r\n=":
        i += 1
    if i >= len(text) or text[i] != '{':
        raise ValueError("JSON does not start with '{' after marker")

    depth = 0
    j = i
    in_str = False
    esc = False
    while j < len(text):
        ch = text[j]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    j += 1  # include closing brace
                    break
        j += 1
    return text[i:j]


def extract_first_page_teachers_from_html(html: str) -> Tuple[List[Dict[str, Any]], str, bool]:
    """
    Parse first-page (SSR) data from window.__RELAY_STORE__ within the HTML.
    Returns:
        (teachers, end_cursor, has_next_page)
    `teachers` includes ALL teachers for De Anza College (no department filter).
    """
    marker = "window.__RELAY_STORE__ = "
    blob = balanced_json_after(marker, html)
    store = json.loads(blob)

    teachers = []
    for _, obj in store.items():
        if isinstance(obj, dict) and obj.get("__typename") == "Teacher":
            teachers.append({
                "id": obj.get("id"),                      # used only for de-duplication
                "legacyId": obj.get("legacyId"),          # not exported
                "firstName": obj.get("firstName"),
                "lastName": obj.get("lastName"),
                "department": obj.get("department"),
                "avgRating": obj.get("avgRating"),
                "numRatings": obj.get("numRatings"),
                "avgDifficulty": obj.get("avgDifficulty"),
                "wouldTakeAgainPercent": obj.get("wouldTakeAgainPercent"),
            })

    # Extract the pageInfo for subsequent GraphQL pagination
    end_cursor = None
    has_next = None
    for _, obj in store.items():
        if isinstance(obj, dict) and obj.get("__typename") == "PageInfo":
            end_cursor = obj.get("endCursor")
            has_next = obj.get("hasNextPage")
            break

    return teachers, end_cursor, bool(has_next)


def gql_req(session: requests.Session, variables: Dict[str, Any], query_str: str = None) -> Dict[str, Any]:
    """
    Submit a GraphQL request compatible with the site's pagination query.
    """
    if query_str is None:
        query_str = """
query TeacherSearchPaginationQuery($query: TeacherSearchQuery!, $first: Int!, $after: String) {
  newSearch {
    teachers(query: $query, first: $first, after: $after) {
      didFallback
      edges {
        cursor
        node {
          __typename
          ... on Teacher {
            id
            legacyId
            firstName
            lastName
            department
            avgRating
            numRatings
            avgDifficulty
            wouldTakeAgainPercent
          }
        }
      }
      pageInfo { hasNextPage endCursor }
      resultCount
    }
  }
}
"""
    payload = {
        "operationName": "TeacherSearchPaginationQuery",
        "variables": variables,
        "query": query_str,
    }
    r = session.post(GQL_URL, headers=HEADERS, data=json.dumps(payload))
    r.raise_for_status()
    return r.json()


def fetch_teacher_reviews(session: requests.Session, teacher_id: str, legacy_id: str = None, count: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch the latest reviews for a specific teacher.
    First tries GraphQL, then falls back to parsing HTML if needed.
    Returns a list of review dictionaries.
    """
    # Try GraphQL first
    query_str = """
query TeacherRatingsPageQuery($id: ID!) {
  node(id: $id) {
    ... on Teacher {
      id
      ratings(first: 5) {
        edges {
          node {
            id
            comment
            date
            helpfulRating
            clarityRating
            difficultyRating
            isForCredit
            isForOnlineClass
            wouldTakeAgain
            grade
            textbookUse
            attendanceMandatory
            class
          }
        }
      }
    }
  }
}
"""
    variables = {"id": teacher_id}
    
    try:
        payload = {
            "operationName": "TeacherRatingsPageQuery",
            "variables": variables,
            "query": query_str,
        }
        r = session.post(GQL_URL, headers=HEADERS, data=json.dumps(payload))
        r.raise_for_status()
        data = r.json()
        
        if data and "errors" not in data:
            teacher_node = data.get("data", {}).get("node", {})
            if teacher_node:
                ratings = teacher_node.get("ratings", {})
                edges = ratings.get("edges", []) or []
                
                reviews = []
                for edge in edges[:count]:
                    node = edge.get("node", {})
                    if node:
                        review = {
                            "comment": node.get("comment", ""),
                            "date": node.get("date", ""),
                            "qualityRating": node.get("clarityRating"),
                            "difficultyRating": node.get("difficultyRating"),
                            "isOnlineClass": node.get("isForOnlineClass", False),
                            "isForCredit": node.get("isForCredit"),
                            "wouldTakeAgain": node.get("wouldTakeAgain"),
                            "grade": node.get("grade", ""),
                            "textbookUse": node.get("textbookUse"),
                            "attendanceMandatory": node.get("attendanceMandatory"),
                            "class": node.get("class", ""),
                        }
                        reviews.append(review)
                
                if reviews:
                    return reviews
    except Exception:
        pass  # Fall through to try HTML parsing
    
    # Fallback: Try parsing from HTML if we have legacy_id
    if legacy_id:
        try:
            prof_url = f"https://www.ratemyprofessors.com/ShowRatings.jsp?tid={legacy_id}"
            html = session.get(prof_url, headers=HEADERS).text
            
            # Try to extract from Relay store
            marker = "window.__RELAY_STORE__ = "
            if marker in html:
                blob = balanced_json_after(marker, html)
                store = json.loads(blob)
                
                reviews = []
                for _, obj in store.items():
                    if isinstance(obj, dict) and obj.get("__typename") == "Rating":
                        if len(reviews) >= count:
                            break
                        review = {
                            "comment": obj.get("comment", ""),
                            "date": obj.get("date", ""),
                            "qualityRating": obj.get("clarityRating"),
                            "difficultyRating": obj.get("difficultyRating"),
                            "isOnlineClass": obj.get("isForOnlineClass", False),
                            "isForCredit": obj.get("isForCredit"),
                            "wouldTakeAgain": obj.get("wouldTakeAgain"),
                            "grade": obj.get("grade", ""),
                            "textbookUse": obj.get("textbookUse"),
                            "attendanceMandatory": obj.get("attendanceMandatory"),
                            "class": obj.get("class", ""),
                        }
                        reviews.append(review)
                
                if reviews:
                    return reviews
        except Exception:
            pass
    
    return []


def fetch_all(session: requests.Session, fetch_reviews: bool = True) -> List[Dict[str, Any]]:
    """
    Full flow:
      1) Load the first page HTML and parse Relay store for the initial Teacher nodes.
      2) Continue with GraphQL pagination using pageInfo until all data is fetched.
      3) Optionally fetch the latest 5 reviews for each professor.
    Returns a list of raw teacher dicts (internal field names) with reviews if requested.
    """
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    # Step 1: first-page (SSR) data
    print("Fetching initial page...")
    html = session.get(SEARCH_URL, headers=HEADERS).text
    first_batch, end_cursor, has_next = extract_first_page_teachers_from_html(html)

    for row in first_batch:
        if row["id"] and row["id"] not in seen:
            out.append(row)
            seen.add(row["id"])
    
    print(f"Initial batch: {len(first_batch)} professors")

    # Step 2: GraphQL pagination from the endCursor of first page
    # Note: No departmentID filter, only schoolID
    variables = {
        "query": {
            "text": "",
            "schoolID": SCHOOL_ID_B64,
            "fallback": True
        },
        "first": 20,
        "after": end_cursor
    }

    page_count = 1
    while has_next:
        try:
            data = gql_req(session, variables)
            teachers_root = (
                data.get("data", {})
                    .get("newSearch", {})
                    .get("teachers", {})
            )
            edges = teachers_root.get("edges", []) or []
            
            new_count = 0
            for e in edges:
                node = (e or {}).get("node", {})
                if node.get("__typename") == "Teacher":
                    tid = node.get("id")
                    if tid and tid not in seen:
                        out.append({
                            "id": tid,
                            "legacyId": node.get("legacyId"),
                            "firstName": node.get("firstName"),
                            "lastName": node.get("lastName"),
                            "department": node.get("department"),
                            "avgRating": node.get("avgRating"),
                            "numRatings": node.get("numRatings"),
                            "avgDifficulty": node.get("avgDifficulty"),
                            "wouldTakeAgainPercent": node.get("wouldTakeAgainPercent"),
                        })
                        seen.add(tid)
                        new_count += 1

            page_info = teachers_root.get("pageInfo", {}) or {}
            has_next = bool(page_info.get("hasNextPage"))
            variables["after"] = page_info.get("endCursor")
            
            page_count += 1
            print(f"Page {page_count}: +{new_count} professors (Total: {len(out)})")
            
            time.sleep(0.4)  # light pacing
            
        except Exception as e:
            print(f"Error on page {page_count}: {e}")
            time.sleep(2)  # longer wait on error
            continue

    # Step 3: Fetch reviews for each professor
    if fetch_reviews:
        print("\n" + "=" * 60)
        print("Fetching reviews for each professor...")
        print("=" * 60)
        total = len(out)
        for idx, teacher in enumerate(out, 1):
            teacher_id = teacher.get("id")
            legacy_id = teacher.get("legacyId")
            if teacher_id:
                name = f"{teacher.get('firstName', '')} {teacher.get('lastName', '')}".strip()
                print(f"[{idx}/{total}] Fetching reviews for {name}...", end=" ", flush=True)
                reviews = fetch_teacher_reviews(session, teacher_id, legacy_id=legacy_id, count=5)
                teacher["reviews"] = reviews
                print(f"[OK] {len(reviews)} reviews")
                time.sleep(0.5)  # Rate limiting between requests
            else:
                teacher["reviews"] = []

    return out


# ---------------------------- Export shaping ----------------------------

def fmt2(x):
    """Format numeric value to two decimal places; return empty string for None/invalid."""
    if x is None:
        return ""
    try:
        return f"{float(x):.2f}"
    except Exception:
        return ""


def to_export_rows(raw_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform raw rows to the final schema:
      - Drop `id` and `legacyId`
      - Merge firstName + lastName -> Full_Name
      - Rename fields to Capitalized_Snake_Case
      - Format numeric values to two decimals as strings
      - Include latest 5 reviews
    """
    export = []
    for r in raw_rows:
        full = f"{(r.get('firstName') or '').strip()} {(r.get('lastName') or '').strip()}".strip()
        
        # Format reviews
        reviews = r.get("reviews", [])
        formatted_reviews = []
        for rev in reviews:
            formatted_review = {
                "Comment": rev.get("comment", ""),
                "Date": rev.get("date", ""),
                "Quality_Rating": fmt2(rev.get("qualityRating")),
                "Difficulty_Rating": fmt2(rev.get("difficultyRating")),
                "Is_Online_Class": "Yes" if rev.get("isOnlineClass") else "No",
                "Is_For_Credit": "Yes" if rev.get("isForCredit") else "No",
                "Would_Take_Again": "Yes" if rev.get("wouldTakeAgain") else "No",
                "Grade": rev.get("grade", ""),
                "Textbook_Use": rev.get("textbookUse", ""),
                "Class": rev.get("class", ""),
            }
            formatted_reviews.append(formatted_review)
        
        export.append({
            "Full_Name": full,
            "Department": r.get("department"),
            "Average_Rating": fmt2(r.get("avgRating")),
            "Num_Ratings": r.get("numRatings") if r.get("numRatings") is not None else "",
            "Average_Difficulty": fmt2(r.get("avgDifficulty")),
            "Would_Take_Again_Percent": fmt2(r.get("wouldTakeAgainPercent")),
            "Latest_Reviews": formatted_reviews,
        })
    return export


def save(out_rows: List[Dict[str, Any]], prefix: str = "rmp_deanza_all_professors"):
    """Write both JSON and CSV with the required field names and formatting."""
    export_rows = to_export_rows(out_rows)

    # JSON - includes full review objects
    print(f"\nSaving {len(export_rows)} professors to {prefix}.json...")
    with open(f"{prefix}.json", "w", encoding="utf-8") as f:
        json.dump(export_rows, f, ensure_ascii=False, indent=2)

    # CSV - reviews stored as JSON strings for each review
    fields = [
        "Full_Name",
        "Department",
        "Average_Rating",
        "Num_Ratings",
        "Average_Difficulty",
        "Would_Take_Again_Percent",
        "Latest_Reviews",
    ]
    print(f"Saving {len(export_rows)} professors to {prefix}.csv...")
    with open(f"{prefix}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in export_rows:
            csv_row = {k: row.get(k, "") for k in fields}
            # Convert reviews list to JSON string for CSV
            if "Latest_Reviews" in csv_row and isinstance(csv_row["Latest_Reviews"], list):
                csv_row["Latest_Reviews"] = json.dumps(csv_row["Latest_Reviews"], ensure_ascii=False)
            w.writerow(csv_row)


def main():
    print("=" * 60)
    print("De Anza College - ALL Professors Scraper")
    print("(Including latest 5 reviews for each professor)")
    print("=" * 60)
    
    with requests.Session() as s:
        raw = fetch_all(s, fetch_reviews=True)
    
    print("\n" + "=" * 60)
    print(f"[RESULT] Total professors collected: {len(raw)}")
    total_reviews = sum(len(prof.get("reviews", [])) for prof in raw)
    print(f"[RESULT] Total reviews collected: {total_reviews}")
    print("=" * 60)
    
    save(raw)
    
    print("\n[SUCCESS] Data collection complete!")
    print(f"[INFO] Total: {len(raw)} professors")
    print(f"[INFO] Total reviews: {total_reviews}")


if __name__ == "__main__":
    main()


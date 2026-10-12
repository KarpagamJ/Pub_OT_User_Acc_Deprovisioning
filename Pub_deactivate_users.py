### deactivate_users.py

import pandas as pd
import requests
from datetime import datetime

# === CONFIGURATION ===
EXCEL_INPUT = "deactivation_template.xlsx"
API_BASE_URL = "https://host_name.onetrust.com/api/scim/v2/Users"
API_TOKEN = "Paste_your_token_here"

# === HEADERS ===
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

# === LOAD INPUT LIST ===
try:
    deactivation_list = pd.read_excel(EXCEL_INPUT)
    print(f" Loaded {len(deactivation_list)} records from {EXCEL_INPUT}")
except Exception as e:
    print(f" Failed to load input file: {e}")
    exit(1)

# === REMOVE DUPLICATES BY EMAIL ===
deactivation_list.drop_duplicates(subset=["Current Email Address"], inplace=True)
unique_emails = deactivation_list["Current Email Address"].dropna().unique()
print(f" Unique users to deactivate: {len(unique_emails)}")


# === FUNCTION TO FETCH USER ID BY EMAIL ===
def get_user_id_by_email(email):
    try:
        params = {"filter": f'emails.value eq "{email.strip()}"'}
        response = requests.get(API_BASE_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        resources = data.get("Resources", [])
        if resources:
            return resources[0]["id"]
    except Exception as e:
        print(f" Failed fetching user {email}: {e}")
    return None


# === DEACTIVATE USERS ===
results = []

for _, user in deactivation_list.iterrows():
    email = str(user.get("Current Email Address")).strip().lower()
    user_id = get_user_id_by_email(email)

    if user_id:
        payload = {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:PatchOp"],
            "Operations": [
                {"op": "replace", "path": "active", "value": False}
            ]
        }
        try:
            response = requests.patch(
                f"{API_BASE_URL}/{user_id}",
                headers=headers,
                json=payload,
                timeout=10
            )
            status_code = response.status_code
            response_json = response.json() if response.content else {"message": "No content"}
        except Exception as e:
            status_code = "Error"
            response_json = {"error": str(e)}
    else:
        status_code = 404
        response_json = {"error": "User not found in OneTrust"}

    results.append({
        "Email": email,
        "Status Code": status_code,
        "Response": response_json
    })


# === SAVE RESULTS ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"deactivation_results_{timestamp}.xlsx"
results_df = pd.DataFrame(results)
results_df.to_excel(output_file, index=False)

print(f" Deactivation results saved to {output_file}")
 
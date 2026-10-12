#User Account deactivation list creation
import pandas as pd
from datetime import datetime, timedelta

# Path to the exported user list from OneTrust
export_file_path = "your_file_path/user_export.csv"

# Load the exported CSV file
export_df = pd.read_csv(export_file_path)

# Deduplicate users based on email
unique_users = export_df.drop_duplicates(subset='Email').copy()

# Parse last login date and filter users inactive for 6+ months
six_months_ago = datetime.today() - timedelta(days=6*30)
unique_users['Last Login Date'] = pd.to_datetime(unique_users['Last Login Date'], errors='coerce', dayfirst=True)

# Filter out users from "Org_exclude" and "Country_exclude"
excluded_organizations = ["Org_exclude"]
excluded_locations = ['Country_exclude']

# Filtered users after excluding "Org_exclude" and "Country_exclude"
filtered_users = unique_users[~unique_users['Managed By'].str.contains('|'.join(excluded_locations), case=False, na=False) & ~unique_users['Managed By'].isin(excluded_organizations)]

# Filter inactive users (6+ months) and users with null login dates
inactive_users = filtered_users[
    ((filtered_users['Last Login Date'] <= six_months_ago) | filtered_users['Last Login Date'].isna())
]

# Create deactivation template
deactivation_template = pd.DataFrame({
    'Action': 'Deactivate',
    'Current Email Address': inactive_users['Email'],
    'New Email Address': '',
    'First Name': inactive_users['First Name'],
    'Last Name': inactive_users['Last Name'],
    'Current Organization': inactive_users['Managed By'],
    'Current Role': '',
    'New Organization': '',
    'New Role': '',
    'Managing Organization': '',
    'User Type': inactive_users['Internal/External'],
    'Expiration Date': inactive_users['Expiration Date'],
    'Department': inactive_users['Department'],
    'Business Unit': inactive_users['Business Unit'],
    'Employee Id': inactive_users['Employee Id'],
    'Manager': inactive_users['Manager'],
    'Division': inactive_users['Division'],
    'Job Title': inactive_users['Job Title'],
    'Office Location': inactive_users['Office Location']
})

# Save the deactivation template
output_path = "deactivation_template.xlsx"
deactivation_template.to_excel(output_path, index=False)

# Summary statistics
total_users = len(unique_users)
inactive_users_count = len(inactive_users)
null_login_users_count = filtered_users['Last Login Date'].isna().sum()
deactivation_users_count = len(deactivation_template)

print(f"Unique users after deduplication: {len(unique_users)}")
#print(f"Total users: {total_users}")
print(f"Inactive users (6+ months): {inactive_users_count}")
print(f"Users with no login: {null_login_users_count}")
print(f"Users to be deactivated: {deactivation_users_count}")
print(f"Deactivation template saved to {output_path}")
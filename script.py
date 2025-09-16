import json
import requests
import base64

# Pobieranie danych wejściowych
campaign_id = inputData['campaign_id']
user = inputData['user']
password = inputData['password']

original_phone_number = inputData['phone_number']
full_name = inputData['full_name']
company_name = inputData['company_name']
e_mail = inputData['email']
industry = inputData['industry']
campaign = f"FB: {inputData['campaign']}"
orign_date = inputData['data']
date = orign_date[:10]
orign_timedate = orign_date[-13:]
time = orign_timedate [:5]
note = f"Form z: {date} {time}"
api_sub = inputData['api_sub']

# Autoryzacja
credentials = f"{user}:{password}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

headers = {
    "Content-Type": "application/json;charset=utf-8",
    "Authorization": f"Basic {encoded_credentials}"
}

# 1. Companies API
print("Dodawanie firmy...")
companies_url = f"https://{api_sub}.thulium.com/api/companies"
company_data = {
    "name": company_name,
    "phone_number": original_phone_number,
    "email": e_mail,
    "note": f"{industry} {note}",
    "custom_fields": {
       "kampania": campaign
    }
}

companies_response = requests.post(companies_url, headers=headers, json=company_data)
print(f"Companies - Status code: {companies_response.status_code}")
print(companies_response.text)

# 2. Customers API
customer_id = None
if companies_response.status_code == 201:
    try:
        companies_data = companies_response.json()
        company_id = companies_data.get('company_id')
        
        if company_id:
            print(f"Otrzymano company_id: {company_id}")
            
            print("Dodawanie klienta z powiązaniem do firmy...")
            customers_url = f"https://{api_sub}.thulium.com/api/customers"
            customer_data = {
                "surname": full_name,
                "email": e_mail,
                "phone_number": [original_phone_number],
                "company_id": company_id,
                "note" : f"{industry} {note}",
                "custom_fields": {
                    "kampania": campaign
                }
            }
            
            customers_response = requests.post(customers_url, headers=headers, json=customer_data)
            print(f"Customers - Status code: {customers_response.status_code}")
            print(customers_response.text)
            
            # Pobranie customer_id z odpowiedzi Customers API
            if customers_response.status_code in [200, 201]:
                try:
                    customers_data = customers_response.json()
                    customer_id = customers_data.get('customer_id')
                    print(f"Otrzymano customer_id: {customer_id}")
                except json.JSONDecodeError:
                    print("Błąd: Nie można zdekodować odpowiedzi JSON z Customers API")
            else:
                print(f"Błąd Customers API. Status code: {customers_response.status_code}")
        else:
            print("Błąd: Nie otrzymano company_id w odpowiedzi")
            
    except json.JSONDecodeError:
        print("Błąd: Nie można zdekodować odpowiedzi JSON z Companies API")
else:
    print(f"Błąd Companies API - nie można kontynuować. Status code: {companies_response.status_code}")

# 3. CRM Outbounds API - dodawanie rekordu do kampanii z customer_id
if customer_id:
    print("Dodawanie rekordu do kampanii CRM...")
    crm_outbounds_url = f"https://{api_sub}.thulium.com/api/crm_outbounds/{campaign_id}/records"
    crm_record_data = {
        "customer_id": customer_id
    }
    
    crm_outbounds_response = requests.post(crm_outbounds_url, headers=headers, json=crm_record_data)
    print(f"CRM Outbounds - Status code: {crm_outbounds_response.status_code}")
    print(crm_outbounds_response.text)
else:
    print("Błąd: Nie można dodać rekordu do kampanii - brak customer_id")

from typing import Union
from django.shortcuts import render
from django.http import HttpResponse

from .models import Supplier, ScannedSupplier
from .enums import CompanyStatus
import requests
from bs4 import BeautifulSoup
from PIL import Image


def index(request):
    """
    Website homepage.
    """
    return render(request, 'index.html')


def update(request):
    """
    Scrap ACM webpage to retrieve new electricity suppliers and save them in database.
    """

    test = scan_supplier("ENGIE Nederland Retail B.V.")
    print(test.name)
    print(test.website)
    print(test.logo)
    # response = requests.get("https://www.acm.nl/nl/onderwerpen/energie/energiebedrijven/vergunningen/vergunninghouders-elektriciteit-en-gas#faq_81128")
    # soup = BeautifulSoup(response.text, 'html.parser')
    # table = soup.find('table', {'title': 'Register vergunninghouders elektriciteit kleinverbruik'})
    # table_body = table.find('tbody')
    # rows = table_body.find_all('tr')

    # for row in rows:
    #     cols = row.find_all('td')

    #     name = "Unknown"
    #     status = CompanyStatus.UNKNOWN

    #     for iteration, col in enumerate(cols):
    #         if not iteration:
    #             name = col.contents[0]
    #         else:
    #             last_status = col.find_all('a')[-1].contents[0]
    #             status = find_status(last_status)
        
    #     #Check if supplier already exists if not, save new supplier.
    #     if Supplier.objects.filter(name = name).exists() is False and name != "Unknown":
    #         Supplier.objects.create(name = name, status = status.name)

    return render(request, 'index.html')


def find_status(last_status) -> CompanyStatus:
    """
    Takes input from webscrapping and transforms string into CompanyStatus enum.
    """
    if "Verleend" in last_status:
        return CompanyStatus.GRANTED
    elif "Wijziging" in last_status:
        return CompanyStatus.NAME_CHANGE
    elif "Ingetrokken" in last_status:
        return CompanyStatus.REVOKED
    else:
        return CompanyStatus.UNKNOWN


def scan_supplier(name: str) -> Union[ScannedSupplier, None]:
    """

    """
    #Check if ScannedSupplier already exists if so, return.
    if ScannedSupplier.objects.filter(name = name).exists():
        return
    
    query_name = name

    if 'Eneco' in query_name:
        query_name = 'Eneco'

    if 'ENGIE' in query_name:
        query_name = 'Engie'

    if 'B.V.' in name:
        query_name = query_name.replace('B.V.', '')
    
    scanned_supplier = get_scanned_supplier(query_name)

    if scanned_supplier is None:
        query_name = query_name.replace('Energie', '')
    else:
        return scanned_supplier

    scanned_supplier = get_scanned_supplier(query_name)

    if scanned_supplier is None:
        query_name = query_name.replace(' ', '')
    else:
        return scanned_supplier
    
    scanned_supplier = get_scanned_supplier(query_name)

    if scanned_supplier is None:
        query_name = query_name + '.nl'
    else:
        return scanned_supplier
    
    scanned_supplier = get_scanned_supplier(query_name)

    if scanned_supplier is None:
        return None
    else:
        return scanned_supplier


def get_scanned_supplier(name: str) -> Union[ScannedSupplier, None]:

    url = "https://autocomplete.clearbit.com/v1/companies/suggest?query=" + name
    request = requests.get(url)

    if request.ok:
        response = request.json()
    else:
        return None
    
    #Nothing found.
    if len(response) == 0:
        return None

    if len(response) == 1:
        return create_scanned_supplier(response[0].get('logo'), response[0].get('name'), response[0].get('domain'))

    #More than one company found with this name.
    if len(response) > 1:
        for company in response:
            domain = company.get('domain')
            if ".nl" in domain:
                return create_scanned_supplier(company.get('logo'), company.get('name'), company.get('domain'))
            else:
                return None
    
   
def save_logo(logo_url: str, name: str):
    logo = Image.open(requests.get(logo_url, stream=True).raw)
    image_name = name.replace(' ', '')
    save_path = f'acm_app/images/{image_name}.png'
    logo.save(save_path, format="png")
    return save_path
    

def create_scanned_supplier(logo: str, name: str, domain: str): 
    save_path = save_logo(logo, name)
    return ScannedSupplier(name = name, logo = save_path, website = domain)

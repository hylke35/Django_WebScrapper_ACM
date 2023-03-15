from typing import Union
from django.shortcuts import render
from django.http import HttpResponse
from .models import Supplier, ScannedSupplier
from .enums import CompanyStatus
from bs4 import BeautifulSoup
from PIL import Image

import requests


def index(request):
    """
    Website homepage.
    """
    return render(request, 'index.html')


def update(request):
    """
    Scrap ACM webpage to retrieve new electricity suppliers and save them in database.
    """

    response = requests.get("https://www.acm.nl/nl/onderwerpen/energie/energiebedrijven/vergunningen/vergunninghouders-elektriciteit-en-gas#faq_81128")

    if not response.ok:
        return render(request, 'index.html', {'error' : 'ERROR: Unable to connect to ACM website'})
    
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'title': 'Register vergunninghouders elektriciteit kleinverbruik'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')

    for row in rows:
        cols = row.find_all('td')

        name = "Unknown"
        status = CompanyStatus.UNKNOWN

        for iteration, col in enumerate(cols):
            if not iteration:
                name = col.contents[0]
            else:
                last_status = col.find_all('a')[-1].contents[0]
                status = find_status(last_status)
        
            #Check if supplier already exists if not, save new supplier.
        if Supplier.objects.filter(name = name, status = status.name).exists() is False and name != "Unknown":
            if Supplier.objects.filter(name = name).exists():
                supplier_to_change = Supplier.objects.filter(name = name).first()
                supplier_to_change.status = status.name
                supplier_to_change.save()
                notify(name, status)
            else:
                Supplier.objects.create(name = name, status = status.name)
                notify(name, status)
                
    suppliers = Supplier.objects.filter(status = CompanyStatus.GRANTED.name)

    return render(request, 'list.html', {'suppliers' : suppliers})


def list(request):
    """
    List of electricity suppliers page.
    """
    suppliers = Supplier.objects.filter(status = CompanyStatus.GRANTED.name)
    return render(request, 'list.html', {'suppliers' : suppliers})


def detail(request, name):
    """
    Detail page to inspect company data
    """
    supplier = Supplier.objects.filter(name = name).first()
    scanned_supplier = scan_supplier(name)
    if scanned_supplier:
        if ScannedSupplier.objects.filter(name = scanned_supplier.name).exists() is False:
            scanned_supplier.save()
            supplier.scanned_supplier = scanned_supplier
            supplier.save()

    return render(request, 'detail.html', {'scanned_supplier' : scanned_supplier})


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
    Attempts multiple methods of uncovering the 'correct' name of the company to then scan for company data.
    """
    #Check if ScannedSupplier already exists if so, return.
    if ScannedSupplier.objects.filter(name = name).exists():
        return
    
    query_name = name

    if 'Eneco' in query_name:
        query_name = 'Eneco'

    if 'ENGIE' in query_name:
        query_name = 'Engie'

    if 'Essent' in query_name:
        query_name = 'Essent'

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
    """
    Checks if the company can be found in the response.
    """
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
    """
    Grab the logo from and link and store it locally.
    """
    logo = Image.open(requests.get(logo_url, stream=True).raw)
    image_name = name.replace(' ', '')
    save_path = f'acm_app/static/{image_name}.png'
    logo.save(save_path, format="png")

    return f'{image_name}.png'
    

def create_scanned_supplier(logo: str, name: str, domain: str): 
    """
    Create the actual ScannedSupplier object to be saved later on.
    """
    save_path = save_logo(logo, name)
    return ScannedSupplier(name = name, logo = save_path, website = domain)


#Vanwege tijd niet volledig geimplementeerd maar zou een email sturen via een SMTP Server
#Hier een voorbeeld van hoe ik dit had kunnen doen: https://realpython.com/python-send-email/
def notify(name, status):
    """
    Notify admin email when a new supplier is added or a previous supplier has its rights revoked.
    """

    if status == CompanyStatus.REVOKED:
        print(f'Supplier: {name} has had its license: Revoked')
    elif status == CompanyStatus.GRANTED:
        print(f'A new Supplier has been added: {name}')
    else:
        return

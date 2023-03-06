from django.shortcuts import render
from django.http import HttpResponse

from .models import Supplier, ScannedSupplier
from .enums import CompanyStatus
import requests
from bs4 import BeautifulSoup


def index(request):
    """
    Website homepage.
    """
    return render(request, 'index.html')


def update(request):
    """
    Scrap ACM webpage to retrieve new electricity suppliers and save them in database.
    """

    scan_supplier("Engie")
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


def scan_supplier(name: str):
    """

    """
    #Check if ScannedSupplier already exists if so, return.
    if ScannedSupplier.objects.filter(name = name).exists():
        return
    
    query_name = name

    if 'B.V.' in name:
        query_name = query_name.replace('B.V.', '')

    url = "https://autocomplete.clearbit.com/v1/companies/suggest?query=" + name
    print(url)
    request = requests.get(url)
    response = request.json()

    #More than one company found with this name
    if len(response) > 1:
        
    

    
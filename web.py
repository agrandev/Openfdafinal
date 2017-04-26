 # -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#     Andrea Grande Vadillo

import http.client
import http.server
import json

class OpenFDAClient():

    OPENFDA_API_URL = "api.fda.gov"
    OPENFDA_API_EVENT = "/drug/event.json"
    OPENFDA_API_DRUG = '&search=patient.drug.medicinalproduct:'
    OPENFDA_API_COMPANY='&search=companynumb:'

    def get_event(self, limite):

        conn = http.client.HTTPSConnection(self.OPENFDA_API_URL)
        #search = patient.reaction.reactionnedrapt:"fati"
        conn.request('GET',self.OPENFDA_API_EVENT+'?limit=' + limite)
        r1 = conn.getresponse()
        data1 = r1.read()
        data = data1.decode('utf8')
        events = json.loads(data)
        return events



    def get_search_drug(self, drug_search):
        conn = http.client.HTTPSConnection(self.OPENFDA_API_URL)
        conn.request('GET',self.OPENFDA_API_EVENT + '?limit=10' + self.OPENFDA_API_DRUG + drug_search )
        r1 = conn.getresponse()
        data1 = r1.read()
        data = data1.decode('utf8')
        events = json.loads(data)
        return events

    def get_search_company(self, company_search):
        conn = http.client.HTTPSConnection(self.OPENFDA_API_URL)
        conn.request('GET',self.OPENFDA_API_EVENT+'?limit=10' + self.OPENFDA_API_COMPANY + company_search)
        r1 = conn.getresponse()
        data1 = r1.read()
        data = data1.decode('utf8')
        events = json.loads(data)
        return events



class OpenFDAParser():

    def get_medicamentos(self, events):

        medicamentos = []
        results = events["results"]
        for event in results:

            medicamentos += [event["patient"]["drug"][0]["medicinalproduct"]]

        return medicamentos

    def get_empresas(self, events):
        empresas = []
        results = events["results"]

        for event in results:
            empresas += [event["companynumb"]]
        return empresas

    def get_gender(self, events):
        patientsex=[]
        results=events['results']
        for event in results:
                patientsex+= [event['patient']['patientsex']]
        return patientsex



class OpenFDAHTML():

    def get_main_page(self):
        html = """
        <html>
            <head>
            </head>
            <body>
                <h1>OpenFDA Client</h1>
                <form method="get" action="listDrugs">
                    <input type = "number" size="3" name="limit"></input>
                    <input type = "submit" value="Drug List"></input>
                </form>
                <form method="get" action="searchDrug">
                    <input type = "text" name="drug"></input>
                    <input type = "submit" value="Drug Search"></input>
                </form>
                <form method='get' action='listCompanies'>
                    <input type = "number" size="3" name="limit"></input>
                    <input type = "submit" value="Companies List"></input>
                </form>
                <form method="get" action="searchCompany">
                    <input type = "text" name="company"></input>
                    <input type = "submit" value="Company Search"></input>
                </form>
                <form method="get" action="listGender">
                    <input type = "number" size="3" name="limit"></input>
                    <input type = "submit" value="Gender List"></input>
                </form>
            </body>
        </html>
        """
        return html

    def html_error(self):
        html = """
            <html>
                <head>
                </head>
                <body>
                    <h1>Error 404</h1>
                    <br>Pagina no encontrada.</br>
                    <br>No hemos localizado la pagina que estabas buscando y el servidor devuelve error 404.</br>
                    <br>La pagina que buscas no existe o ha ocurrido un error inesperado.</br>
                </body>
            </html>
            """
        return html

    def list_html(self, items):
        s=""
        for item in items:
            s += "<li>" +item+ "</li>"


        html = """
        <html>
        <head></head>
        <body>
            <h1></h1>
            <ol>
                %s
            </ol>
        </body>
        </html>
        """%(s)

        return html



class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def get_parametro(self):
        parametro = self.path.split("=")[1]
        return parametro

    def limite(self):
        limite=str(self.path.split("=")[1])
        if limite=='':
            limite='10'
        return limite

    def do_GET(self):

        fdaclient=OpenFDAClient()
        fdaparser=OpenFDAParser()
        fdahtml=OpenFDAHTML()

        main_page= False
        is_listdrugs=False
        is_listcompanies=False
        is_search_company=False
        is_search_drug=False
        is_patientsex=False
        if self.path== "/":
            main_page= True
        elif '/listDrugs'in self.path:
            is_listdrugs = True
        elif '/searchDrug'in self.path:
            is_search_drug=True
        elif '/listCompanies'in self.path:
            is_listcompanies=True
        elif '/searchCompany'in self.path:
            is_search_company=True
        elif '/listGender' in self.path:
            is_patientsex=True

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()



        if main_page:
            html = fdahtml.get_main_page()
            self.wfile.write(bytes(html, "utf8"))

        elif is_listdrugs:
            limite=self.limite()
            event=fdaclient.get_event(limite)
            medicamentos= fdaparser.get_medicamentos(event)
            html= fdahtml.list_html(medicamentos)
            self.wfile.write(bytes(html, "utf8"))

        elif is_search_drug:
            drug=self.get_parametro()
            event=fdaclient.get_search_drug(drug)
            companies=fdaparser.get_empresas(event)
            html=fdahtml.list_html(companies)
            self.wfile.write(bytes(html, "utf8"))#event

        elif is_listcompanies:
            limite=self.limite()
            event=fdaclient.get_event(limite)
            empresas= fdaparser.get_empresas(event)
            html= fdahtml.list_html(empresas)
            self.wfile.write(bytes(html, "utf8"))

        elif is_search_company:
            company=self.get_parametro()
            event=fdaclient.get_search_company(company)
            drugs=fdaparser.get_medicamentos(event)
            html=fdahtml.list_html(drugs)
            self.wfile.write(bytes(html, "utf8"))

        elif is_patientsex:
            limite=self.limite()
            event=fdaclient.get_event(limite)
            gender=fdaparser.get_gender(event)
            html= fdahtml.list_html(gender)
            self.wfile.write(bytes(html, "utf8"))
        else:
            error=fdahtml.html_error()
            self.wfile.write(bytes(error, "utf8"))

        return

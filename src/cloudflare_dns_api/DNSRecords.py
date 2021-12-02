# -*- coding: utf-8 -*-
"""
cloudflare_dns_api.DNSRecords
~~~~~~~~~~~~~

"""
import requests
import json

BASE_URL = "https://api.cloudflare.com/client/v4"


class DNSRecords(object):
    def __init__(self, token):
        self.token = token
        self.dns_records = {}

    def _create_headers(self, headers):
        headers["Authorization"] = "Bearer " + self.token
        headers["Content-Type"] = "application/json"

    def _get_request(self, url):
        headers = {}
        self._create_headers(headers)

        try:
            response = requests.get(url, headers=headers)
        except Exception as e:
            raise e

        if response.status_code == 200:
            return response
        else:
            print("Request failure: " + str(response.status_code))
            raise

    def _put_request(self, url, data):
        headers = {}
        self._create_headers(headers)
        try:
            response = requests.put(url, headers=headers, data=json.dumps(data))
        except Exception as e:
            raise e

        if response.status_code == 200:
            return True
        else:
            print("Request failure: " + str(response.status_code))
            raise

    def get_zones(self):
        url = BASE_URL + "/zones"

        response = self._get_request(url)

        zones = {}
        for record in response.json()["result"]:
            zones[record["name"]] = record

        self.dns_records = zones

    def get_dns_records(self, zone_name):
        if not self.dns_records:
            self.get_zones()

        if zone_name in self.dns_records:
            url = (
                BASE_URL
                + "/zones/"
                + self.dns_records[zone_name]["id"]
                + "/dns_records"
            )

            response = self._get_request(url)

            dns_records = {}
            for record in response.json()["result"]:
                dns_records[record["name"], record["type"]] = record

            self.dns_records[zone_name]["dns_records"] = dns_records

        else:
            print("Zone with name " + zone_name + " does not exist.")
            raise

    def update_dns_record(self, zone_name, new_record):
        pass

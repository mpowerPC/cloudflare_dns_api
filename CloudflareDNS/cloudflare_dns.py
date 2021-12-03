# -*- coding: utf-8 -*-
"""
CloudflareDNS.cloudflare_dns
~~~~~~~~~~~~~

"""
import requests
import json

BASE_URL = "https://api.cloudflare.com/client/v4/"


def check_record(record):
    valid_types = (
        "A",
        "AAAA",
        "CNAME",
        "HTTPS",
        "TXT",
        "SRV",
        "LOC",
        "MX",
        "NS",
        "CERT",
        "DNSKEY",
        "DS",
        "NAPTR",
        "SMIMEA",
        "SSHFP",
        "SVCB",
        "TLSA",
        "URI",
        "read only",
    )

    record_pass = True
    for key in record:
        if key not in ("type", "name", "content", "ttl", "priority", "proxied"):
            print("Invalid record key.")
            record_pass = False

    if "type" in record:
        if record["type"] not in valid_types:
            print("Key 'type' is not a valid value.")
            record_pass = False

        elif record["type"] in ("MX", "SRV", "URI"):
            if "priority" in record:
                if not (0 <= record["priority"] <= 65535):
                    print("Key 'priority' is not a valid value.")
                    record_pass = False
            else:
                print("Required key 'priority' is missing.")
                record_pass = False
    else:
        print("Required key 'type' is missing.")
        record_pass = False

    if "name" not in record:
        print("Required key 'name' is missing.")
        record_pass = False

    if "content" not in record:
        print("Required key 'content' is missing.")
        record_pass = False

    if "ttl" in record:
        if not (record["ttl"] == 1 or 60 <= record["ttl"] <= 86400):
            print("Key 'ttl' is not a valid value.")
            record_pass = False
    else:
        print("Required key 'ttl' is missing.")
        record_pass = False

    if not record_pass:
        print("Submitted record not compliant with Cloudflare API.")
        raise


class CloudflareDNS(object):
    def __init__(self, token):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        }
        self.dns_records = {}

    def _get_request(self, url):
        try:
            response = requests.get(url, headers=self.headers)
        except Exception as e:
            raise e

        if response.status_code == 200:
            return response
        else:
            print("Request failure: " + str(response.status_code))
            raise

    def _post_request(self, url, data):
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(data))
        except Exception as e:
            raise e

        if response.status_code == 200:
            return True
        else:
            print("Request failure: " + str(response.status_code))
            raise

    def _put_request(self, url, data):
        try:
            response = requests.put(url, headers=self.headers, data=json.dumps(data))
        except Exception as e:
            raise e

        if response.status_code == 200:
            return True
        else:
            print("Request failure: " + str(response.status_code))
            raise

    def _delete_request(self, url):
        try:
            response = requests.delete(url, headers=self.headers)
        except Exception as e:
            raise e

        if response.status_code == 200:
            return True
        else:
            print("Request failure: " + str(response.status_code))
            raise

    def _simplified_zones(self):
        output = {}
        for zone_name in self.dns_records:
            record = self.dns_records[zone_name]
            output[zone_name] = {
                "id": record["id"],
                "name": record["name"],
                "status": record["status"],
            }
        return output

    def _simplified_dns_records(self, zone_name):
        dns_records = {}
        for dns_record_key in self.dns_records[zone_name]["dns_records"]:
            record = self.dns_records[zone_name]["dns_records"][dns_record_key]
            dns_records[dns_record_key] = {
                "id": record["id"],
                "name": record["name"],
                "type": record["type"],
                "content": record["content"],
                "ttl": record["ttl"],
                "proxied": record["proxied"],
            }
            if "priority" in record:
                dns_records[dns_record_key]["priority"] = record["priority"]
        return dns_records

    def get_zones(self):
        url = BASE_URL + "zones"
        response = self._get_request(url)
        zones = {}
        for record in response.json()["result"]:
            zones[record["name"]] = record
        self.dns_records = zones

        return self._simplified_zones()

    def get_records(self, zone_name):
        if not self.dns_records:
            self.get_zones()

        if zone_name in self.dns_records:
            url = (
                BASE_URL + "zones/" + self.dns_records[zone_name]["id"] + "/dns_records"
            )

            response = self._get_request(url)

            dns_records = {}
            for record in response.json()["result"]:
                dns_records[record["name"], record["type"]] = record

            self.dns_records[zone_name]["dns_records"] = dns_records
        else:
            print("Zone with name " + zone_name + " does not exist.")
            raise

        return self._simplified_dns_records(zone_name)

    def insert_record(self, zone_name, new_record):
        old_records = self.get_records(zone_name)
        zone_id = self.dns_records[zone_name]["id"]

        check_record(new_record)

        key = (new_record["name"], new_record["type"])
        if key not in old_records:
            url = BASE_URL + "zones/" + zone_id + "/dns_records"
            self._post_request(url, new_record)
        else:
            print("Record already exists.")
            raise

        return self.get_records(zone_name)

    def update_record(self, zone_name, new_record):
        old_records = self.get_records(zone_name)
        zone_id = self.dns_records[zone_name]["id"]

        check_record(new_record)

        key = (new_record["name"], new_record["type"])
        if key in old_records:
            new_record["id"] = old_records[key]["id"]
            if new_record != old_records[key]:
                url = BASE_URL + "zones/" + zone_id + "/dns_records/" + new_record["id"]

                self._put_request(url, new_record)
            else:
                print("Record already exists.")
        else:
            print("Record does not exists.")
            raise

        return self.get_records(zone_name)

    def delete_record(self, zone_name, dns_record_name, dns_record_type):
        old_records = self.get_records(zone_name)
        zone_id = self.dns_records[zone_name]["id"]
        key = (dns_record_name, dns_record_type)

        if key in old_records:
            url = (
                BASE_URL + "zones/" + zone_id + "/dns_records/" + old_records[key]["id"]
            )
            self._delete_request(url)
        else:
            print("Records were not deleted, unable to find DNS record identifier.")

        return self.get_records(zone_name)

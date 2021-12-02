# -*- coding: utf-8 -*-
"""
cloudflare_dns_api.DNSRecords
~~~~~~~~~~~~~

"""
import requests
import json

BASE_URL = "https://api.cloudflare.com/client/v4/zones"


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

    return record_pass


class DNSRecords(object):
    def __init__(self, token):
        self.headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
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
            if "priority" in record:
                dns_records[dns_record_key] = {
                    "id": record["id"],
                    "name": record["name"],
                    "type": record["type"],
                    "content": record["content"],
                    "ttl": record["ttl"],
                    "priority": record["priority"],
                    "proxied": record["proxied"],
                }
            else:
                dns_records[dns_record_key] = {
                    "id": record["id"],
                    "name": record["name"],
                    "type": record["type"],
                    "content": record["content"],
                    "ttl": record["ttl"],
                    "proxied": record["proxied"],
                }
        output = {zone_name: {"dns_records": dns_records}}
        return output

    def zones(self):
        response = self._get_request(BASE_URL)
        zones = {}
        for record in response.json()["result"]:
            zones[record["name"]] = record
        self.dns_records = zones

        return self._simplified_zones()

    def get(self, zone_name):
        if not self.dns_records:
            self.zones()

        if zone_name in self.dns_records:
            url = BASE_URL + "/" + self.dns_records[zone_name]["id"] + "/dns_records"

            response = self._get_request(url)

            dns_records = {}
            for record in response.json()["result"]:
                dns_records[record["name"], record["type"]] = record

            self.dns_records[zone_name]["dns_records"] = dns_records

        else:
            print("Zone with name " + zone_name + " does not exist.")
            raise

        return self._simplified_dns_records(zone_name)

    def merge(self, zone_name, new_record):
        if not self.dns_records:
            self.zones()

        if zone_name in self.dns_records:
            if "dns_records" not in self.dns_records[zone_name]:
                self.get(zone_name)

            zone_id = self.dns_records[zone_name]["id"]
            if check_record(new_record):
                old_records = self._simplified_dns_records(zone_name)[zone_name][
                    "dns_records"
                ]
                if (new_record["name"], new_record["type"]) in old_records:
                    new_record["id"] = old_records[
                        (new_record["name"], new_record["type"])
                    ]["id"]
                    if (
                        new_record
                        != old_records[(new_record["name"], new_record["type"])]
                    ):
                        url = (
                            BASE_URL
                            + "/"
                            + zone_id
                            + "/dns_records/"
                            + new_record["id"]
                        )

                        self._put_request(url, new_record)
                    else:
                        print("Record already exists.")
                else:
                    url = BASE_URL + "/" + zone_id + "/dns_records"

                    self._post_request(url, new_record)

            else:
                print("Record does not comply with Cloudflare api.")
                raise
        else:
            print("Zone with name " + zone_name + " does not exist.")
            raise

        return self.get(zone_name)

    def delete(
        self, zone_name, dns_record_id=None, dns_record_name=None, dns_record_type=None
    ):
        if not self.dns_records:
            self.zones()

        if zone_name in self.dns_records:
            if "dns_records" not in self.dns_records[zone_name]:
                self.get(zone_name)

            if (dns_record_name, dns_record_type) in self.dns_records[zone_name][
                "dns_records"
            ]:
                dns_record_id = self.dns_records[zone_name]["dns_records"][
                    (dns_record_name, dns_record_type)
                ]["id"]

            if dns_record_id:
                url = (
                    BASE_URL
                    + "/"
                    + self.dns_records[zone_name]["id"]
                    + "/dns_records/"
                    + dns_record_id
                )
                self._delete_request(url)
            else:
                print("Records were not deleted, unable to find DNS record identifier.")
        else:
            print("Zone with name " + zone_name + " does not exist.")
            raise

        return self.get(zone_name)

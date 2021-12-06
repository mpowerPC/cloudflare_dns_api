# -*- coding: utf-8 -*-
"""
CloudflareDNS.cloudflare_dns
~~~~~~~~~~~~~

"""
import requests
import warnings
import json

BASE_URL = "https://api.cloudflare.com/client/v4/"


def check_record(record):
    """Verifies that the submitted dns record contains the necessary keys and dns types to be posted to the Cloudflare
    API.

    :param record: A DNS record.
    :type record: dict
    """
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
        if key not in ("type", "name", "content", "ttl", "priority", "proxied", "id"):
            warnings.warn("Invalid key in DNS record: " + key)
            record_pass = False

    if "type" in record:
        if record["type"] not in valid_types:
            warnings.warn("Key 'type' is not a valid value: " + record["type"])
            record_pass = False

        elif record["type"] in ("MX", "SRV", "URI"):
            if "priority" not in record:
                warnings.warn("Required key 'priority' is missing from the DNS record.")
                record_pass = False
    else:
        warnings.warn("Required key 'type' is missing from the DNS record.")
        record_pass = False

    if "name" not in record:
        warnings.warn("Required key 'name' is missing from the DNS record.")
        record_pass = False

    if "content" not in record:
        warnings.warn("Required key 'content' is missing from the DNS record.")
        record_pass = False

    if "ttl" not in record:
        warnings.warn("Required key 'ttl' is missing is missing from the DNS record.")
        record_pass = False

    if not record_pass:
        raise ValueError(
            "Submitted record not compliant with Cloudflare API. Check logs for exact issue."
        )


class CloudflareDNS(object):
    """This is a class that utilizes the requests library to interact with the Cloudflare API DNS Records for a Zone
    found: 'https://api.cloudflare.com/#dns-records-for-a-zone-properties'. Allowing for automated creation, updating and
    deleting of DNS records in specified zones.

    :param token: A Cloudflare API Token with Zone.DNS permissions.
    :type token: str
    """

    def __init__(self, token):
        """Constructor method
        """
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        }
        self.dns_records = {}

    def _get_request(self, url):
        """Returns a :class:`requests.Response` object which contains a server’s response to an HTTP request.
        :param url: A url to send a get request.
        :type url: str
        :return: A server’s response to an HTTP request.
        :rtype: requests.Response object
        """
        try:
            response = requests.get(url, headers=self.headers)
        except Exception as e:
            raise e

        if response.status_code == 200:
            return response
        else:
            response.raise_for_status()

    def _post_request(self, url, data):
        """Returns a :class:`requests.Response` object which contains a server’s response to an HTTP request.
        :param url: A url to send a post request.
        :type url: str
        :param data: A payload to send with the post request.
        :type data: dict
        :return: A server’s response to an HTTP request.
        :rtype: requests.Response object
        """
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(data))
        except Exception as e:
            raise e

        if response.status_code == 200:
            return response
        else:
            response.raise_for_status()

    def _put_request(self, url, data):
        """Returns a :class:`requests.Response` object which contains a server’s response to an HTTP request.
        :param url: A url to send a put request.
        :type url: str
        :param data: A payload to send with the put request.
        :type data: dict
        :return: A server’s response to an HTTP request.
        :rtype: requests.Response object
        """
        try:
            response = requests.put(url, headers=self.headers, data=json.dumps(data))
        except Exception as e:
            raise e

        if response.status_code == 200:
            return response
        else:
            response.raise_for_status()

    def _delete_request(self, url):
        """Returns a :class:`requests.Response` object which contains a server’s response to an HTTP request.
        :param url: A url to send a delete request.
        :type url: str
        :return: A server’s response to an HTTP request.
        :rtype: requests.Response object
        """
        try:
            response = requests.delete(url, headers=self.headers)
        except Exception as e:
            raise e

        if response.status_code == 200:
            return response
        else:
            response.raise_for_status()

    def _simplified_zones(self):
        """Returns a dict of zones attached to the API token, this dictionary is keyed on zone names.

        :return: A dict of zones keyed on zone names.
        :rtype: dict
        """
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
        """Returns a dict of dns records attached to the API token and zone, this dictionary is keyed on record name and
         type.

        :param zone_name: A Cloudflare DNS zone usually the domain name.
        :type zone_name: str
        :return: A dict of dns records keyed on record name and type.
        :rtype: dict
        """
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
        """Returns a dict of zones attached to the API token, this dictionary is keyed on zone names. This function
         preforms a get request to 'https://api.cloudflare.com/client/v4/zones' which returns all zones attached to the
         API token.

        :return: A dict of zones keyed on zone names.
        :rtype: dict
        """
        url = BASE_URL + "zones"
        response = self._get_request(url)
        zones = {}
        for record in response.json()["result"]:
            zones[record["name"]] = record
        self.dns_records = zones

        return self._simplified_zones()

    def get_records(self, zone_name):
        """Returns a dict of dns records attached to the API token and zone, this dictionary is keyed on record name and
         type. This function preforms a get request to
         'https://api.cloudflare.com/client/v4/zones/<zone_name>/dns_records' which returns all dns records attached to
         the spcified zone.

        :param zone_name: A Cloudflare DNS zone usually the domain name.
        :type zone_name: str
        :return: A dict of dns records keyed on record name and type.
        :rtype: dict
        """
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
            raise ValueError("Zone with name " + zone_name + " does not exist.")

        return self._simplified_dns_records(zone_name)

    def insert_record(self, zone_name, new_record):
        """Returns a dict of dns records attached to the API token and zone, this dictionary is keyed on record name and
         type. This function preforms a post request to
         'https://api.cloudflare.com/client/v4/zones/<zone_name>/dns_records' which inserts the dns record into the
         zone.

        :param zone_name: A Cloudflare DNS zone usually the domain name.
        :type zone_name: str
        :param new_record: A DNS record.
        :type new_record: dict
        :return: A dict of dns records keyed on record name and type.
        :rtype: dict
        """
        old_records = self.get_records(zone_name)
        zone_id = self.dns_records[zone_name]["id"]

        check_record(new_record)

        key = (new_record["name"], new_record["type"])
        if key not in old_records:
            url = BASE_URL + "zones/" + zone_id + "/dns_records"
            self._post_request(url, new_record)
        else:
            warnings.warn("DNS record already exists.")

        return self.get_records(zone_name)

    def update_record(self, zone_name, new_record):
        """Returns a dict of dns records attached to the API token and zone, this dictionary is keyed on record name and
         type. This function preforms a put request to
         'https://api.cloudflare.com/client/v4/zones/<zone_name>/dns_records/<record_id>' which updates fields of the
         dns record.

        :param zone_name: A Cloudflare DNS zone usually the domain name.
        :type zone_name: str
        :param new_record: A DNS record.
        :type new_record: dict
        :return: A dict of dns records keyed on record name and type.
        :rtype: dict
        """
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
                warnings.warn("DNS record already exists.")
        else:
            raise ValueError("DNS record does not exist.")

        return self.get_records(zone_name)

    def delete_record(self, zone_name, dns_record_name, dns_record_type):
        """Returns a dict of dns records attached to the API token and zone, this dictionary is keyed on record name and
         type. This function preforms a delete request to
         'https://api.cloudflare.com/client/v4/zones/<zone_name>/dns_records/<record_id>' which delete the dns record.

        :param zone_name: A Cloudflare DNS zone usually the domain name.
        :type zone_name: str
        :param dns_record_name: DNS record name.
        :type dns_record_name: str
        :param dns_record_type: DNS record type.
        :type dns_record_type: str
        :return: A dict of dns records keyed on record name and type.
        :rtype: dict
        """
        old_records = self.get_records(zone_name)
        zone_id = self.dns_records[zone_name]["id"]
        key = (dns_record_name, dns_record_type)

        if key in old_records:
            url = (
                BASE_URL + "zones/" + zone_id + "/dns_records/" + old_records[key]["id"]
            )
            self._delete_request(url)
        else:
            warnings.warn(
                "Records were not deleted, unable to find DNS record identifier."
            )

        return self.get_records(zone_name)

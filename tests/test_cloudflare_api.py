# -*- coding: utf-8 -*-
"""
tests.test_cloudflare_dns
~~~~~~~~~~~~~
Too run tests a file named test.json must be placed in the test folder with a working Cloudflare API token in it. The
associated account must also have a zone to test adding and removing dns records.

EXAMPLE "test.json" FILE:
{
    "token": "YQSn-xWAQiiEh9qM58wZNnyQS7FUdoqGIUAbrh7T",
    "zone": "example.com"
}
"""
import CloudflareDNS
import json
import pytest

with open("test.json") as f:
    cfg = json.load(f)
    TOKEN = cfg["token"]
    ZONE = cfg["zone"]


def test_insert_record():
    cfd = CloudflareDNS.CloudflareDNS(token=TOKEN)
    test_record = {
        "type": "TXT",
        "name": "cloudflare_dns_api." + ZONE,
        "content": "Insert TEST",
        "ttl": 1,
        "proxied": False,
    }

    dns_records = cfd.insert_record(ZONE, test_record)
    result_record = dns_records[(test_record["name"], test_record["type"])]
    test_record["id"] = result_record["id"]
    assert test_record == result_record


def test_update_record():
    cfd = CloudflareDNS.CloudflareDNS(token=TOKEN)
    test_record = {
        "type": "TXT",
        "name": "cloudflare_dns_api." + ZONE,
        "content": "Update TEST",
        "ttl": 1,
        "proxied": False,
    }

    dns_records = cfd.update_record(ZONE, test_record)
    result_record = dns_records[(test_record["name"], test_record["type"])]
    test_record["id"] = result_record["id"]
    assert test_record == result_record


def test_delete_record():
    cfd = CloudflareDNS.CloudflareDNS(token=TOKEN)
    test_record = {
        "type": "TXT",
        "name": "cloudflare_dns_api." + ZONE,
        "content": "Update TEST",
        "ttl": 1,
        "proxied": False,
    }

    dns_records = cfd.delete_record(ZONE, test_record["name"], test_record["type"])

    key = (test_record["name"], test_record["type"])

    assert key not in dns_records


if __name__ == "__main__":
    pytest.main([__file__])

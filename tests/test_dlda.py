#!/usr/bin/env python

import os
import sys

# For coverage.
if __package__ is None:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from unittest import main, TestCase

import requests
import requests_mock

from iris_sdk.client import Client
from iris_sdk.models.account import Account

XML_RESPONSE_DLDA_GET = (
    "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>"
    "<DldaOrderResponse><DldaOrder>"
    "<CustomerOrderId>5a88d16d-f8a9-45c5-a5db-137d700c6a22</CustomerOrderId>"
    "<OrderCreateDate>2014-07-10T12:38:11.833Z</OrderCreateDate>"
    "<AccountId>14</AccountId><CreatedByUser>jbm</CreatedByUser>"
    "<OrderId>ea9e90c2-77a4-4f82-ac47-e1c5bb1311f4</OrderId>"
    "<LastModifiedDate>2014-07-10T12:38:11.833Z</LastModifiedDate>"
    "<ProcessingStatus>RECEIVED</ProcessingStatus><DldaTnGroups>"
    "<DldaTnGroup><TelephoneNumbers>"
    "<TelephoneNumber>2053778335</TelephoneNumber>"
    "<TelephoneNumber>2053865784</TelephoneNumber></TelephoneNumbers>"
    "<AccountType>BUSINESS</AccountType><ListingType>LISTED</ListingType>"
    "<ListingName><FirstName>Joe</FirstName><LastName>Smith</LastName>"
    "</ListingName><ListAddress>true</ListAddress><Address>"
    "<HouseNumber>12</HouseNumber><StreetName>ELM</StreetName>"
    "<City>New York</City><StateCode>NY</StateCode><Zip>10007</Zip>"
    "<Country>United States</Country><AddressType>Dlda</AddressType>"
    "</Address></DldaTnGroup></DldaTnGroups></DldaOrder>"
    "</DldaOrderResponse>"
)

XML_RESPONSE_DLDA_HISTORY = (
    "<?xml version=\"1.0\"?> <OrderHistoryWrapper><OrderHistory>"
    "<OrderDate>2014-09-04T16:28:11.320Z</OrderDate>"
    "<Note>The DL/DA request has been received</Note>"
    "<Author>jbm</Author><Status>RECEIVED</Status></OrderHistory>"
    "<OrderHistory><OrderDate>2014-09-04T16:28:18.742Z</OrderDate>"
    "<Note>The DL/DA request is being processed by our 3rd party supplier"
    "</Note><Author>jbm</Author><Status>PROCESSING</Status> </OrderHistory>"
    "<OrderHistory><OrderDate>2014-09-05T19:00:17.968Z</OrderDate>"
    "<Note>The DL/DA request is complete for all TNs</Note>"
    "<Author>jbm</Author><Status>COMPLETE</Status></OrderHistory>"
    "</OrderHistoryWrapper>"
)

XML_RESPONSE_DLDA_LIST = (
    "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>"
    "<ResponseSelectWrapper><ListOrderIdUserIdDate>"
    "<TotalCount>3</TotalCount><OrderIdUserIdDate>"
    "<accountId>14</accountId><CountOfTNs>2</CountOfTNs>"
    "<userId>team_ua</userId>"
    "<lastModifiedDate>2014-07-07T10:06:43.427Z</lastModifiedDate>"
    "<OrderType>dlda</OrderType>"
    "<OrderDate>2014-07-07T10:06:43.427Z</OrderDate>"
    "<orderId>37a6447c-1a0b-4be9-ba89-3f5cb0aea142</orderId>"
    "<OrderStatus>FAILED</OrderStatus></OrderIdUserIdDate>"
    "<OrderIdUserIdDate><accountId>14</accountId>"
    "<CountOfTNs>2</CountOfTNs><userId>team_ua</userId>"
    "<lastModifiedDate>2014-07-07T10:05:56.595Z</lastModifiedDate>"
    "<OrderType>dlda</OrderType>"
    "<OrderDate>2014-07-07T10:05:56.595Z</OrderDate>"
    "<orderId>743b0e64-3350-42e4-baa6-406dac7f4a85</orderId>"
    "<OrderStatus>RECEIVED</OrderStatus></OrderIdUserIdDate>"
    "<OrderIdUserIdDate><accountId>14</accountId>"
    "<CountOfTNs>2</CountOfTNs><userId>team_ua</userId>"
    "<lastModifiedDate>2014-07-07T09:32:17.234Z</lastModifiedDate>"
    "<OrderType>dlda</OrderType>"
    "<OrderDate>2014-07-07T09:32:17.234Z</OrderDate>"
    "<orderId>f71eb4d2-bfef-4384-957f-45cd6321185e</orderId>"
    "<OrderStatus>RECEIVED</OrderStatus></OrderIdUserIdDate>"
    "</ListOrderIdUserIdDate></ResponseSelectWrapper>"
)

XML_RESPONSE_DLDA_POST = (
    "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>"
    "<DldaOrderResponse><DldaOrder>"
    "<CustomerOrderId>5a88d16d-f8a9-45c5-a5db-137d700c6a22</CustomerOrderId>"
    "<OrderCreateDate>2014-07-10T12:38:11.833Z</OrderCreateDate>"
    "<AccountId>14</AccountId><CreatedByUser>jbm</CreatedByUser>"
    "<OrderId>ea9e90c2-77a4-4f82-ac47-e1c5bb1311f4</OrderId>"
    "<LastModifiedDate>2014-07-10T12:38:11.833Z</LastModifiedDate>"
    "<ProcessingStatus>RECEIVED</ProcessingStatus><DldaTnGroups>"
    "<DldaTnGroup><TelephoneNumbers>"
    "<TelephoneNumber>2053778335</TelephoneNumber>"
    "<TelephoneNumber>2053865784</TelephoneNumber></TelephoneNumbers>"
    "<AccountType>BUSINESS</AccountType><ListingType>LISTED</ListingType>"
    "<ListingName><FirstName>Joe</FirstName><LastName>Smith</LastName>"
    "</ListingName><ListAddress>true</ListAddress><Address>"
    "<HouseNumber>12</HouseNumber><StreetName>ELM</StreetName>"
    "<City>New York</City><StateCode>NY</StateCode><Zip>10007</Zip>"
    "<Country>United States</Country><AddressType>Dlda</AddressType>"
    "</Address></DldaTnGroup></DldaTnGroups></DldaOrder>"
    "</DldaOrderResponse>"
)

class ClassDldaTest(TestCase):

    """Test DLDA orders"""

    @classmethod
    def setUpClass(cls):
        cls._client = Client("http://foo", "bar", "bar", "qux")
        cls._account = Account(client=cls._client)

    @classmethod
    def tearDownClass(cls):
        del cls._client
        del cls._account

    def test_dldas_get(self):

        dlda = self._account.dldas.create()
        dlda.id = "ea9e90c2-77a4-4f82-ac47-e1c5bb1311f4"

        self.assertEquals(dlda.get_xpath(),
            self._account.get_xpath() + self._account.dldas._xpath +
            dlda._xpath.format(dlda.id))

        url = self._client.config.url + dlda.get_xpath()

        with requests_mock.Mocker() as m:

            m.get(url, content=XML_RESPONSE_DLDA_GET)

            dlda = self._account.dldas.get(dlda.id)

            self.assertEquals(m.request_history[0].method, "GET")

            self.assertEquals(dlda.id, "ea9e90c2-77a4-4f82-ac47-e1c5bb1311f4")
            self.assertEquals(dlda.customer_order_id,
                "5a88d16d-f8a9-45c5-a5db-137d700c6a22")
            self.assertEquals(dlda.order_create_date,
                "2014-07-10T12:38:11.833Z")
            self.assertEquals(dlda.account_id, "14")
            self.assertEquals(dlda.created_by_user, "jbm")
            self.assertEquals(dlda.order_id,
                "ea9e90c2-77a4-4f82-ac47-e1c5bb1311f4")
            self.assertEquals(dlda.last_modified_date,
                "2014-07-10T12:38:11.833Z")
            self.assertEquals(dlda.processing_status, "RECEIVED")

            grp = dlda.dlda_tn_groups.dlda_tn_group.items[0]

            self.assertEquals(
                grp.telephone_numbers.telephone_number.items,
                ["2053778335","2053865784"]
            )

            self.assertEquals(grp.account_type, "BUSINESS")
            self.assertEquals(grp.listing_type, "LISTED")
            self.assertEquals(grp.list_address, "true")

            lname = grp.listing_name

            self.assertEquals(lname.first_name, "Joe")
            self.assertEquals(lname.last_name, "Smith")

            addr = grp.address

            self.assertEquals(addr.city, "New York")
            self.assertEquals(addr.house_number, "12")
            self.assertEquals(addr.street_name, "ELM")
            self.assertEquals(addr.state_code, "NY")
            self.assertEquals(addr.zip, "10007")
            self.assertEquals(addr.country, "United States")
            self.assertEquals(addr.address_type, "Dlda")

    def test_dldas_list(self):

        self.assertEquals(self._account.dldas.get_xpath(),
            self._account.get_xpath() + self._account.dldas._xpath)

        url = self._client.config.url + self._account.dldas.get_xpath()

        with requests_mock.Mocker() as m:

            m.get(url, content=XML_RESPONSE_DLDA_LIST)

            dldas = self._account.dldas.list()

            dlda = dldas.items[0]

            self.assertEquals(m.request_history[0].method, "GET")

            self.assertEquals(len(dldas.items), 3)
            self.assertEquals(dlda.id, "37a6447c-1a0b-4be9-ba89-3f5cb0aea142")
            self.assertEquals(dlda.account_id, "14")
            self.assertEquals(dlda.count_of_tns, "2")
            self.assertEquals(dlda.user_id, "team_ua")
            self.assertEquals(dlda.last_modified_date,
                "2014-07-07T10:06:43.427Z")
            self.assertEquals(dlda.order_type, "dlda")
            self.assertEquals(dlda.order_date, "2014-07-07T10:06:43.427Z")
            self.assertEquals(dlda.order_id, "37a6447c-1a0b-4be9-ba89-3f5cb0aea142")
            self.assertEquals(dlda.order_status, "FAILED")

    def test_dldas_post(self):

        self.assertEquals(self._account.dldas.get_xpath(),
            self._account.get_xpath() + self._account.dldas._xpath)

        url = self._client.config.url + self._account.dldas.get_xpath()

        with requests_mock.Mocker() as m:

            m.post(url, content=XML_RESPONSE_DLDA_POST)

            order_data = {
                "customer_order_id": "123",
                "dlda_tn_groups": {
                    "dlda_tn_group": [{
                        "telephone_numbers": {
                            "telephone_number": ["4352154856"]
                        },
                        "account_type": "RESIDENTIAL",
                        "listing_type": "LISTED",
                        "list_address": "true",
                        "listing_name": {
                            "first_name": "first name",
                            "first_name2": "first name2",
                            "last_name": "last name",
                            "designation": "designation",
                            "title_of_lineage": "title of lineage",
                            "title_of_address": "title of address",
                            "title_of_address2": "title of address2",
                            "title_of_lineage_name2":"title of lineage name2",
                            "title_of_address_name2":"title of address name2",
                            "title_of_address2_name2":
                                "title of address2 name2",
                            "place_listing_as": "place listing as"
                        },
                        "address": {
                            "house_prefix": "house prefix",
                            "house_number": "915",
                            "house_suffix": "house suffix",
                            "pre_directional": "pre directional",
                            "street_name": "street name",
                            "street_suffix": "street suffix",
                            "post_directional": "post directional",
                            "address_line2": "address line2",
                            "city": "city",
                            "state_code": "state code",
                            "zip": "zip",
                            "plus_four": "plus four",
                            "country": "country",
                            "address_type": "address type"
                        }
                    }]
                }
            }

            dlda = self._account.dldas.create(order_data, False)

            self.assertEquals(dlda.customer_order_id, "123")
            grp = dlda.dlda_tn_groups.dlda_tn_group.items[0]
            self.assertEquals(grp.telephone_numbers.telephone_number.items,
                ["4352154856"])
            self.assertEquals(grp.account_type, "RESIDENTIAL")
            self.assertEquals(grp.listing_type, "LISTED")
            self.assertEquals(grp.list_address, "true")

            name = grp.listing_name

            self.assertEquals(name.first_name, "first name")
            self.assertEquals(name.first_name2, "first name2")
            self.assertEquals(name.last_name, "last name")
            self.assertEquals(name.designation, "designation")
            self.assertEquals(name.title_of_lineage, "title of lineage")
            self.assertEquals(name.title_of_address, "title of address")
            self.assertEquals(name.title_of_address2, "title of address2")
            self.assertEquals(name.title_of_lineage_name2,
                "title of lineage name2")
            self.assertEquals(name.title_of_address_name2,
                "title of address name2")
            self.assertEquals(name.title_of_address2_name2,
                "title of address2 name2")
            self.assertEquals(name.place_listing_as, "place listing as")

            addr = grp.address

            self.assertEquals(addr.house_prefix, "house prefix")
            self.assertEquals(addr.house_number, "915")
            self.assertEquals(addr.house_suffix, "house suffix")
            self.assertEquals(addr.pre_directional, "pre directional")
            self.assertEquals(addr.street_name, "street name")
            self.assertEquals(addr.street_suffix, "street suffix")
            self.assertEquals(addr.post_directional, "post directional")
            self.assertEquals(addr.address_line2, "address line2")
            self.assertEquals(addr.city, "city")
            self.assertEquals(addr.state_code, "state code")
            self.assertEquals(addr.zip, "zip")
            self.assertEquals(addr.plus_four, "plus four")
            self.assertEquals(addr.country, "country")
            self.assertEquals(addr.address_type, "address type")

            dlda = self._account.dldas.create(order_data)

            self.assertEquals(m.request_history[0].method, "POST")

            self.assertEquals(dlda.customer_order_id,
                "5a88d16d-f8a9-45c5-a5db-137d700c6a22")
            self.assertEquals(dlda.order_create_date,
                "2014-07-10T12:38:11.833Z")
            self.assertEquals(dlda.account_id, "14")
            self.assertEquals(dlda.created_by_user, "jbm")
            self.assertEquals(dlda.order_id,
                "ea9e90c2-77a4-4f82-ac47-e1c5bb1311f4")
            self.assertEquals(dlda.last_modified_date,
                "2014-07-10T12:38:11.833Z")
            self.assertEquals(dlda.processing_status, "RECEIVED")

            grp = dlda.dlda_tn_groups.dlda_tn_group.items[0]

            self.assertEquals(grp.telephone_numbers.telephone_number.items,
                ["2053778335","2053865784"])
            self.assertEquals(grp.account_type, "BUSINESS")
            self.assertEquals(grp.listing_type, "LISTED")
            self.assertEquals(grp.list_address, "true")

            name = grp.listing_name

            self.assertEquals(name.first_name, "Joe")
            self.assertEquals(name.last_name, "Smith")

            addr = grp.address

            self.assertEquals(addr.city, "New York")
            self.assertEquals(addr.house_number, "12")
            self.assertEquals(addr.street_name, "ELM")
            self.assertEquals(addr.state_code, "NY")
            self.assertEquals(addr.zip, "10007")
            self.assertEquals(addr.country, "United States")
            self.assertEquals(addr.address_type, "Dlda")

    def test_dldas_put(self):

        order_data = {
            "order_id": "7802373f-4f52-4387-bdd1-c5b74833d6e2",
            "customer_order_id": "123",
            "dlda_tn_groups": {
                "dlda_tn_group": [{
                    "telephone_numbers": {
                        "telephone_number": ["4352154856"]
                    },
                    "account_type": "RESIDENTIAL",
                    "listing_type": "LISTED",
                    "list_address": "true",
                    "listing_name": {
                        "first_name": "first name",
                        "first_name2": "first name2",
                        "last_name": "last name",
                        "designation": "designation",
                        "title_of_lineage": "title of lineage",
                        "title_of_address": "title of address",
                        "title_of_address2": "title of address2",
                        "title_of_lineage_name2":"title of lineage name2",
                        "title_of_address_name2":"title of address name2",
                        "title_of_address2_name2": "title of address2 name2",
                        "place_listing_as": "place listing as"
                    },
                    "address": {
                        "house_prefix": "house prefix",
                        "house_number": "915",
                        "house_suffix": "house suffix",
                        "pre_directional": "pre directional",
                        "street_name": "street name",
                        "street_suffix": "street suffix",
                        "post_directional": "post directional",
                        "address_line2": "address line2",
                        "city": "city",
                        "state_code": "state code",
                        "zip": "zip",
                        "plus_four": "plus four",
                        "country": "country",
                        "address_type": "address type"
                    }
                }]
            }
        }

        dlda = self._account.dldas.create(order_data, False)

        self.assertEquals(dlda.customer_order_id, "123")
        self.assertEquals(dlda.order_id,
            "7802373f-4f52-4387-bdd1-c5b74833d6e2")

        grp = dlda.dlda_tn_groups.dlda_tn_group.items[0]
        self.assertEquals(grp.telephone_numbers.telephone_number.items,
            ["4352154856"])
        self.assertEquals(grp.account_type, "RESIDENTIAL")
        self.assertEquals(grp.listing_type, "LISTED")
        self.assertEquals(grp.list_address, "true")

        name = grp.listing_name

        self.assertEquals(name.first_name, "first name")
        self.assertEquals(name.first_name2, "first name2")
        self.assertEquals(name.last_name, "last name")
        self.assertEquals(name.designation, "designation")
        self.assertEquals(name.title_of_lineage, "title of lineage")
        self.assertEquals(name.title_of_address, "title of address")
        self.assertEquals(name.title_of_address2, "title of address2")
        self.assertEquals(name.title_of_lineage_name2,
            "title of lineage name2")
        self.assertEquals(name.title_of_address_name2,
            "title of address name2")
        self.assertEquals(name.title_of_address2_name2,
            "title of address2 name2")
        self.assertEquals(name.place_listing_as, "place listing as")

        addr = grp.address

        self.assertEquals(addr.house_prefix, "house prefix")
        self.assertEquals(addr.house_number, "915")
        self.assertEquals(addr.house_suffix, "house suffix")
        self.assertEquals(addr.pre_directional, "pre directional")
        self.assertEquals(addr.street_name, "street name")
        self.assertEquals(addr.street_suffix, "street suffix")
        self.assertEquals(addr.post_directional, "post directional")
        self.assertEquals(addr.address_line2, "address line2")
        self.assertEquals(addr.city, "city")
        self.assertEquals(addr.state_code, "state code")
        self.assertEquals(addr.zip, "zip")
        self.assertEquals(addr.plus_four, "plus four")
        self.assertEquals(addr.country, "country")
        self.assertEquals(addr.address_type, "address type")

        self.assertEquals(dlda.get_xpath(),
            self._account.get_xpath() + self._account.dldas._xpath +
            dlda._xpath.format(dlda.id))

        url = self._client.config.url + dlda.get_xpath()

        with requests_mock.Mocker() as m:

            m.put(url, status_code = 200, content = XML_RESPONSE_DLDA_GET)

            dlda.save()

            self.assertEquals(m.request_history[0].method, "PUT")

if __name__ == "__main__":
    main()
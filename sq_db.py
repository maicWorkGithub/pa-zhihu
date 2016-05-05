#!/usr/bin/env python3
#  coding: utf-8
import sqlite3
import json
import os


class SqDb:
    def __init__(self):
        self.data_path = os.path.split(os.path.realpath(__file__))[0] + '/data.db'
        self.link_path = os.path.split(os.path.realpath(__file__))[0] + '/link.db'
        self.data_con = sqlite3.connect(self.data_path)
        self.link_con = sqlite3.connect(self.link_path)
        self.data_cor = self.data_con.cursor()
        self.link_cor = self.link_con.cursor()
        self.data_cor.execute("CREATE TABLE IF NOT EXISTS person_dict "
                              "(id INT(20) PRIMARY KEY AUTOINCREMENT,imglist TEXT,title VARCHAR(255), mark varchar(255),tag varchar(31))")
        self.link_cor.execute("CREATE TABLE IF NOT EXISTS links"
                              "(id INT(20) PRIMARY KEY AUTOINCREMENT , link VARCHAR(100), status VARCHAR(20))")


    def save_data(self, data=None):
        pass

    def save_link(self, link=None):
        pass

    def read_data(self):
        pass

    def read_link(self):
        pass

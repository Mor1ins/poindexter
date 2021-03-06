#! /usr/bin/env python
# -*- coding: utf-8 -*-


import os
import re
from Note import Note
from sqlalchemy import create_engine

DB_NAME = "sqlite"
TABLE_NAME = "notes"
DB_NOTES_PATH = "../../../%s.db" % TABLE_NAME
CONNECTING_STRING = "%s:///%s" % (DB_NAME, "%s")
notes_fields = """
    note_id integer primary key,
    faculty varchar,
    graduate varchar,
    course_name varchar,
    study_year integer,
    lecture_name varchar,
    total_year integer,
    semester integer,
    url varchar
"""
inserting_fields = """
    faculty, graduate, course_name, study_year, lecture_name, total_year, semester, url
"""
create_table_query = "create table %s (%s)" % ("%s", notes_fields)
insert_query = 'insert into %s(%s) values (%s)' % ("%s", inserting_fields, "%s")
update_query = "update %s set url='%s' where url='%s'"
select_query = 'select %s from %s'

format_dir = r'(\w+)\s+(\d)(\d)\s+(\w+),\s+(\w+\s*\w*),\s+(\w+)\s+(\w+),\s+(\d+)'


# trans_set_query = 'SET TRANSACTION %s'
# trans_autocommit_query = 'SET autocommit=&d'

class Checker:
    @staticmethod
    def check_title(title, template=format_dir):
        return len(re.match(template, title).groups()) == 1


class NotesDB:
    def __init__(self, db_path, table):
        self.table = table
        self.db_path = db_path
        self.engine = create_engine(CONNECTING_STRING % self.db_path)

    def exist(self):
        return os.path.exists(self.db_path)

    def create_table(self):
        self.engine.execute(create_table_query % self.table)

    def remove_table(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def insert_into(self, values):
        query = insert_query % (self.table, values)
        self.engine.execute(query)

    def update_url(self, rand_id, url):
        query = update_query % (self.table, url, rand_id)
        self.engine.execute(query)

    def select_all(self):
        result = self.engine.execute(select_query % (inserting_fields, self.table))
        return result.fetchall()


if __name__ == "__main__":
    db = NotesDB(DB_NOTES_PATH, TABLE_NAME)
    db.open()
    db.remove_table()
    db.create_table()

    dirs = os.listdir("../../../out")
    for dir in dirs:
        matches = re.findall(format_dir, dir, re.U)
        if len(matches) > 0:
            db.insert_into(Note.from_list(matches[0]).__str__())

    for note in db.select_all():
        print(note)

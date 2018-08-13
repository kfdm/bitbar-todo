import os
import configparser
import requests
import sys
import collections
import logging

if "BitBar" not in os.environ:
    logging.basicConfig(level=logging.DEBUG)
else:
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf8")

config = configparser.ConfigParser()
with open(os.path.expanduser("~/.bitbarrc")) as fp:
    config.read_file(fp)


class Task(object):
    def __init__(self, data):
        self.data = data

    def format(self, prefix=""):
        yield prefix
        yield "({priority}) {title}".format(**self.data)
        if self.data.get("due"):
            yield " [" + self.data["due"] + "]"
        yield "\n"
        if "external" in self.data:
            yield prefix
            yield "({priority}) {title}".format(**self.data)
            yield "|  alternate=true href={external}".format(**self.data)
            yield "\n"


def main():
    print(":card_index:")
    print("---")
    print("RELOAD | refresh=true")
    print("---")
    response = requests.get(
        config["todo"]["query"],
        headers={"Authorization": "Token " + config["todo"]["token"]},
    )
    response.raise_for_status()

    groups = collections.defaultdict(list)
    for todo in response.json():
        # Separate tasks with due dates from the other
        # open tasks
        if todo.get("due") and todo["status"] == 1:
            groups[0].append(Task(todo))
        else:
            groups[todo["status"]].append(Task(todo))

    for todo in groups[0]:
        for line in todo.format():
            sys.stdout.write(line)

    print("Unscheduled")
    for todo in groups[1]:
        for line in todo.format('-- '):
            sys.stdout.write(line)

    print("Completed")
    for todo in groups[2]:
        for line in todo.format('-- '):
            sys.stdout.write(line)


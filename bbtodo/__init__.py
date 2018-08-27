import os
import configparser
import requests
import sys
import collections
import logging
import datetime

if "BitBar" not in os.environ:
    logging.basicConfig(level=logging.DEBUG)
else:
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf8")


class ANSI:
    red = '\033[1;31m'
    green = '\033[1;32m'
    blue = '\033[1;34m'
    yellow = '\033[1;33m'
    reset = '\033[0m'

now = datetime.datetime.utcnow()
config = configparser.ConfigParser()
with open(os.path.expanduser("~/.bitbarrc")) as fp:
    config.read_file(fp)


class Task(object):
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data[key]

    def format(self, prefix=""):
        yield prefix

        if self.data["priority"] > 7:
            yield ANSI.red
        elif self.data["priority"] > 5:
            yield ANSI.yellow

        yield "(%s) " % self.data["priority"]
        yield ANSI.reset

        if "project" in self.data:
            yield "#%s " % self.data["project"]["title"]

        yield self.data["title"]

        if self.data.get("due"):
            due = datetime.datetime.strptime(self.data["due"], "%Y-%m-%d")
            if due < now:
                yield ANSI.red
            yield " [%s] " % self.data["due"]
            if due < now:
                yield '!!!'
            yield ANSI.reset

        yield "|"

        yield "\n"
        if "external" in self.data:
            yield "--"
            yield prefix
            yield self.data["external"]
            # yield "({priority}) {title}".format(**self.data)
            yield "|  alternate=true href={external}".format(**self.data)
            yield "\n"


def main():
    print(":card_index:")
    print("---")
    print("RELOAD | refresh=true")
    print("---")
    response = requests.get(
        config["todo"]["query"],
        headers={
            "Authorization": "Token " + config["todo"]["token"],
            "User-Agent": "bitbar-todo",
        },
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

    for todo in sorted(groups[0], key=lambda t: t["priority"], reverse=True):
        for line in todo.format():
            sys.stdout.write(line)

    print("Unscheduled")
    for todo in sorted(groups[1], key=lambda t: t["priority"], reverse=True):
        for line in todo.format("-- "):
            sys.stdout.write(line)

    print("Completed")
    for todo in sorted(groups[2], key=lambda t: t["priority"], reverse=True):
        for line in todo.format("-- "):
            sys.stdout.write(line)


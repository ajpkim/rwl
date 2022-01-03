import argparse
import csv
import datetime

import pandas as pd

"""
TODO
- view() options
- updating status of list items once completed
  - need some type of searching and interactive editing capabilities

Overview
- rwl is a tool for recording things I read, watch, and listen to
- the objective is to have an efficient method for capturing simple data about the content I take in
- Initial build will just write to a csv
"""

DATAFILE = "/home/ajpkim/code/rwl/rwl/rwl_data.csv"
COLS = [
    "type",
    "title",
    "creator",
    "date",
    "timestamp",
    "published",
    "note",
    "url",
    "rating",
    "status",
]
TYPES = [
    "book",
    "essay",
    "paper",
    "movie",
    "video",
    "podcast",
]


def clean_kwargs(kwargs):
    kwargs = {k: v for (k, v) in kwargs.items() if k in COLS}
    for col in COLS:
        if col not in kwargs:
            kwargs[col] = None
    return kwargs


def add_record(*args, **kwargs):
    with open(DATAFILE, "a") as f:
        writer = csv.DictWriter(f, COLS)
        writer.writerow(kwargs)

    print("------------------------------")
    print("Recorded:")
    for col in COLS:
        print(f"{col:<10} {kwargs[col]}")
    print("------------------------------")


def view_recent(n=10, content_type=None):
    df = pd.read_csv(DATAFILE)
    if content_type:
        df = df.loc[df["type"] == content_type]
    print(df.tail(n))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    options_parent_parser = argparse.ArgumentParser(add_help=False)
    options_parent_parser.add_argument("-c", "--creator", type=str)
    options_parent_parser.add_argument("-n", "--note", type=str)
    options_parent_parser.add_argument("-p", "--published", type=str)
    options_parent_parser.add_argument("-r", "--rating", type=float)
    options_parent_parser.add_argument("-u", "--url", type=str)

    add_list_parent_parser = argparse.ArgumentParser(add_help=False)
    add_list_parent_parser.add_argument("type", type=str, choices=TYPES)
    add_list_parent_parser.add_argument("title", type=str)

    main_parser = argparse.ArgumentParser()
    subparser = main_parser.add_subparsers(dest="command")

    add_parser = subparser.add_parser(
        "add", parents=[add_list_parent_parser, options_parent_parser]
    )
    add_parser.add_argument(
        "-d", "--date", type=str, default=datetime.datetime.today().strftime("%Y-%m-%d")
    )

    list_parser = subparser.add_parser(
        "list", parents=[add_list_parent_parser, options_parent_parser]
    )

    view_parser = subparser.add_parser("view", parents=[options_parent_parser])
    view_parser.add_argument("-N", "--number", type=int, default=10)
    view_parser.add_argument("-t", "--type", type=str, choices=TYPES, default="book")

    args = main_parser.parse_args()
    kwargs = vars(args)

    if args.command in ["add", "list"]:
        status_timestamp = {
            "status": int(args.command == "add"),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        kwargs.update(status_timestamp)
        kwargs = clean_kwargs(kwargs)
        add_record(**kwargs)

    if args.command == "view":
        view_recent(content_type=args.type)

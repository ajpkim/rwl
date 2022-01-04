import argparse
import csv
import datetime

import pandas as pd

"""
TODO
- view() options
- updating status of list items once completed
  - need some type of searching and interactive editing capabilities
- install in editable mode: https://github.com/python-poetry/poetry/discussions/1135 (NeilGirdhar on Oct 31, 2020)
  - setup.py

Overview
- rwl is a tool for recording things I read, watch, and listen to
- the objective is to have an efficient method for capturing simple data about the content I take in
- Initial build will just write to a csv
"""

DATAFILE = "/home/ajpkim/code/rwl/rwl/rwl_data.csv"
COLS = [
    "category",
    "title",
    "creator",
    "date",
    "timestamp",
    "published",
    "note",
    "url",
    "rating",
    "finished",
]
CATEGORIES = [
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


def view_recent(n=10, shelf=False, category=None):
    df = pd.read_csv(DATAFILE)
    df = df.loc[df["finished"] == 0] if shelf else df.loc[df["finished"] == 1]
    if category:
        df = df.loc[df["category"] == category]
    print(df.tail(n))


if __name__ == "__main__":
    options_parent_parser = argparse.ArgumentParser(add_help=False)
    options_parent_parser.add_argument("-c", "--creator", metavar="", type=str)
    options_parent_parser.add_argument("-n", "--note", metavar="", type=str)
    options_parent_parser.add_argument("-p", "--published", metavar="", type=str)
    options_parent_parser.add_argument("-r", "--rating", metavar="", type=float)
    options_parent_parser.add_argument("-u", "--url", metavar="", type=str)

    add_shelf_parent_parser = argparse.ArgumentParser(add_help=False)
    add_shelf_parent_parser.add_argument(
        "category",
        metavar="Category",
        type=str,
        choices=CATEGORIES,
        help=f"{CATEGORIES}",
    )
    add_shelf_parent_parser.add_argument(
        "title", metavar="Title", type=str, help="Title of material"
    )

    main_parser = argparse.ArgumentParser()
    subparser = main_parser.add_subparsers(dest="command")

    add_parser = subparser.add_parser(
        "add",
        description="Record finished items",
        parents=[add_shelf_parent_parser, options_parent_parser],
    )
    add_parser.add_argument(
        "-d",
        "--date",
        metavar="",
        type=str,
        default=datetime.datetime.today().strftime("%Y-%m-%d"),
    )

    shelf_parser = subparser.add_parser(
        "shelf",
        description="Shelve material for later",
        parents=[add_shelf_parent_parser, options_parent_parser],
    )

    view_parser = subparser.add_parser(
        "view",
        description="View recorded data on finished and shelved items",
        parents=[options_parent_parser],
    )
    view_parser.add_argument(
        "content",
        metavar="Type of entries",
        choices=["fin", "shelf"],
        help="[fin, shelf]",
    )
    view_parser.add_argument(
        "category",
        metavar="Category",
        nargs="*",
        choices=CATEGORIES,
        help=f"{CATEGORIES}",
    )
    view_parser.add_argument("-N", "--number", type=int, default=10)

    args = main_parser.parse_args()
    kwargs = vars(args)

    if args.command in ["add", "shelf"]:
        status_timestamp = {
            "finished": int(args.command == "add"),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        kwargs.update(status_timestamp)
        kwargs = clean_kwargs(kwargs)
        add_record(**kwargs)

    if args.command == "view":
        shelf = args.content == "shelf"
        view_recent(n=args.number, shelf=shelf, category=args.category)

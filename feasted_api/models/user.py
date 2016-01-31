import json
from collections import namedtuple
from operator import xor
from typing import Optional

import rethinkdb as rdb
from tornado import gen

User = namedtuple('User', [
    'user_id',
    'name',
])


@gen.coroutine
def create_user(user_id, db_conn) -> Optional[User]:
    resp = yield rdb.table("users"). \
        insert(
            {"id": user_id, "is_active": False},
            durability='hard', return_changes='always'). \
        run(db_conn)
    if resp.get("inserted", 0) == 1:
        return resp.get("changes", {}).get("new_val", None)
    else:
        return None


@gen.coroutine
def delete_user(user_id, db_conn) -> Optional[User]:
    resp = yield rdb.table("users"). \
        get(user_id). \
        delete(durability='hard', return_changes='always'). \
        run(db_conn)
    if resp.get("deleted", 0) == 1:
        return resp.get("changes", {}).get("old_val", None)
    else:
        return None


@gen.coroutine
def get_user(user_id, db_conn) -> Optional[User]:
    user = yield rdb.table("users").get(user_id).run(db_conn)
    return user


@gen.coroutine
def make_user_inactive(user_id, db_conn) -> Optional[User]:
    user = yield update_user(user_id, {"is_active": False}, db_conn)
    return user


def parse_user_from_json(string) -> Optional[User]:
    try:
        user = json.loads(string)
    except json.JSONDecodeError:
        return None
    return user


@gen.coroutine
def update_user(user_id, user, db_conn) -> Optional[User]:
    resp = yield rdb.table("users"). \
        get(user_id). \
        update(user, durability='hard', return_changes='always'). \
        run(db_conn)
    if xor((resp.get("replaced", 0) == 1), (resp.get("unchanged", 0) == 1)):
        return resp.get("changes", {}).get("new_val", None)
    else:
        return None
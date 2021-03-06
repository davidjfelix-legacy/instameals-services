from operator import xor
from typing import Optional, List, Dict, Tuple

import rethinkdb as rdb
from tornado import gen

from ..models.base import BaseModel


@gen.coroutine
def delete(table: str, model_id, db_conn) -> Optional[Dict]:
    resp = yield rdb.table(table). \
        get(model_id). \
        delete(durability='hard', return_changes='always'). \
        run(db_conn)
    if resp.get("deleted", 0) == 1:
        changes = resp.get("changes", [])
        return changes[0].get("old_val", None) if len(changes) == 1 else None
    else:
        return None


@gen.coroutine
def get(table: str, model_id, db_conn) -> Optional[Dict]:
    resp = yield rdb.table(table).get(model_id).run(db_conn)
    return resp if resp else None


@gen.coroutine
def get_nearest(table: str,
                db_conn,
                lng_lat: Tuple[float, float] = (-84.51, 39.10),
                max_dist: int = 10,
                unit: str = 'mi',
                max_results: int = 20) -> List[Dict]:
    resp = yield rdb.table(table). \
        get_nearest(rdb.point(*lng_lat),
                    index='location',
                    max_dist=max_dist,
                    unit=unit,
                    max_results=max_results). \
        run(db_conn)
    if len(resp) > 0:
        models = []
        for item in resp:
            doc = item.get('doc')
            if doc:
                models.append(doc)
        return models
    else:
        return []


@gen.coroutine
def insert(table: str, model: Dict, db_conn) -> Optional[Dict]:
    resp = yield rdb.table(table). \
        insert(
            model,
            durability='hard', return_changes='always'). \
        run(db_conn)

    if resp.get("inserted", 0) == 1:
        changes = resp.get('changes', [])
        return changes[0].get('new_val', None) if len(changes) == 1 else None
    else:
        return None


@gen.coroutine
def update(model: BaseModel, db_conn) -> Optional[Dict]:
    resp = yield rdb.table(model.table). \
        get(model.model_id). \
        update(model.values, durability='hard', return_changes='always'). \
        run(db_conn)
    if xor((resp.get("replaced", 0) == 1), (resp.get("unchanged", 0) == 1)):
        changes = resp.get("changes", [])
        return changes[0].get("new_val", None) if len(changes) == 1 else None
    else:
        return None


@gen.coroutine
def upsert(model: BaseModel, db_conn) -> Optional[Dict]:
    resp = yield rdb.table(model.table). \
        insert(
            model.values,
            durability='hard', return_changes='always', conflict='update'). \
        run(db_conn)

    # FIXME: or updated
    if resp.get("inserted", 0) == 1:
        changes = resp.get('changes', [])
        return changes[0].get('new_val', None) if len(changes) == 1 else None
    else:
        return None

@gen.coroutine
def get_all_and_order_by(table: str, order_attribute: str, db_conn) -> List[Dict]:
    resp = yield rdb.table(table).order_by(order_attribute).run(db_conn)
    if len(resp) > 0:
        models = []
        for item in resp:
            models.append(item)
        return models
    else:
        return []

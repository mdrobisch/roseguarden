__author__ = 'drobisch'

from sqlalchemy import func

def get_query_count(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count
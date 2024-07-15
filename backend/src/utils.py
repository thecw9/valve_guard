from src.orm_model import Measures
from src.db import engine
from sqlalchemy.orm import Session


def get_realtime_data(keys: list[int], session: Session) -> dict[int, float]:
    """
    Retrieve realtime data

    Args:
        keys (list[int]): measure keys

    Returns:
        dict[int, float]: realtime data with measure key as key and data as value
    """
    print(keys)
    query = session.query(Measures).filter(Measures.key.in_(keys))
    data = query.all()
    return {item.key: item.value for item in data}


if __name__ == "__main__":
    session = Session(engine)
    keys = [4222125155614726, 4222125155680262, 4222125156139014, 4222125156204550]
    print(get_realtime_data(keys, session))

"""Customer-support memory and LangGraph persistence resources.

All PostgreSQL connection management for LangGraph lives in this helper.
The database schema is set up by a separate deployment service; this module
never calls ``PostgresSaver.setup()`` or ``PostgresStore.setup()``.

Environment variables (injected by Docker Compose / Kubernetes):
    DB_USER, DB_PASSWORD, DB_MEMORY_DATABASE
    DB_MEMORY_HOST (falls back to DB_HOST)
    DB_MEMORY_PORT (default 5432)
    DB_SSLMODE (default disable; configure TLS in production)
    LANGGRAPH_POOL_MIN_SIZE (default 0)
    LANGGRAPH_POOL_MAX_SIZE (default 2)
    LANGGRAPH_POOL_TIMEOUT (default 10 seconds)

Memory storage connects directly to PostgreSQL by default, rather than the
PgBouncer transaction-pooling endpoint used by business read tools.
"""



import atexit
import logging
import os
import threading
from dataclasses import dataclass

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)


def _memory_conninfo() -> str:
    """Construct a safe libpq conninfo string from container environment."""
    host = os.getenv("DB_MEMORY_HOST") or os.environ["DB_HOST"]
    return make_conninfo(
        host=host,
        port=os.getenv("DB_MEMORY_PORT", "5432"),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        dbname=os.environ["DB_MEMORY_DATABASE"],
        sslmode=os.getenv("DB_SSLMODE", "disable"),
        connect_timeout=10,
    )


# Keep this public name for existing integrations. Computing a DSN does not
# open a connection; the pool is opened only when a helper is first used.
DB_URI = _memory_conninfo()


@dataclass
class _PersistenceResources:
    pid: int
    pool: ConnectionPool
    checkpointer: PostgresSaver
    store: PostgresStore


_resources: _PersistenceResources | None = None
_resources_lock = threading.RLock()


def get_langgraph_persistence() -> tuple[PostgresSaver, PostgresStore]:
    """Return process-local checkpointer and store backed by one Psycopg pool.

    Pools are created lazily in the calling Celery child process, never
    eagerly in the parent process at module import time.

    Psycopg pool recovery -> Celery task recovery -> Permanent failure
    """
    global _resources

    pid = os.getpid()
    resources = _resources
    if resources is not None and resources.pid == pid and not resources.pool.closed:
        return resources.checkpointer, resources.store

    with _resources_lock:
        resources = _resources
        if resources is not None and resources.pid == pid and not resources.pool.closed:
            return resources.checkpointer, resources.store

        min_size = int(os.getenv("LANGGRAPH_POOL_MIN_SIZE", "0"))
        max_size = int(os.getenv("LANGGRAPH_POOL_MAX_SIZE", "2"))
        timeout = float(os.getenv("LANGGRAPH_POOL_TIMEOUT", "10"))
        reconnect_timeout = 30


        if not 0 <= min_size <= max_size or max_size < 1:
            raise ValueError("Invalid LANGGRAPH_POOL_MIN_SIZE / LANGGRAPH_POOL_MAX_SIZE")
        if timeout <= 0:
            raise ValueError("LANGGRAPH_POOL_TIMEOUT must be positive")

        pool = ConnectionPool(
            conninfo=DB_URI,
            min_size=min_size,
            max_size=max_size,
            timeout=timeout,
            reconnect_timeout=reconnect_timeout,
            check=ConnectionPool.check_connection, # validate connections before handling to application
            kwargs={
                "autocommit": True,
                "row_factory": dict_row,
                "prepare_threshold": None,
            },
            open=False,
            name=f"langgraph-memory-{pid}",
        )
        # Reuse pool if it can be reopened, if not close it and raise 
        # ConnectionPool handles recovery behaviour https://www.psycopg.org/psycopg3/docs/advanced/pool.html including opening new connections
        try:
            pool.open(wait=False)
            checkpointer = PostgresSaver(pool)
            store = PostgresStore(pool)
        except Exception:
            pool.close()
            logger.exception(
                "Failed to initialize LangGraph persistence resources"
            )
            raise

        _resources = _PersistenceResources(pid, pool, checkpointer, store)
        logger.info("LangGraph persistence pool initialized | pid=%s | max_size=%s", pid, max_size)
        return checkpointer, store


def close_langgraph_persistence() -> None:
    """Close only this process's pool, on normal shutdown."""
    global _resources
    with _resources_lock:
        resources = _resources
        if resources is None or resources.pid != os.getpid():
            return
        _resources = None
        resources.pool.close()
        logger.info("LangGraph persistence pool closed | pid=%s", os.getpid())


atexit.register(close_langgraph_persistence)

# Celery is optional for non-worker programs that import this helper.
try:
    from celery.signals import worker_process_shutdown
except ImportError:
    pass
else:
    @worker_process_shutdown.connect(weak=False)
    def _close_on_worker_shutdown(**kwargs):
        close_langgraph_persistence()

"""
https://reference.langchain.com/python/langgraph/store/#langgraph.store.postgres.PostgresStore

In this memory storage:
namespace : (email_conversation_history, {customer_id})
key: {case_id}
"""

def _location(customer_id: int, case_id: int) -> tuple[tuple[str, str], str]:
    """Preserve the existing memory namespace/key convention."""
    return ("email_conversation_history", str(customer_id)), str(case_id)


def read_customer_support_history(customer_id: int, case_id: int) -> dict | None:
    namespace, key = _location(customer_id, case_id)
    _, store = get_langgraph_persistence()
    result = store.get(namespace=namespace, key=key)
    return result.value if result is not None else None


def update_customer_support_history(
    customer_id: int,
    case_id: int,
    message: str,
    message_history: dict,
    from_customer: bool = True,
):
    """Append supplied message to caller-provided history and persist it.

    Preserves existing signature and key numbering. This is not an atomic
    append: concurrent tasks updating one case still require coordination.
    """
    assert message_history is None or isinstance(message_history, dict)
    namespace, key = _location(customer_id, case_id)
    memory_value = f"{message}"

    if not message_history:
        message_history = {"0": memory_value}
    else:
        message_history[str(len(message_history))] = memory_value

    _, store = get_langgraph_persistence()
    store.put(namespace, key, message_history)


def delete_customer_support_history(customer_id: int, case_id: int):
    namespace, key = _location(customer_id, case_id)
    _, store = get_langgraph_persistence()
    store.delete(namespace, key)


def add_customer_support_history(customer_id: int, case_id: int, value: dict):
    namespace, key = _location(customer_id, case_id)
    _, store = get_langgraph_persistence()
    store.put(namespace, key, value)


if __name__ == "__main__":
    delete_customer_support_history(404, 404)
    print(read_customer_support_history(404, 404))

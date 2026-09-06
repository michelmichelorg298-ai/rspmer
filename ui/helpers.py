import streamlit as st


def safe_index(options: list, value, default: int = 0) -> int:
    try:
        return options.index(value)
    except ValueError:
        return default


def invalidate_cache(*keys: str) -> None:
    for key in keys:
        st.session_state.pop(key, None)


def mark_list_stale(list_key: str) -> None:
    st.session_state[f"{list_key}_loaded"] = False


def get_cached_list(list_key: str, fetch_fn):
    loaded_key = f"{list_key}_loaded"
    if not st.session_state.get(loaded_key):
        st.session_state[list_key] = fetch_fn()
        st.session_state[loaded_key] = True
    return st.session_state.get(list_key, [])


def rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

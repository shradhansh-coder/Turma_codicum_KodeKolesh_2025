import traceback, sys

try:
    import app  # noqa: F401
    print("IMPORT_OK")
except Exception:
    traceback.print_exc()
    sys.exit(1)

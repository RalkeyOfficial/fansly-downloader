from time import sleep as s

# mostly used to attempt to open fansly downloaders documentation
def open_url(url_to_open: str):
    s(10)
    try:
        import webbrowser
        webbrowser.open(url_to_open, new=0, autoraise=True)
    except Exception:
        pass
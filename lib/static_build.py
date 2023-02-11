#
# little script used to build static pages
#
__author__ = "IU1BOW - Corrado"
import sys
from staticjinja import Site

def csrf_token():
    return "none"

if __name__ == "__main__":
    print (sys.argv)
    site = Site.make_site(
        searchpath=sys.argv[1],
        outpath=sys.argv[2],
        env_globals={
            "cookies_check": False,
            "csrf_token": csrf_token,
            "telnet": "none",
            "mail": "none"
        },
    )
    site.render(use_reloader=False)

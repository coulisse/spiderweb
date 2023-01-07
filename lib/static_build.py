#
# little script used to build static pages
#
__author__ = "IU1BOW - Corrado"
from staticjinja import Site


def cookies_check():
    return False


if __name__ == "__main__":
    site = Site.make_site(
        searchpath="../static/html/dev/",
        outpath="../static/html/rel/",
        env_globals={
            "cookies_check": cookies_check,
        },
    )
    site.render(use_reloader=False)

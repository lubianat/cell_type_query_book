import urllib.parse
import yaml
import requests
import re
from mdutils.mdutils import MdUtils
from pathlib import Path

HERE = Path(__file__).parent.resolve()
RESULTS = HERE.parent.joinpath("results").resolve()
DOCS = HERE.parent.joinpath("docs").resolve()


def main():
    html = """
    
    
    <!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Wikidata Bib</title>
    <meta property="og:description" content="powered by Wikidata" />
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous" />
    <link href="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js" rel="stylesheet"
        integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.8.2/css/bulma.min.css" />
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" />
</head>
<body>
    <section class="section">
        <div class="container">
            <div class="columns is-centered">
                <div class="column is-half has-text-centered">
                    <h2 class="title is-2">Overview of Cell Types on Wikidata</h1>
                </div>
            </div>
        </div>
    </section>
    
    
    
     <div class="has-text-centered">
    
    
    
    """

    with open("src/dashboard.yaml", "r") as c:
        config = yaml.load(c.read(), Loader=yaml.FullLoader)

    for query in config["queries"]:
        if query is not None:
            html = update_html(html, query)

    html += """
    
    </div>
    </div>
    <div class="content has-text-centered">
                <br>
                <h4>Credits</h4>
                <p> Source code at <a href="https://github.com/lubianat/cell_type_query_book"> GitHub </a></p>
                <p>
                    This content is available under a  <a target="_blank" href="https://creativecommons.org/publicdomain/zero/1.0/">  Creative Commons CC0</a> license. 
                </p>
            </div>
    </body>
    
    </html>
    
    """
    HERE.parent.joinpath("index.html").write_text(html)


def update_html(html, query):
    title, sparql_query = get_sparql_from_shortened_wiki_url(query)
    iframe = render_embedding_iframe(sparql_query)
    html += f' <h3  class="title is-3"> {title} </h2>\n'
    html += f"{iframe}\n"
    return html


def update_markdown(mdFile, query):
    title, sparql_query = get_sparql_from_shortened_wiki_url(query)
    iframe = render_embedding_iframe(sparql_query)
    mdFile.new_header(2, title)
    mdFile.new_line(iframe)
    mdFile.new_line("")


def get_sparql_from_shortened_wiki_url(wiki_url):
    session = requests.Session()  # so connections are recycled

    full_uri = session.head(wiki_url, allow_redirects=True).url
    sparql_query = urllib.parse.unquote(full_uri.split(".org/")[-1])
    sparql_query = sparql_query.replace("embed.html#", "")
    title_search = re.search("title:(.*)\n", sparql_query, re.IGNORECASE)
    title = title_search.group(1)
    return title, sparql_query


def render_embedding_iframe(query):
    url = render_embedding_url(query)
    return (
        """<iframe style="width: 80%; height: 50vh; border: none;" """
        f"""src="{url}" referrerpolicy="origin" """
        """sandbox="allow-scripts allow-same-origin allow-popups"></iframe>"""
    )


def render_embedding_url(query):
    return "https://query.wikidata.org/embed.html#" + urllib.parse.quote(query, safe="")


if __name__ == "__main__":
    main()

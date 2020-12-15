import pysolr
import json
import pandas as pd
import logging
from datetime import datetime

# CLI command that deletes all data from a core:
# curl -X POST -H 'Content-Type: application/json' --data-binary '{"delete":{"query":"*:*" }}' http://localhost:8983/solr/news_de/update

class SolrHandler:
    def __init__(self, lang=None):
        self.solr = {"DE": pysolr.Solr('http://localhost:8983/solr/news_de/', always_commit=False, timeout=10),
                     "EN": pysolr.Solr('http://localhost:8983/solr/news_en/', always_commit=False, timeout=10)}
        self.lang = None
        self.set_lang(lang=lang)

    def status(self, lang="DE"):
        solr = self.solr[lang] if lang else self.solr[self.lang]
        try:
            return True if json.loads(solr.ping())["status"] == "OK" else False
        except Exception as e:
            print("\nSolrHandler.status(): can not reach solr server, error:", e)
            return False

    def set_lang(self, lang=None):
        self.lang = lang if lang in ["DE", "EN"] else self.lang

    def commit(self):
        for core in self.solr.values():
            core.commit()

    def update(self, data=None, lang=None):
        print("SolrHandler.update():")

        self.set_lang(lang=lang)
        if self.lang not in ["DE", "EN"]:
            return
        solr = self.solr[self.lang]

        if isinstance(data, dict):
            try:
                solr.add(data)
            except:
                logging.warning("Could not add data to Solr!")

        elif isinstance(data, pd.DataFrame) and data.shape[0] > 0: #and self.status(lang):
            for row in data.to_dict("index").values():
                try:
                    solr.add(row)
                except:
                    logging.warning("Could not add row to Solr!")
        print("\tchanges committed to solr.")

    def delete(self, data=None, lang=None):
        print("SolrHandler.delete()")

        self.set_lang(lang=lang)
        if self.lang not in ["DE", "EN"]:
            return
        solr = self.solr[self.lang]

        if isinstance(data, dict) and "id" in data.keys():
            id_ = data["id"]
            if id_:
                solr.delete(id=data["id"])

        elif isinstance(data, pd.DataFrame) and data.shape[0] > 0 and self.status(lang):
            for id_ in data.index:
                solr.delete(id=id_)
        else:
            solr.delete(id=data)

        print("\tchanges committed to solr.")

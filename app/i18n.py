# -*- coding: utf-8 -*-
import json

def load_translations(i18n_file_path):
    with open(i18n_file_path, encoding="utf-8") as f:
        return json.load(f)


def make_translator(translations: dict):
    def t(key: str):
        return translations.get(key, key)
    return t

#!/usr/bin/python3

from googletrans import Translator

async def traduzir_texto(texto, destino='pt'):
    translator = Translator()
    traducao = translator.translate(texto, dest=destino)
    return traducao.text
from googletrans import Translator 

async def traduzir_texto(texto: str) -> str:
    destino='pt'
    translator = Translator()
    traducao = translator.translate(texto, dest=destino)
    return traducao 
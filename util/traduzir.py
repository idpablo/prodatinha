from googletrans import Translator # pyright: ignore

async def traduzir_texto(texto: str) -> str:
    destino='pt'
    translator = Translator()
    traducao = translator.translate(texto, dest=destino)
    return traducao # pyright: ignore
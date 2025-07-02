import re
import os
import fitz 
import spacy

# Verificação simples de CPF e Telefone
def simple_find(filename):
    caminho_arquivo = os.path.join('data', filename)
    nome_arquivo, ext = os.path.splitext(filename)
    caminho_saida = os.path.join('output', f"{nome_arquivo}_tarjado{ext}")

    doc = fitz.open(caminho_arquivo)

    padroes = [
        (r'\d{3}\.\d{3}\.\d{3}-\d{2}', "XXX.XXX.XXX-XX"),  # CPF
        (r'\d{2}\.\d{3}\.\d{3}-\d{1}', "XX.XXX.XXX-X"),    # RG
        (r'\(\d{2}\)\s?\d{4,5}-\d{4}', "(XX) XXXXX-XXXX"), # Telefone
    ]


    for pagina in doc:
        texto_pagina = pagina.get_text()

        for padrao, texto_substituto in padroes:
            for match in re.findall(padrao, texto_pagina):

                areas = pagina.search_for(match, quads=True)
                for quad in areas:
                    rect = quad.rect

                    # Reduz a altura da tarja (ex: de 10pt para 8.5pt)
                    reducao_altura = 9.0
                    rect.y0 += reducao_altura / 2
                    rect.y1 -= reducao_altura / 2

                    pagina.add_redact_annot(rect, fill=(0, 0, 0), text=texto_substituto)
                    pagina.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    doc.save(caminho_saida)
    print(f"Novo arquivo gerado: {caminho_saida}")

# Verificação profunda usando machine learning
def extensive_find(filename):
    import fitz
    nlp = spacy.load("pt_core_news_lg")
    caminho_saida = os.path.join('output', f"{os.path.splitext(filename)[0]}_tarjado_extensivo.pdf")
    doc = fitz.open(os.path.join('output', f"{os.path.splitext(filename)[0]}_tarjado.pdf"))

    entidades_sensiveis = ["PER", "LOC", "ORG", "DATE"]  # Pessoa, Local, Organização, Data

    for pagina in doc:
        texto_pagina = pagina.get_text()
        doc_spacy = nlp(texto_pagina)
        for ent in doc_spacy.ents:
            if ent.label_ in entidades_sensiveis:
                for match in re.findall(re.escape(ent.text), texto_pagina):
                    areas = pagina.search_for(match)
                    for area in areas:
                        pagina.add_redact_annot(area, fill=(0, 0, 0), text="[DADO SENSÍVEL]")
        pagina.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    doc.save(caminho_saida)
    print(f"Arquivo extensivamente anonimizado: {caminho_saida}")

# processar o texto do PDF
def process_text(filename):
    simple_find(filename)
    #extensive_find(filename)

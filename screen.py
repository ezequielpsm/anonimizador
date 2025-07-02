import os
import flet as ft
import shutil
import subprocess
import platform
from modules import read  # ou qualquer que seja o módulo que tenha `process_text`

def main(page: ft.Page):
    page.title = "Anonimizador de Dados Pessoais"
    page.theme_mode = "light"
    page.scroll = ft.ScrollMode.AUTO

    nome_arquivo_copiado = ft.Ref[str]()

    arquivo = ft.Text("Nenhum arquivo selecionado", size=14)
    status = ft.Text("", size=14, color="green")

    botao_abrir_pdf = ft.ElevatedButton("📂 Abrir PDF", visible=False)

    def abrir_pdf(filepath):
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":
            subprocess.run(["open", filepath])
        else:
            subprocess.run(["xdg-open", filepath])

    def selecione_arquivo(e: ft.FilePickerResultEvent):
        if e.files:
            original_caminho = e.files[0].path
            nome_arquivo = os.path.basename(original_caminho)
            pasta_destino = "data"
            os.makedirs(pasta_destino, exist_ok=True)
            destino_caminho = os.path.join(pasta_destino, nome_arquivo)
            try:
                shutil.copy(original_caminho, destino_caminho)
                nome_arquivo_copiado.current = nome_arquivo
                arquivo.value = f"Selecionado: {nome_arquivo} (copiado para '{pasta_destino}/')"
                status.value = ""
                botao_abrir_pdf.visible = False
                botao_abrir_pdf.on_click = None
                page.update()
            except Exception as err:
                status.value = f"Erro ao copiar arquivo: {err}"
                page.update()

    abrir_geren = ft.FilePicker(on_result=selecione_arquivo)
    page.overlay.append(abrir_geren)

    def anonimizar_pdf(e):
        if not nome_arquivo_copiado.current:
            status.value = "Nenhum arquivo selecionado para anonimizar."
            page.update()
            return

        try:
            status.value = "Anonimizando... aguarde."
            page.update()
            os.makedirs("output", exist_ok=True)

            read.read_pdf(nome_arquivo_copiado.current)


            # CORREÇÃO: Cria nome de saída dinâmico
            nome_base, extensao = os.path.splitext(nome_arquivo_copiado.current)
            nome_arquivo_saida = f"{nome_base}_tarjado{extensao}"
            caminho_saida = os.path.join("output", nome_arquivo_saida)

            if os.path.exists(caminho_saida):
                status.value = "Anonimização concluída! Clique em 'Abrir PDF'."
                botao_abrir_pdf.visible = True
                botao_abrir_pdf.on_click = lambda _, path=caminho_saida: abrir_pdf(path)
            else:
                status.value = f"Erro: o PDF '{nome_arquivo_saida}' não foi gerado."
                botao_abrir_pdf.visible = False
                botao_abrir_pdf.on_click = None
            page.update()

        except Exception as err:
            status.value = f"Erro na anonimização: {err}"
            page.update()

    header = ft.Text("ANONIMIZADOR DE DADOS PESSOAIS", size=24, weight="bold", color="blue")
    descricao = ft.Text("Este programa lê um arquivo PDF e remove dados sensíveis.", size=16)

    botao_importar = ft.ElevatedButton(
        "Importar PDF",
        on_click=lambda _: abrir_geren.pick_files(
            dialog_title="Selecione um arquivo PDF",
            allow_multiple=False,
            allowed_extensions=["pdf"]
        )
    )
    botao_anonimizar = ft.ElevatedButton("🔐 Anonimizar", on_click=anonimizar_pdf)

    page.add(
        header,
        descricao,
        arquivo,
        status,
        ft.Row([botao_importar, botao_anonimizar, botao_abrir_pdf]),
    )

ft.app(target=main)
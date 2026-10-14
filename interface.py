import json
import os
import queue
import re
import threading
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText

import automatizador

ARQUIVO_CONFIG = "config.json"
ARQUIVO_TOTAL = "total.txt"   # perfis seguidos somando todas as execuções
ARQUIVO_LOG = "log.txt"
LINHAS_LOG = 300              # linhas mostradas na tela


def lerTotalGeral():
    try:
        with open(ARQUIVO_TOTAL, encoding="utf-8") as f:
            return int(f.read().strip() or 0)
    except (FileNotFoundError, ValueError):
        return 0


def salvarTotalGeral(total):
    with open(ARQUIVO_TOTAL, "w", encoding="utf-8") as f:
        f.write(str(total))


def ultimasLinhasLog(quantidade, bytesFim=200_000):
    """Lê só o fim do log.txt (o arquivo pode ficar enorme)"""
    try:
        with open(ARQUIVO_LOG, "rb") as f:
            f.seek(max(0, os.path.getsize(ARQUIVO_LOG) - bytesFim))
            texto = f.read().decode("utf-8", errors="ignore")
    except FileNotFoundError:
        return []
    return [l for l in texto.splitlines() if l.strip()][-quantidade:]


def carregarConfig():
    config = dict(automatizador.CONFIG_PADRAO)
    try:
        with open(ARQUIVO_CONFIG, encoding="utf-8") as f:
            config.update(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    # Configs antigas só tinham "urls": vira a primeira lista
    if not config.get("listas"):
        config["listas"] = {"Principal": list(config.get("urls", []))}
    if config.get("listaAtual") not in config["listas"]:
        config["listaAtual"] = next(iter(config["listas"]))
    return config


def lerUrls(texto):
    urls = [normalizarUrl(l) for l in texto.splitlines()]
    return list(dict.fromkeys(u for u in urls if u))  # remove vazias e repetidas


def normalizarUrl(texto):
    """Aceita 'https://www.instagram.com/perfil/', 'instagram.com/perfil', '@perfil' ou 'perfil'"""
    texto = texto.strip()
    if not texto:
        return ""
    if "instagram.com/" in texto:
        perfil = texto.split("instagram.com/", 1)[1]
    else:
        perfil = texto
    perfil = perfil.lstrip("@").strip("/").split("/")[0].split("?")[0]
    return f"https://www.instagram.com/{perfil}/" if perfil else ""


class Interface:
    def __init__(self, janela):
        self.janela = janela
        self.filaLog = queue.Queue()
        self.parar = threading.Event()
        self.thread = None
        self.totalCliques = 0   # perfis seguidos na execução atual (ou na última)
        self.totalGeral = lerTotalGeral()

        janela.title("Automatizador Instagram")
        janela.geometry("720x780")
        janela.minsize(600, 650)

        config = carregarConfig()
        principal = ttk.Frame(janela, padding=12)
        principal.pack(fill="both", expand=True)

        # ---- Conta ----
        conta = ttk.LabelFrame(principal, text="Conta do Instagram", padding=10)
        conta.pack(fill="x")
        conta.columnconfigure(1, weight=1)

        ttk.Label(conta, text="Usuário:").grid(row=0, column=0, sticky="w", pady=3)
        self.varUsuario = tk.StringVar(value=config.get("usuario", ""))
        ttk.Entry(conta, textvariable=self.varUsuario).grid(row=0, column=1, columnspan=2, sticky="ew", pady=3)

        ttk.Label(conta, text="Senha:").grid(row=1, column=0, sticky="w", pady=3)
        self.varSenha = tk.StringVar(value=config.get("senha", ""))
        self.entradaSenha = ttk.Entry(conta, textvariable=self.varSenha, show="•")
        self.entradaSenha.grid(row=1, column=1, sticky="ew", pady=3)
        self.varMostrar = tk.BooleanVar(value=False)
        ttk.Checkbutton(conta, text="Mostrar", variable=self.varMostrar,
                        command=self.alternarSenha).grid(row=1, column=2, padx=(8, 0))

        self.varLembrar = tk.BooleanVar(value=bool(config.get("senha")))
        ttk.Checkbutton(conta, text="Lembrar senha neste computador (fica salva em config.json)",
                        variable=self.varLembrar).grid(row=2, column=1, columnspan=2, sticky="w")
        ttk.Label(conta, text="Deixe em branco para fazer o login manualmente na janela do navegador.",
                  foreground="gray").grid(row=3, column=0, columnspan=3, sticky="w", pady=(4, 0))

        # ---- Perfis ----
        perfis = ttk.LabelFrame(principal, text="Perfis alvo (um por linha: URL, @perfil ou perfil)", padding=10)
        perfis.pack(fill="both", expand=True, pady=(10, 0))

        self.listas = {nome: list(urls) for nome, urls in config["listas"].items()}
        self.listaAtual = config["listaAtual"]

        barraListas = ttk.Frame(perfis)
        barraListas.pack(fill="x", pady=(0, 6))
        ttk.Label(barraListas, text="Lista:").pack(side="left")
        self.varLista = tk.StringVar(value=self.listaAtual)
        self.comboListas = ttk.Combobox(barraListas, textvariable=self.varLista, state="readonly", width=25)
        self.comboListas.pack(side="left", padx=5)
        self.comboListas.bind("<<ComboboxSelected>>", self.trocarLista)
        ttk.Button(barraListas, text="Nova", command=self.novaLista).pack(side="left")
        ttk.Button(barraListas, text="Renomear", command=self.renomearLista).pack(side="left", padx=5)
        ttk.Button(barraListas, text="Excluir", command=self.excluirLista).pack(side="left")

        self.textoUrls = ScrolledText(perfis, height=8, wrap="none", font=("Consolas", 10))
        self.textoUrls.pack(fill="both", expand=True)
        self.atualizarListas()

        # ---- Configurações ----
        ajustes = ttk.LabelFrame(principal, text="Configurações", padding=10)
        ajustes.pack(fill="x", pady=(10, 0))

        self.varLimite = tk.IntVar(value=config["limite"])
        self.varPausa = tk.IntVar(value=config["pausaMinutos"])
        self.varEsperaMin = tk.IntVar(value=config["esperaMin"])
        self.varEsperaMax = tk.IntVar(value=config["esperaMax"])
        self.varHeadless = tk.BooleanVar(value=config["headless"])

        campos = [
            ("Seguir por ciclo:", self.varLimite, 1, 200, "perfis"),
            ("Pausa entre ciclos:", self.varPausa, 1, 1440, "minutos"),
            ("Espera mínima:", self.varEsperaMin, 1, 600, "segundos"),
            ("Espera máxima:", self.varEsperaMax, 1, 600, "segundos"),
        ]
        for linha, (rotulo, var, minimo, maximo, unidade) in enumerate(campos):
            ttk.Label(ajustes, text=rotulo).grid(row=linha // 2, column=(linha % 2) * 3, sticky="w", pady=3)
            ttk.Spinbox(ajustes, from_=minimo, to=maximo, textvariable=var, width=6).grid(
                row=linha // 2, column=(linha % 2) * 3 + 1, padx=5, pady=3)
            ttk.Label(ajustes, text=unidade).grid(row=linha // 2, column=(linha % 2) * 3 + 2, sticky="w", padx=(0, 20))
        ttk.Checkbutton(ajustes, text="Navegador invisível (headless)",
                        variable=self.varHeadless).grid(row=2, column=0, columnspan=6, sticky="w", pady=(5, 0))

        # ---- Botões ----
        botoes = ttk.Frame(principal)
        botoes.pack(fill="x", pady=10)
        self.botaoIniciar = ttk.Button(botoes, text="▶ Iniciar", command=self.iniciar)
        self.botaoIniciar.pack(side="left")
        self.botaoParar = ttk.Button(botoes, text="■ Parar", command=self.pararBot, state="disabled")
        self.botaoParar.pack(side="left", padx=5)
        ttk.Button(botoes, text="Salvar configurações", command=self.salvar).pack(side="left")
        self.varStatus = tk.StringVar(value="Parado")
        ttk.Label(botoes, textvariable=self.varStatus, font=("Arial", 10, "bold")).pack(side="right")

        # ---- Total de todas as execuções ----
        barraTotal = ttk.Frame(principal)
        barraTotal.pack(fill="x", pady=(0, 8))
        self.varTotalGeral = tk.StringVar()
        ttk.Label(barraTotal, textvariable=self.varTotalGeral, font=("Arial", 10, "bold")).pack(side="left")
        ttk.Button(barraTotal, text="Zerar", command=self.zerarTotal).pack(side="right")
        self.mostrarTotalGeral()

        # ---- Log (as linhas mais recentes ficam em cima) ----
        quadroLog = ttk.LabelFrame(principal, text="Log", padding=5)
        quadroLog.pack(fill="both", expand=True)
        ttk.Button(quadroLog, text="Limpar", command=self.limparLog).pack(anchor="e", pady=(0, 5))
        self.textoLog = ScrolledText(quadroLog, height=10, state="disabled", font=("Consolas", 9))
        self.textoLog.pack(fill="both", expand=True)
        for linha in ultimasLinhasLog(100):
            self.adicionarAoLog(linha)

        # O bot roda em outra thread: as linhas de log passam por uma fila
        automatizador.ouvinteLog = self.filaLog.put
        janela.protocol("WM_DELETE_WINDOW", self.fechar)
        self.lerLog()

    def alternarSenha(self):
        self.entradaSenha.config(show="" if self.varMostrar.get() else "•")

    # ---- Listas de perfis ----
    def guardarListaAtual(self):
        self.listas[self.listaAtual] = lerUrls(self.textoUrls.get("1.0", "end"))

    def atualizarListas(self):
        """Atualiza o combobox e mostra os perfis da lista selecionada"""
        self.comboListas.config(values=list(self.listas))
        self.varLista.set(self.listaAtual)
        self.textoUrls.delete("1.0", "end")
        self.textoUrls.insert("1.0", "\n".join(self.listas[self.listaAtual]))

    def trocarLista(self, _evento=None):
        self.guardarListaAtual()
        self.listaAtual = self.varLista.get()
        self.atualizarListas()

    def pedirNome(self, titulo, inicial=""):
        nome = simpledialog.askstring(titulo, "Nome da lista:", initialvalue=inicial, parent=self.janela)
        nome = (nome or "").strip()
        if nome and nome != inicial and nome in self.listas:
            messagebox.showerror("Erro", f'Já existe uma lista chamada "{nome}".')
            return ""
        return nome

    def novaLista(self):
        nome = self.pedirNome("Nova lista")
        if not nome:
            return
        self.guardarListaAtual()
        self.listas[nome] = []
        self.listaAtual = nome
        self.atualizarListas()
        self.textoUrls.focus_set()

    def renomearLista(self):
        nome = self.pedirNome("Renomear lista", self.listaAtual)
        if not nome or nome == self.listaAtual:
            return
        self.guardarListaAtual()
        # Recria o dicionário para manter a ordem das listas
        self.listas = {(nome if n == self.listaAtual else n): u for n, u in self.listas.items()}
        self.listaAtual = nome
        self.atualizarListas()

    def excluirLista(self):
        if len(self.listas) == 1:
            messagebox.showerror("Erro", "Precisa existir pelo menos uma lista.")
            return
        if not messagebox.askyesno("Excluir lista", f'Excluir a lista "{self.listaAtual}"?'):
            return
        del self.listas[self.listaAtual]
        self.listaAtual = next(iter(self.listas))
        self.atualizarListas()

    def lerConfig(self):
        """Lê os campos da tela; retorna None se algo estiver inválido"""
        self.guardarListaAtual()
        urls = self.listas[self.listaAtual]
        try:
            config = {
                "usuario": self.varUsuario.get().strip(),
                "senha": self.varSenha.get(),
                "urls": urls,
                "listas": self.listas,
                "listaAtual": self.listaAtual,
                "limite": self.varLimite.get(),
                "pausaMinutos": self.varPausa.get(),
                "esperaMin": self.varEsperaMin.get(),
                "esperaMax": self.varEsperaMax.get(),
                "headless": self.varHeadless.get(),
            }
        except tk.TclError:
            messagebox.showerror("Erro", "As configurações precisam ser números inteiros.")
            return None
        if not urls:
            messagebox.showerror("Erro", f'A lista "{self.listaAtual}" está vazia. Coloque pelo menos um perfil alvo.')
            return None
        if config["esperaMin"] > config["esperaMax"]:
            messagebox.showerror("Erro", "A espera mínima não pode ser maior que a máxima.")
            return None
        if config["limite"] < 1 or config["pausaMinutos"] < 1 or config["esperaMin"] < 1:
            messagebox.showerror("Erro", "Os valores precisam ser maiores que zero.")
            return None
        return config

    def salvar(self, avisar=True):
        config = self.lerConfig()
        if config is None:
            return None
        paraSalvar = dict(config)
        if not self.varLembrar.get():
            paraSalvar["senha"] = ""
        with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
            json.dump(paraSalvar, f, indent=2, ensure_ascii=False)
        # Mostra as URLs já arrumadas
        self.atualizarListas()
        if avisar:
            messagebox.showinfo("Salvo", "Configurações salvas.")
        return config

    def iniciar(self):
        config = self.salvar(avisar=False)
        if config is None:
            return
        self.parar.clear()
        self.totalCliques = 0
        self.thread = threading.Thread(target=self.rodar, args=(config,), daemon=True)
        self.thread.start()
        self.botaoIniciar.config(state="disabled")
        self.botaoParar.config(state="normal")
        self.mostrarRodando()

    def mostrarRodando(self):
        self.varStatus.set(f"🟢 Rodando · {self.totalCliques} seguidos")

    def rodar(self, config):
        # Os avisos do bot passam pela mesma fila do log (a tela só pode mexer na thread dela)
        try:
            automatizador.executar(
                config, self.parar,
                aoPausar=lambda minutos: self.filaLog.put(("pausa", minutos)),
                aoRetomar=lambda: self.filaLog.put(("retomou",)),
                aoSeguir=lambda total: self.filaLog.put(("seguiu", total)),
            )
        except Exception as e:
            self.filaLog.put(f"❌ Erro: {e}\n")
        self.filaLog.put(None)  # avisa que terminou

    def pararBot(self):
        self.parar.set()
        self.botaoParar.config(state="disabled")
        self.varStatus.set("🟡 Parando...")

    def lerLog(self):
        while not self.filaLog.empty():
            item = self.filaLog.get()
            if item is None:
                self.aoTerminar()
            elif isinstance(item, tuple):
                self.tratarAviso(*item)
            else:
                self.adicionarAoLog(item)
        self.janela.after(200, self.lerLog)

    def tratarAviso(self, tipo, valor=None):
        if tipo == "seguiu":
            self.totalCliques = valor
            self.totalGeral += 1
            salvarTotalGeral(self.totalGeral)
            self.mostrarTotalGeral()
            if self.botaoParar.instate(["!disabled"]):
                self.mostrarRodando()
        elif tipo == "pausa":
            volta = (datetime.now() + timedelta(minutes=valor)).strftime("%H:%M")
            self.varStatus.set(f"⏸ Pausa até {volta} · {self.totalCliques} seguidos")
        elif tipo == "retomou":
            # Avisa com som que a pausa acabou
            self.janela.bell()
            if self.botaoParar.instate(["!disabled"]):
                self.mostrarRodando()

    def aoTerminar(self):
        self.botaoIniciar.config(state="normal")
        self.botaoParar.config(state="disabled")
        self.varStatus.set(f"Parado · {self.totalCliques} seguidos" if self.totalCliques else "Parado")

    def adicionarAoLog(self, linha):
        """As linhas mais recentes ficam em cima"""
        # Mensagens com quebras de linha ("***FIM DO PROGRAMA***") viram uma linha só
        umaLinha = re.sub(r"\s*\n\s*", " ", linha).strip()
        if not umaLinha:
            return
        self.textoLog.config(state="normal")
        self.textoLog.insert("1.0", umaLinha + "\n")
        self.textoLog.delete(f"{LINHAS_LOG + 1}.0", "end")
        self.textoLog.see("1.0")
        self.textoLog.config(state="disabled")

    def limparLog(self):
        if not messagebox.askyesno("Limpar log", "Apagar todo o log?"):
            return
        open(ARQUIVO_LOG, "w", encoding="utf-8").close()
        self.textoLog.config(state="normal")
        self.textoLog.delete("1.0", "end")
        self.textoLog.config(state="disabled")

    def mostrarTotalGeral(self):
        self.varTotalGeral.set(f"Total seguido (todas as execuções): {self.totalGeral}")

    def zerarTotal(self):
        if not messagebox.askyesno("Zerar total", f"Zerar o total de {self.totalGeral} perfis seguidos?"):
            return
        self.totalGeral = 0
        salvarTotalGeral(0)
        self.mostrarTotalGeral()

    def fechar(self):
        if self.thread and self.thread.is_alive():
            if not messagebox.askyesno("Sair", "O bot está rodando. Parar e sair?"):
                return
            self.parar.set()
            self.esperarThreadEFechar()
        else:
            self.janela.destroy()

    def esperarThreadEFechar(self):
        # Espera o navegador fechar direito antes de sair
        if self.thread.is_alive():
            self.janela.after(300, self.esperarThreadEFechar)
        else:
            self.janela.destroy()


if __name__ == "__main__":
    janela = tk.Tk()
    Interface(janela)
    janela.mainloop()

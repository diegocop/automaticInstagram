import json
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

import automatizador

ARQUIVO_CONFIG = "config.json"


def carregarConfig():
    config = dict(automatizador.CONFIG_PADRAO)
    try:
        with open(ARQUIVO_CONFIG, encoding="utf-8") as f:
            config.update(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return config


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
        self.textoUrls = ScrolledText(perfis, height=8, wrap="none", font=("Consolas", 10))
        self.textoUrls.pack(fill="both", expand=True)
        self.textoUrls.insert("1.0", "\n".join(config.get("urls", [])))

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

        # ---- Log ----
        quadroLog = ttk.LabelFrame(principal, text="Log", padding=5)
        quadroLog.pack(fill="both", expand=True)
        self.textoLog = ScrolledText(quadroLog, height=10, state="disabled", font=("Consolas", 9))
        self.textoLog.pack(fill="both", expand=True)

        # O bot roda em outra thread: as linhas de log passam por uma fila
        automatizador.ouvinteLog = self.filaLog.put
        janela.protocol("WM_DELETE_WINDOW", self.fechar)
        self.lerLog()

    def alternarSenha(self):
        self.entradaSenha.config(show="" if self.varMostrar.get() else "•")

    def lerConfig(self):
        """Lê os campos da tela; retorna None se algo estiver inválido"""
        urls = [normalizarUrl(l) for l in self.textoUrls.get("1.0", "end").splitlines()]
        urls = list(dict.fromkeys(u for u in urls if u))  # remove vazias e repetidas
        try:
            config = {
                "usuario": self.varUsuario.get().strip(),
                "senha": self.varSenha.get(),
                "urls": urls,
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
            messagebox.showerror("Erro", "Coloque pelo menos um perfil alvo.")
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
        self.textoUrls.delete("1.0", "end")
        self.textoUrls.insert("1.0", "\n".join(config["urls"]))
        if avisar:
            messagebox.showinfo("Salvo", "Configurações salvas.")
        return config

    def iniciar(self):
        config = self.salvar(avisar=False)
        if config is None:
            return
        self.parar.clear()
        self.thread = threading.Thread(target=self.rodar, args=(config,), daemon=True)
        self.thread.start()
        self.botaoIniciar.config(state="disabled")
        self.botaoParar.config(state="normal")
        self.varStatus.set("🟢 Rodando")

    def rodar(self, config):
        try:
            automatizador.executar(config, self.parar)
        except Exception as e:
            self.filaLog.put(f"❌ Erro: {e}\n")
        self.filaLog.put(None)  # avisa que terminou

    def pararBot(self):
        self.parar.set()
        self.botaoParar.config(state="disabled")
        self.varStatus.set("🟡 Parando...")

    def lerLog(self):
        while not self.filaLog.empty():
            linha = self.filaLog.get()
            if linha is None:
                self.botaoIniciar.config(state="normal")
                self.botaoParar.config(state="disabled")
                self.varStatus.set("Parado")
                continue
            self.textoLog.config(state="normal")
            self.textoLog.insert("end", linha)
            self.textoLog.see("end")
            self.textoLog.config(state="disabled")
        self.janela.after(200, self.lerLog)

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

import tkinter as tk

janela = tk.Tk()
janela.title("titulo")
janela.geometry("500x500")

rotulo = tk.Label(janela,text="ola", font=("Arial", 14))
rotulo.pack(pady=20)


entrada = tk.Entry(janela, width=40)
entrada.pack(pady=5)

def mostrarTexto():
    texto = entrada.get()
    rotulo.config(text=f"voce digitou:{texto}")


botao = tk.Button(janela, text="Mostrar Texto", command=mostrarTexto)
botao.pack(pady=10)


opcoes =["opcao 1", "opcao 2", "opcao 3"]
varOpcoes = tk.StringVar(value=opcoes[0])
menu = tk.OptionMenu(janela, varOpcoes, *opcoes)
menu.pack(pady=10)

rotulo2 = tk.Label(janela,text="ola", font=("Arial", 14))
rotulo2.pack(pady=20)

def mostrarOpcoes():
    rotulo2.config(text=f"Escolheu:{varOpcoes.get()}")

botaoMenu = tk.Button(janela, text="confirmar opcao",command=mostrarOpcoes)
botaoMenu.pack(pady=5)


def soma(a, b):
    return a + b

x = soma(2, 3)   # ← clique aqui e ponha o breakpoint
print(x)



janela.mainloop()
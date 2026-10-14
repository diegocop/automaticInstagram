import os
import time
import random
import threading
from datetime import datetime
from playwright.sync_api import sync_playwright

# Função extra chamada a cada linha de log (a interface usa para mostrar o log na tela)
ouvinteLog = None


class Parado(Exception):
    """Lançada quando o usuário aperta "Parar" na interface"""


#playwright codegen https://www.instagram.com/diegocop/
def senhaUsuario(page, usuario, senha, parar):

    # Abre a página de login do Instagram
    page.goto("https://www.instagram.com/accounts/login/")

    if usuario and senha:
        # O Instagram já usou name='username'/'password' e hoje usa 'email'/'pass'
        campoUsuario = "input[name='email'], input[name='username']"
        campoSenha = "input[name='pass'], input[name='password']"

        # Espera os campos aparecerem
        page.wait_for_selector(campoUsuario)
        page.wait_for_selector(campoSenha)

        # Preenche usuário e senha
        page.fill(campoUsuario, usuario)

        time.sleep(1)
        page.fill(campoSenha, senha)

        time.sleep(1)

        # Aperta Enter para entrar
        page.press(campoSenha, "Enter")
    else:
        # Sem credenciais: espera o login manual na janela do navegador
        log("Faça o login manualmente na janela do navegador...")

    # Espera o login terminar (pode pedir código 2FA, sem limite de tempo)
    while not estaLogado(page):
        if parar.is_set():
            raise Parado()
        page.wait_for_timeout(3000)
    log("✅ Login feito.")
    page.wait_for_timeout(5000)


def estaLogado(page):
    """O cookie 'sessionid' só existe quando a conta está logada"""
    return any(c["name"] == "sessionid" for c in page.context.cookies("https://www.instagram.com"))


def clicar_com_mouse(page, locator):
    """Move o mouse até o centro do elemento e clica"""
    box = locator.bounding_box()
    if box:
        x = box["x"] + box["width"] / 2
        y = box["y"] + box["height"] / 2
        page.mouse.move(x, y)
        page.mouse.click(x, y)
        print("Clique realizado!")
        return True
    return False


def esperar(page, segundos, parar):
    """Espera em pedaços de 1s para o botão "Parar" responder rápido"""
    fim = time.time() + segundos
    while time.time() < fim:
        if parar.is_set():
            raise Parado()
        page.wait_for_timeout(min(1000, (fim - time.time()) * 1000))


def esperarTempo(page, config, parar):
    # tempo aleatório entre esperaMin e esperaMax segundos
    espera = random.uniform(config["esperaMin"], config["esperaMax"])
    print(f"Esperando {espera:.2f} segundos...")
    esperar(page, espera, parar)

def log(mensagem, arquivoLog="log.txt"):
  # Pega a hora atual no formato: 2025-09-10 14:30:15
  agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Cria a linha de log
  linha = f"[{agora}] {mensagem}\n"
    # Abre o arquivo em modo append e adiciona a linha
  with open(arquivoLog, "a", encoding="utf-8") as f:
    f.write(linha)
  print(f"[{agora}] {mensagem}\n")
  if ouvinteLog:
    ouvinteLog(linha)

url = [
    "https://www.instagram.com/centralcaprichoso/",
    "https://www.instagram.com/boigarantido/",
    "https://www.instagram.com/canalgarantido/",
    "https://www.instagram.com/portal.garantido/",
    "https://www.instagram.com/garantidoreioficial/",
    "https://www.instagram.com/prince_amodoboi/",
    "https://www.instagram.com/boicaprichoso/",
    "https://www.instagram.com/raca.azul/",
    "https://www.instagram.com/lojacantocaprichoso/",
    "https://www.instagram.com/centralcaprichoso/","https://www.instagram.com/paulo_george__/"
]
'''
,"https://www.instagram.com/matus.kkj/"
,"https://www.instagram.com/pqpmjr/"
,"https://www.instagram.com/matheusgomesdotcom/"
,"https://www.instagram.com/cstr_duda/"
,"https://www.instagram.com/byaorl_/"
,"https://www.instagram.com/julisntss/"
,"https://www.instagram.com/luquezia8/"
,"https://www.instagram.com/limaalicia_xxz/"
,"https://www.instagram.com/vick_tae2013/"
,"https://www.instagram.com/rn_da_rocinhaw/"
,"https://www.instagram.com/_omargama/"
,"https://www.instagram.com/_lyly.px/"
,"https://www.instagram.com/fabriciosimasbrandaos/"
,"https://www.instagram.com/mtm.shiawase/"
,"https://www.instagram.com/_marifhy/"
,"https://www.instagram.com/leticiax_eva/"
,"https://www.instagram.com/carolineedressa/"
,"https://www.instagram.com/cf_daa_gaby/"
,"https://www.instagram.com/pamwstar/"
,"https://www.instagram.com/mariaa_bonifacio/"
,"https://www.instagram.com/boibonitooficial/"
,"https://www.instagram.com/odhayx_agalysteu/"
,"https://www.instagram.com/clarawzf_/"
,"https://www.instagram.com/yz_gaby_sntss/"
,"https://www.instagram.com/o_borari/"
,"https://www.instagram.com/raimundodirceulopes/"
,"https://www.instagram.com/letii_liborio/"
,"https://www.instagram.com/oliveiranilce48/"
,"https://www.instagram.com/nara_castro25/"
,"https://www.instagram.com/alicejordall/"
,"https://www.instagram.com/eriane_ribeiro/"
,"https://www.instagram.com/brunockpb_/"
,"https://www.instagram.com/heloisa_.avinte/"
,"https://www.instagram.com/an4xqx_/"
,"https://www.instagram.com/ninoabrv/"
,"https://www.instagram.com/marciofarias1189/"
,"https://www.instagram.com/luanamacedo595/"
,"https://www.instagram.com/tayanneferreira_/"
,"https://www.instagram.com/julia_bastoos3/"
,"https://www.instagram.com/xaninho11/"
,"https://www.instagram.com/vanderci.brito.125/"
,"https://www.instagram.com/cativoqueiroz/"
,"https://www.instagram.com/dioneifrank/"
,"https://www.instagram.com/vitoriacristina_santana/"
,"https://www.instagram.com/araujoesa/"
,"https://www.instagram.com/sday_ane_/"
,"https://www.instagram.com/oi_jessygonzalez/"
,"https://www.instagram.com/sabrina.babi19/"
,"https://www.instagram.com/viviovr/"
,"https://www.instagram.com/festival_minecraft/"
,"https://www.instagram.com/flecha_daisabelleno/"
,"https://www.instagram.com/thisislucao_/"
,"https://www.instagram.com/mana_ferreira30/"
,"https://www.instagram.com/movimentoencarnado/"
,"https://www.instagram.com/zeina_cristina_/"
,"https://www.instagram.com/loves.isabelle.cunha/"
,"https://www.instagram.com/rn_da_rocinhaw/"
,"https://www.instagram.com/luluh_706/"
,"https://www.instagram.com/anapaulada695/"
,"https://www.instagram.com/angelina.marinho.16/"
,"https://www.instagram.com/carla164487/"
,"https://www.instagram.com/joserobertofiscal/"
,"https://www.instagram.com/v.freitasy/"
,"https://www.instagram.com/gui_lhermi/"
,"https://www.instagram.com/thaicy14/"
,"https://www.instagram.com/rmeera274201/"
,"https://www.instagram.com/yunri._.46/"
,"https://www.instagram.com/royaali20248344/"
,"https://www.instagram.com/sara_1_sara_11/"
,"https://www.instagram.com/nirmla31752/"
,"https://www.instagram.com/kainatmatoo/"
,"https://www.instagram.com/moonie_queen_021/"
,"https://www.instagram.com/matcrixx/"
,"https://www.instagram.com/prnssrwy60/"
,"https://www.instagram.com/batoglydel/"
,"https://www.instagram.com/roudaina37390/"
,"https://www.instagram.com/_nanx002/"
,"https://www.instagram.com/xdlelaaaa/"
,"https://www.instagram.com/namanya_sahrul/"
,"https://www.instagram.com/hiuton.puna0.07/"
,"https://www.instagram.com/iamgauravpandat/"
,"https://www.instagram.com/pari7271713/"
,"https://www.instagram.com/tongogara.t/"
,"https://www.instagram.com/ribeiroaltemarbotelho/"
,"https://www.instagram.com/yytta_3123/"
,"https://www.instagram.com/aselkislar/"
,"https://www.instagram.com/sud.ha8225/"
,"https://www.instagram.com/revii_yansyah/"
,"https://www.instagram.com/manda_jaaaaaa/"
,"https://www.instagram.com/__jayvynnn/"
,"https://www.instagram.com/sanjona.khan/"
,"https://www.instagram.com/teto__3tman11/"
,"https://www.instagram.com/presteselmiza/"
,"https://www.instagram.com/teume.e2507/"
,"https://www.instagram.com/saeed_zaxoy_99/"
,"https://www.instagram.com/phuocthanh3/"
,"https://www.instagram.com/ndre7_810/"
,"https://www.instagram.com/terserahkitakw_/"
,"https://www.instagram.com/bwzh__/"
,"https://www.instagram.com/thaisnbmiranda/"
,"https://www.instagram.com/_iarleylopes/"
,"https://www.instagram.com/hosana83254/"
,"https://www.instagram.com/bia.queirozx_/"
,"https://www.instagram.com/cassistico/"
,"https://www.instagram.com/isael.yalla/"
,"https://www.instagram.com/barbara_copetti/"
,"https://www.instagram.com/pamwstar/"
,"https://www.instagram.com/kaikybraga18/"
,"https://www.instagram.com/aliciacarvalho/"
,"https://www.instagram.com/railzaazevedo1/"
,"https://www.instagram.com/lima.veronicadossantos/"
,"https://www.instagram.com/wrmabels/"
,"https://www.instagram.com/amora_lindinha/"
,"https://www.instagram.com/limaalicia_xxz/"
,"https://www.instagram.com/a_sil_via5622/"
,"https://www.instagram.com/rbeca.cz/"
,"https://www.instagram.com/_jcaiio/"
,"https://www.instagram.com/cecilia_clivia/"
,"https://www.instagram.com/eudson390/"
,"https://www.instagram.com/lucass_pp16/"
,"https://www.instagram.com/beatriiz.araujjom/"
,"https://www.instagram.com/carolineleticia625/"
,"https://www.instagram.com/barcelos_sx1/"
,"https://www.instagram.com/hugodaniel_hd/"
,"https://www.instagram.com/robert._05_/"
,"https://www.instagram.com/dbeso__/"
,"https://www.instagram.com/dre_version/"
,"https://www.instagram.com/gabriel_silvax457/"
,"https://www.instagram.com/emillyaws/"
,"https://www.instagram.com/daniellec.ribeiro/"
,"https://www.instagram.com/bonjuorcla/"
,"https://www.instagram.com/eeduarda.melo_/"
,"https://www.instagram.com/festival_minecraft/"
,"https://www.instagram.com/novo_usp/"
,"https://www.instagram.com/jm__santtos12/"
,"https://www.instagram.com/kalilnascimentoo/"
,"https://www.instagram.com/sunxne_/"
,"https://www.instagram.com/giovs_453/"
,"https://www.instagram.com/edsonmarinholealdesa/"
,"https://www.instagram.com/danysatierf/"
,"https://www.instagram.com/xandaoantonio/"
,"https://www.instagram.com/skrriii_/"
,"https://www.instagram.com/festival_minecraft/"
,"https://www.instagram.com/paulo_george__/"
,"https://www.instagram.com/matus.kkj/"
,"https://www.instagram.com/pqpmjr/"
,"https://www.instagram.com/matheusgomesdotcom/"
,"https://www.instagram.com/cstr_duda/"
,"https://www.instagram.com/byaorl_/"
,"https://www.instagram.com/julisntss/"
,"https://www.instagram.com/limaalicia_xxz/"
,"https://www.instagram.com/festival_minecraft/"
,"https://www.instagram.com/lohramlamazon/"
,"https://www.instagram.com/__emanuelly.s1/"
,"https://www.instagram.com/elle.ssecrets/"
,"https://www.instagram.com/semcellvr/"
,"https://www.instagram.com/linckonemanoell/"
,"https://www.instagram.com/carlinh092/"
,"https://www.instagram.com/eliasthrv96_ofc/"
,"https://www.instagram.com/xwgabyy_/"
,"https://www.instagram.com/dailystefanne/"
]
'''


# Configuração usada quando o script roda sem a interface
CONFIG_PADRAO = {
    "usuario": os.environ.get("IG_USUARIO", ""),
    "senha": os.environ.get("IG_SENHA", ""),
    "urls": url,
    "limite": 15,          # seguidas por ciclo
    "pausaMinutos": 60,    # pausa depois de atingir o limite
    "esperaMin": 4,        # espera aleatória entre ações (segundos)
    "esperaMax": 15,
    "headless": False,
}


def rolarNoMeio(page, distancias):
    # Pega o tamanho da viewport (janela visível)
    viewport = page.viewport_size
    center_x = viewport["width"] / 2
    center_y = viewport["height"] / 2
    # Move o mouse para o centro da tela
    page.mouse.move(center_x, center_y)
    page.wait_for_timeout(1000)
    for d in distancias:
        page.mouse.wheel(0, d)
        page.wait_for_timeout(1000)
    log("✅ Scroll realizado com o mouse no meio da tela.")


def abrirSeguidores(page):
    """Clica no contador "X seguidores" do perfil e retorna a caixa que abre"""
    # O contador é um link com href="#"; o link "Seguido(a) por..." (mutualOnly) é outra lista
    contador = page.locator("a:has-text('seguidores'):not([href*='mutualOnly'])").first
    contador.wait_for(timeout=15000)
    contador.scroll_into_view_if_needed()
    clicar_com_mouse(page, contador)

    dialogo = page.locator("div[role='dialog']").last
    dialogo.wait_for(timeout=15000)
    log("✅ Caixa de seguidores aberta.")
    return dialogo


def executar(config, parar=None, aoPausar=None, aoRetomar=None, aoSeguir=None):
    """Roda o bot até o usuário apertar "Parar" (parar.set())

    aoPausar(minutos), aoRetomar() e aoSeguir(total) avisam a interface
    """
    parar = parar or threading.Event()
    urls = [u.strip().rstrip("/") + "/" for u in config["urls"] if u.strip()]
    if not urls:
        log("⚠️ Nenhuma URL configurada.")
        return
    limite = config["limite"]

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir="userdata",
            headless=config["headless"],
            # O bot procura os textos em português ("Seguir")
            locale="pt-BR"
        )
        page = browser.new_page()
        log("\n\n***INÍCIO DO PROGRAMA\n\n***")
        cliques = 0
        totalCliques = 0   # soma de todos os ciclos desta execução
        urlAtual = ""

        try:
            if not estaLogado(page):
                log("Sessão não encontrada, fazendo login...")
                senhaUsuario(page, config["usuario"], config["senha"], parar)

            while not parar.is_set():

                # Se atingiu o limite, faz a pausa
                if cliques >= limite:
                    log(f"⚠️ Limite atingido. Esperando {config['pausaMinutos']} minutos...")
                    if aoPausar:
                        aoPausar(config["pausaMinutos"])
                    esperar(page, config["pausaMinutos"] * 60, parar)
                    if aoRetomar:
                        aoRetomar()
                    log("Pausa terminada, começando outro ciclo.")
                    cliques = 0
                    continue

                log("while True:")
                try:
                    page.goto("https://www.instagram.com")
                    esperarTempo(page, config, parar)

                    urlAtual = random.choice(urls)
                    page.goto(urlAtual)
                    log(f"o perfil visitado: {urlAtual}")
                    esperarTempo(page, config, parar)

                    dialogo = abrirSeguidores(page)
                    esperarTempo(page, config, parar)
                except Parado:
                    raise
                except Exception as e:
                    log(f"⚠️ Erro ao abrir os seguidores de {urlAtual}: {e}")
                    if not estaLogado(page):
                        senhaUsuario(page, config["usuario"], config["senha"], parar)
                    continue

                log(f"cliques < limite:{cliques}<{limite}")
                rolarNoMeio(page, [500, 1000, 1000])

                # Só os botões dentro da caixa de seguidores (não o "Seguir" do próprio perfil)
                botoes = dialogo.locator("button:has-text('Seguir')")
                total = botoes.count()
                log(f"total: {total}")

                if total == 0:
                    # O Instagram às vezes limita a lista ("Nenhum resultado")
                    log(f"⚠️ Nenhum botão 'Seguir' nos seguidores de {urlAtual}, indo para outro perfil.")
                    continue

                contErro = 0
                for i in range(total):
                    try:
                        log("for...try:")
                        # Depois do clique o botão vira "Seguindo" e sai da lista,
                        # então o próximo botão "Seguir" é sempre o primeiro (nth(i) pulava botões)
                        botao = botoes.first
                        botao.scroll_into_view_if_needed(timeout=5000)
                       # clicou = clicar_com_mouse(page, botao)
                        botao.click(timeout=5000)

                        cliques += 1
                        log(f"botao/total[{i+1}/{total}]")
                        # pausa para parecer humano
                        esperarTempo(page, config, parar)

                        totalCliques += 1
                        if aoSeguir:
                            aoSeguir(totalCliques)
                        log(f"quantidade de cliques/limite :{cliques}/{limite} (total: {totalCliques})")

                        if cliques >= limite:
                            break

                    except Parado:
                        raise
                    except Exception as e:
                        log(f"⚠️ Erro ao clicar no botão {i+1}: {e}")
                        contErro+=1
                        if contErro>3:
                            break
                        continue
        except Parado:
            pass
        finally:
            log(f"Total de perfis seguidos nesta execução: {totalCliques}")
            log("\n\n***FIM DO PROGRAMA***\n\n")
            browser.close()


if __name__ == "__main__":
    try:
        executar(CONFIG_PADRAO)
    except KeyboardInterrupt:
        pass

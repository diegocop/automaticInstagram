import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright

#playwright codegen https://www.instagram.com/diegocop/
def senhaUsuario():

    usuario = "diegoinfocop"
    senha = "Ihateyou5338@"

    # Abre a página de login do Instagram
    page.goto("https://www.instagram.com/accounts/login/")

    # Espera os campos aparecerem
    page.wait_for_selector("input[name='username']")
    page.wait_for_selector("input[name='password']")

    # Preenche usuário e senha
    page.fill("input[name='username']", usuario)

    time.sleep(1000)
    page.fill("input[name='password']", senha)

    time.sleep(1000)

    # Clica no botão de login
    page.click("button[type='submit']")

    # Espera alguns segundos para carregar a página
    time.sleep(1000)


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
def esperarTempo():
     # tempo aleatório entre 2s e 7s (2000ms a 7000ms)
        espera = random.randint(4000, 7000)
        print(f"Esperando {espera/1000:.2f} segundos...")
        page.wait_for_timeout(espera)

def log(mensagem, arquivoLog="log.txt"):
  # Pega a hora atual no formato: 2025-09-10 14:30:15
  agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Cria a linha de log
  linha = f"[{agora}] {mensagem}\n"
    # Abre o arquivo em modo append e adiciona a linha
  with open(arquivoLog, "a", encoding="utf-8") as f:
    f.write(linha)
  print(f"[{agora}] {mensagem}\n")

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

urlAtual =""
with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="userdata",
        headless=False

   
    )
    page = browser.new_page()
    log("\n\n***INÍCIO DO PROGRAMA\n\n***")
    # Limite de 24 por hora
    limite = 25
    cliques = 0

    #senhaUsuario()  
    
    

    while True:
        
        log("while True:")
        page.goto("https://www.instagram.com")
    
        esperarTempo()

        urlAtual = random.choice(url)
        page.goto(urlAtual)

        log(f"o perfil visitado: {urlAtual}")

        esperarTempo()

        page.goto(urlAtual+"followers/")

        page.wait_for_selector("span:has-text('seguidores')")

        # pega a posição do botão
        botao = page.locator("span:has-text('seguidores')")

        clicar_com_mouse(page, botao)
        
        esperarTempo()
        # Se ainda não atingiu o limite, executa
        if cliques < limite:
            log(f"cliques < limite:{cliques}<{limite}")    
            

            # Pega o tamanho da viewport (janela visível)
            viewport = page.viewport_size
            center_x = viewport["width"] / 2
            center_y = viewport["height"] / 2        
            # Move o mouse para o centro da tela
            page.mouse.move(center_x, center_y)
            page.wait_for_timeout(1000)  # espera 0.5s para o movimento ser visível
        
            page.mouse.wheel(0, 500)     # rola 500px
            page.wait_for_timeout(1000)
            page.mouse.wheel(0, 1000)     # rola 500px
            page.wait_for_timeout(1000)
            page.mouse.wheel(0, 1000)     # rola 500px
            page.wait_for_timeout(1000)
            log("✅ Scroll realizado com o mouse no meio da tela.")

            # Recalcula os botões a cada loop
            botoes = page.locator("button:has-text('Seguir')")
            total = botoes.count()

            log(botoes)
            log(f"first botao: {botoes.first}")
            log(f"total: {total}")
            
            if total == 0:
                log("if total == 0:")
                #Pega o tamanho da viewport (janela visível)
                viewport = page.viewport_size
                center_x = viewport["width"] / 2
                center_y = viewport["height"] / 2        
                 # Move o mouse para o centro da tela  
                page.mouse.move(center_x, center_y)
                page.wait_for_timeout(1000)  #   
                page.mouse.wheel(0, 1000)     # rola 500px
                page.wait_for_timeout(1000)
                page.mouse.wheel(0,1000)
                log("✅ Scroll realizado com o mouse no meio da tela.")
            
                botoes = page.locator("button:has-text('Seguir')")
                total = botoes.count()
                
                continue
            
          
            if total > 0 and cliques < limite:
                contErro =0
                for i in range(total):
                    try:
                        log("for...try:")  
                        botao = botoes.nth(i)
                        botao.scroll_into_view_if_needed()
                       # clicou = clicar_com_mouse(page, botao)
                        botao.click()

                        cliques += 1
                        log(f"botao/total[{i+1}/{total}]")
                        # pausa para parecer humano (ex.: 5 a 15 segundos)
                       
                                                                      
                        esperarTempo()
                        
                        log(f"quantidade de cliques/limite :{cliques}/{limite}")
                        
                         # Pega o tamanho da viewport (janela visível)
                        #viewport = page.viewport_size
                        #center_x = viewport["width"] / 2
                        #center_y = viewport["height"] / 2        
          #  ove o mouse para o centro da tela  
                        #page.mouse.move(center_x, center_y)
                        #page.mouse.wheel(0, 100)     # rola 500px
                        #page.wait_for_timeout(1000)
                        #print("✅ 001 Scroll realizado com o mouse no meio da tela.")

                       

                        if cliques > limite:
                            break

                    except Exception as e:
                        log(f"⚠️ Erro ao clicar no botão {i+1}: {e}")  
                        contErro+=1
                        if contErro>3:
                            break                     
                        continue        
           
        else:
            log("⚠️ Limite por hora atingido. Esperando passar 1 hora...") 
            

            # Espera 1 hora para a próxima execução
            log("esperando 3600 s") 
            log("\n\n***FIM DO PROGRAMA***\n\n")
            time.sleep(3600)            
            cliques =0
                
    # Aqui o navegador vai continuar aberto
    input("Pressione ENTER para fechar...")
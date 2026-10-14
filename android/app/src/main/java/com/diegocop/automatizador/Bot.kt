package com.diegocop.automatizador

import android.os.Handler
import android.os.Looper
import android.webkit.CookieManager
import android.webkit.WebView
import org.json.JSONObject
import org.json.JSONTokener
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import kotlin.random.Random

/** Lançada quando o usuário aperta "Parar" */
class Parado : Exception()

// Funções injetadas na página antes de cada comando (somem quando a página recarrega).
// Os textos ficam em português e inglês porque o idioma depende do celular.
private const val AJUDANTES = """
window.__bot = window.__bot || {
  textosSeguir: ['seguir', 'seguir de volta', 'follow', 'follow back'],
  texto: (e) => (e.innerText || '').trim().toLowerCase(),
  // A caixa de seguidores (computador) ou a página /followers/ (layout de celular)
  lista: () => {
    const d = document.querySelectorAll("div[role='dialog']");
    return d.length ? d[d.length - 1] : document;
  },
  listaAberta: () => document.querySelectorAll("div[role='dialog']").length > 0
                     || location.pathname.includes('/followers'),
  // O link "Seguido(a) por..." (mutualOnly) é outra lista
  clicarContador: () => {
    const a = [...document.querySelectorAll('a')].find(a => {
      const t = __bot.texto(a);
      return (t.includes('seguidores') || t.includes('followers')) && !(a.href || '').includes('mutualOnly');
    });
    if (!a) return false;
    a.scrollIntoView({block: 'center'});
    a.click();
    return true;
  },
  // Só os botões dentro da lista de seguidores (não o "Seguir" do próprio perfil)
  botoes: () => [...__bot.lista().querySelectorAll('button')]
    .filter(b => __bot.textosSeguir.includes(__bot.texto(b)) && b.dataset.bot !== 'falhou'),
  contar: () => __bot.botoes().length,
  // Depois do clique o botão vira "Seguindo" e sai da lista, então o próximo é sempre o primeiro
  clicarPrimeiro: () => {
    const b = __bot.botoes()[0];
    if (!b) return false;
    document.querySelectorAll("[data-bot='clicado']").forEach(e => delete e.dataset.bot);
    b.dataset.bot = 'clicado';
    b.scrollIntoView({block: 'center'});
    b.click();
    return true;
  },
  // Se o botão continua "Seguir", o clique não pegou: marca para não clicar de novo
  confirmar: () => {
    const b = document.querySelector("[data-bot='clicado']");
    if (!b || !b.isConnected || !__bot.textosSeguir.includes(__bot.texto(b))) return true;
    b.dataset.bot = 'falhou';
    return false;
  },
  // Rola a parte da lista que tem barra de rolagem (carrega mais seguidores)
  rolar: (d) => {
    const l = __bot.lista();
    const el = [...l.querySelectorAll('div')].find(e =>
      e.scrollHeight > e.clientHeight + 10 && /(auto|scroll)/.test(getComputedStyle(e).overflowY));
    (el || document.scrollingElement).scrollBy(0, d);
  },
  preencher: (seletor, valor) => {
    const el = document.querySelector(seletor);
    if (!el) return false;
    // O Instagram usa React: precisa do setter nativo + evento "input"
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    el.focus();
    setter.call(el, valor);
    el.dispatchEvent(new Event('input', {bubbles: true}));
    return true;
  },
  entrar: () => {
    const b = document.querySelector("button[type='submit']");
    if (b) { b.click(); return true; }
    const f = document.querySelector('form');
    if (f) { f.requestSubmit(); return true; }
    return false;
  },
};
"""

// O Instagram já usou name='username'/'password' e hoje usa 'email'/'pass'
private const val CAMPO_USUARIO = "input[name='email'], input[name='username']"
private const val CAMPO_SENHA = "input[name='pass'], input[name='password']"

/**
 * Mesma lógica do automatizador.py, mas controlando o WebView do app.
 * Roda numa thread própria; os comandos para a página vão para a thread da tela e esperam a resposta.
 */
class Bot(
    private val webView: WebView,
    private val config: Config,
    private val log: (String) -> Unit,
    private val mostrarNavegador: () -> Unit,
    private val aoPausar: () -> Unit = {},
    private val aoRetomar: () -> Unit = {},
    private val aoSeguir: (total: Int) -> Unit = {},
) {
    @Volatile
    var parar = false

    private val ui = Handler(Looper.getMainLooper())

    fun executar() {
        val urls = config.urls
        if (urls.isEmpty()) {
            log("⚠️ Nenhuma URL configurada.")
            return
        }
        val limite = config.limite
        log("\n\n***INÍCIO DO PROGRAMA\n\n***")
        var cliques = 0
        var totalCliques = 0   // soma de todos os ciclos desta execução
        var urlAtual = ""

        try {
            if (!estaLogado()) {
                log("Sessão não encontrada, fazendo login...")
                login()
            }

            while (!parar) {
                // Se atingiu o limite, faz a pausa
                if (cliques >= limite) {
                    log("⚠️ Limite atingido. Esperando ${config.pausaMinutos} minutos...")
                    aoPausar()
                    esperar(config.pausaMinutos * 60.0)
                    aoRetomar()
                    log("Pausa terminada, começando outro ciclo.")
                    cliques = 0
                    continue
                }

                try {
                    ir("https://www.instagram.com/")
                    esperarTempo()

                    urlAtual = urls.random()
                    ir(urlAtual)
                    log("o perfil visitado: $urlAtual")
                    esperarTempo()

                    abrirSeguidores()
                    esperarTempo()
                } catch (e: Parado) {
                    throw e
                } catch (e: Exception) {
                    log("⚠️ Erro ao abrir os seguidores de $urlAtual: ${e.message}")
                    if (!estaLogado()) login()
                    continue
                }

                log("cliques < limite: $cliques<$limite")
                rolar(listOf(500, 1000, 1000))

                val total = js("__bot.contar()")?.toIntOrNull() ?: 0
                log("total: $total")
                if (total == 0) {
                    // O Instagram às vezes limita a lista ("Nenhum resultado")
                    log("⚠️ Nenhum botão 'Seguir' nos seguidores de $urlAtual, indo para outro perfil.")
                    continue
                }

                var contErro = 0
                for (i in 0 until total) {
                    try {
                        if (js("__bot.clicarPrimeiro()") != "true") throw RuntimeException("botão 'Seguir' não encontrado")
                        cliques++
                        log("botao/total[${i + 1}/$total]")
                        // pausa para parecer humano
                        esperarTempo()

                        if (js("__bot.confirmar()") != "true") {
                            cliques--
                            throw RuntimeException("o clique não teve efeito (o Instagram pode estar limitando a conta)")
                        }
                        totalCliques++
                        aoSeguir(totalCliques)
                        log("quantidade de cliques/limite: $cliques/$limite (total: $totalCliques)")
                        if (cliques >= limite) break
                    } catch (e: Parado) {
                        throw e
                    } catch (e: Exception) {
                        log("⚠️ Erro ao clicar no botão ${i + 1}: ${e.message}")
                        contErro++
                        if (contErro > 3) break
                    }
                }
            }
        } catch (_: Parado) {
        } finally {
            log("Total de perfis seguidos nesta execução: $totalCliques")
            log("\n\n***FIM DO PROGRAMA***\n\n")
        }
    }

    private fun login() {
        ir("https://www.instagram.com/accounts/login/")

        if (config.usuario.isNotEmpty() && config.senha.isNotEmpty()) {
            // Espera os campos aparecerem
            if (!esperarAte(30.0) { js("!!document.querySelector(${texto(CAMPO_SENHA)})") == "true" }) {
                throw RuntimeException("campos de login não apareceram")
            }
            js("__bot.preencher(${texto(CAMPO_USUARIO)}, ${texto(config.usuario)})")
            esperar(1.0)
            js("__bot.preencher(${texto(CAMPO_SENHA)}, ${texto(config.senha)})")
            esperar(1.0)
            js("__bot.entrar()")
            log("Se o Instagram pedir código ou confirmação, responda na aba Navegador.")
        } else {
            // Sem credenciais: espera o login manual no navegador do app
            log("Faça o login manualmente na aba Navegador...")
            ui.post(mostrarNavegador)
        }

        // Espera o login terminar (pode pedir código 2FA, sem limite de tempo)
        while (!estaLogado()) esperar(3.0)
        naUi { CookieManager.getInstance().flush() }
        log("✅ Login feito.")
        esperar(5.0)
    }

    /** O cookie 'sessionid' só existe quando a conta está logada */
    private fun estaLogado(): Boolean = naUi {
        CookieManager.getInstance().getCookie("https://www.instagram.com")?.contains("sessionid=") == true
    }

    /** Clica no contador "X seguidores" do perfil e espera a lista abrir */
    private fun abrirSeguidores() {
        if (!esperarAte(15.0) { js("__bot.clicarContador()") == "true" }) {
            throw RuntimeException("contador de seguidores não encontrado")
        }
        if (!esperarAte(15.0) { js("__bot.listaAberta()") == "true" }) {
            throw RuntimeException("a lista de seguidores não abriu")
        }
        log("✅ Caixa de seguidores aberta.")
    }

    private fun rolar(distancias: List<Int>) {
        esperar(1.0)
        for (d in distancias) {
            js("__bot.rolar($d)")
            esperar(1.0)
        }
        log("✅ Scroll realizado.")
    }

    private fun ir(url: String) {
        naUi { webView.loadUrl(url) }
        esperar(1.0)
        esperarAte(30.0) { js("document.readyState") == "complete" }
        esperar(2.0)
    }

    /** Espera em pedaços de 1s para o botão "Parar" responder rápido */
    private fun esperar(segundos: Double) {
        val fim = System.currentTimeMillis() + (segundos * 1000).toLong()
        while (true) {
            if (parar) throw Parado()
            val falta = fim - System.currentTimeMillis()
            if (falta <= 0) return
            Thread.sleep(minOf(1000L, falta))
        }
    }

    // tempo aleatório entre esperaMin e esperaMax segundos
    private fun esperarTempo() {
        val min = config.esperaMin.toDouble()
        val max = config.esperaMax.toDouble()
        esperar(if (max > min) Random.nextDouble(min, max) else min)
    }

    /** Repete a condição a cada meio segundo até ela dar certo ou acabar o tempo */
    private fun esperarAte(segundos: Double, condicao: () -> Boolean): Boolean {
        val fim = System.currentTimeMillis() + (segundos * 1000).toLong()
        while (System.currentTimeMillis() < fim) {
            if (condicao()) return true
            esperar(0.5)
        }
        return false
    }

    /** Roda um código JavaScript na página e devolve o resultado como texto (null se não houver) */
    private fun js(codigo: String): String? {
        if (parar) throw Parado()
        val pronto = CountDownLatch(1)
        var resultado: String? = null
        ui.post {
            webView.evaluateJavascript("$AJUDANTES\n$codigo") {
                resultado = it
                pronto.countDown()
            }
        }
        if (!pronto.await(30, TimeUnit.SECONDS)) throw RuntimeException("a página não respondeu")
        val bruto = resultado
        if (bruto == null || bruto == "null") return null
        // O WebView devolve o resultado em JSON ("\"texto\"", true, 3...)
        return JSONTokener(bruto).nextValue().toString()
    }

    /** Executa na thread da tela e espera o resultado */
    private fun <T> naUi(bloco: () -> T): T {
        val pronto = CountDownLatch(1)
        var resultado: Result<T>? = null
        ui.post {
            resultado = runCatching(bloco)
            pronto.countDown()
        }
        if (!pronto.await(30, TimeUnit.SECONDS)) throw RuntimeException("a tela não respondeu")
        return resultado!!.getOrThrow()
    }

    /** Texto como literal JavaScript, com as aspas escapadas */
    private fun texto(valor: String): String = JSONObject.quote(valor)
}

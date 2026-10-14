package com.diegocop.automatizador

import android.annotation.SuppressLint
import android.content.Context
import android.content.MutableContextWrapper
import android.os.Handler
import android.os.Looper
import android.view.ViewGroup
import android.webkit.CookieManager
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * O que precisa sobreviver quando a tela do app fecha: o navegador, o bot e o log.
 * A tela (MainActivity) e o serviço (BotService) só se conectam aqui.
 */
object Automacao {
    private val ui = Handler(Looper.getMainLooper())
    private var navegador: WebView? = null

    // O navegador troca de "dono" (tela do app ou janela flutuante) sem recarregar a página
    private var contexto: MutableContextWrapper? = null

    @Volatile
    var bot: Bot? = null
    val rodando: Boolean get() = bot != null

    var servico: BotService? = null

    // Perfis seguidos somando todos os ciclos da execução atual (ou da última)
    @Volatile
    var totalCliques = 0

    /** Perfis seguidos somando todas as execuções (fica salvo até apertar "Zerar") */
    fun totalGeral(context: Context): Int =
        context.getSharedPreferences("config", Context.MODE_PRIVATE).getInt("totalGeral", 0)

    fun somarTotalGeral(context: Context) {
        val prefs = context.getSharedPreferences("config", Context.MODE_PRIVATE)
        synchronized(this) { prefs.edit().putInt("totalGeral", prefs.getInt("totalGeral", 0) + 1).apply() }
    }

    fun zerarTotalGeral(context: Context) {
        context.getSharedPreferences("config", Context.MODE_PRIVATE).edit().putInt("totalGeral", 0).apply()
    }

    // Na pausa entre ciclos a janela flutuante fica fechada
    @Volatile
    var pausado = false

    // A tela do app está aparecendo (aí o navegador fica nela, não na janela flutuante)
    var telaVisivel = false

    /** Config que a tela passa para o serviço (inclui a senha mesmo quando ela não é salva) */
    var configPendente: Config? = null

    // Avisos para a tela, quando ela está aberta
    var aoLogar: ((linha: String, mensagem: String) -> Unit)? = null
    var aoTerminar: (() -> Unit)? = null
    var aoPedirNavegador: (() -> Unit)? = null

    @SuppressLint("SetJavaScriptEnabled")
    fun navegador(dono: Context): WebView {
        navegador?.let {
            contexto?.baseContext = dono
            return it
        }
        val novoContexto = MutableContextWrapper(dono)
        val novo = WebView(novoContexto)
        novo.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            // Sem o "; wv" o Instagram trata como o Chrome normal do celular
            userAgentString = userAgentString.replace("; wv", "").replace(Regex("Version/[\\d.]+ "), "")
        }
        CookieManager.getInstance().setAcceptCookie(true)
        CookieManager.getInstance().setAcceptThirdPartyCookies(novo, true)
        novo.webViewClient = object : WebViewClient() {
            // Links para abrir o app do Instagram (intent://, instagram://) ficam bloqueados
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean =
                request.url.scheme !in listOf("http", "https")
        }
        novo.loadUrl("https://www.instagram.com/")
        navegador = novo
        contexto = novoContexto
        return novo
    }

    /** Coloca o navegador dentro de outro container (tela do app ou janela flutuante) */
    fun mover(dono: Context, destino: ViewGroup, params: ViewGroup.LayoutParams) {
        val webView = navegador(dono)
        if (webView.parent === destino) return
        (webView.parent as? ViewGroup)?.removeView(webView)
        // Desfaz a miniatura da janela flutuante
        webView.scaleX = 1f
        webView.scaleY = 1f
        destino.addView(webView, 0, params)
    }

    /** A tela do app vai ser destruída: solta o navegador se ele estiver nela */
    fun liberar(app: Context, tela: ViewGroup) {
        contexto?.baseContext = app
        navegador?.let { if (it.parent === tela) tela.removeView(it) }
    }

    /** Grava no log.txt do app, mostra na tela e na notificação (pode ser chamado de qualquer thread) */
    fun log(context: Context, mensagem: String) {
        // Pega a hora atual no formato: 2025-09-10 14:30:15
        val agora = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US).format(Date())
        val linha = "[$agora] $mensagem\n"
        val arquivo = arquivoLog(context)
        synchronized(this) { arquivo.appendText(linha) }
        ui.post {
            aoLogar?.invoke(linha, mensagem)
            servico?.atualizarNotificacao(mensagem.trim())
        }
    }

    fun limparLog(context: Context) {
        synchronized(this) { arquivoLog(context).writeText("") }
    }

    fun arquivoLog(context: Context) = File(context.filesDir, "log.txt")
}

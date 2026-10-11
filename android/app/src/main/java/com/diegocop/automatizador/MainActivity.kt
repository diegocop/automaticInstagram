package com.diegocop.automatizador

import android.annotation.SuppressLint
import android.app.Activity
import android.app.AlertDialog
import android.os.Bundle
import android.text.InputType
import android.view.View
import android.view.WindowManager
import android.webkit.CookieManager
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.CheckBox
import android.widget.EditText
import android.widget.ScrollView
import android.widget.Spinner
import android.widget.TextView
import org.json.JSONObject
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class MainActivity : Activity() {
    private lateinit var navegador: WebView
    private lateinit var painelConfig: ScrollView
    private lateinit var status: TextView
    private lateinit var ultimaLinha: TextView
    private lateinit var usuario: EditText
    private lateinit var senha: EditText
    private lateinit var lembrarSenha: CheckBox
    private lateinit var spinnerListas: Spinner
    private lateinit var textoUrls: EditText
    private lateinit var limite: EditText
    private lateinit var pausa: EditText
    private lateinit var esperaMin: EditText
    private lateinit var esperaMax: EditText
    private lateinit var botaoIniciar: Button
    private lateinit var botaoParar: Button
    private lateinit var textoLog: TextView

    private lateinit var config: Config
    private var bot: Bot? = null
    private val linhasLog = ArrayDeque<String>()
    private val arquivoLog by lazy { File(filesDir, "log.txt") }

    // Evita que o Spinner dispare "trocarLista" enquanto o próprio código mexe nele
    private var atualizandoListas = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        navegador = findViewById(R.id.navegador)
        painelConfig = findViewById(R.id.painelConfig)
        status = findViewById(R.id.status)
        ultimaLinha = findViewById(R.id.ultimaLinha)
        usuario = findViewById(R.id.usuario)
        senha = findViewById(R.id.senha)
        lembrarSenha = findViewById(R.id.lembrarSenha)
        spinnerListas = findViewById(R.id.listas)
        textoUrls = findViewById(R.id.urls)
        limite = findViewById(R.id.limite)
        pausa = findViewById(R.id.pausa)
        esperaMin = findViewById(R.id.esperaMin)
        esperaMax = findViewById(R.id.esperaMax)
        botaoIniciar = findViewById(R.id.iniciar)
        botaoParar = findViewById(R.id.parar)
        textoLog = findViewById(R.id.log)

        configurarNavegador()

        config = Config.carregar(this)
        mostrarConfig()

        findViewById<Button>(R.id.abaConfig).setOnClickListener { painelConfig.visibility = View.VISIBLE }
        findViewById<Button>(R.id.abaNavegador).setOnClickListener { mostrarNavegador() }
        findViewById<CheckBox>(R.id.mostrarSenha).setOnCheckedChangeListener { _, mostrar ->
            senha.inputType = InputType.TYPE_CLASS_TEXT or
                if (mostrar) InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD else InputType.TYPE_TEXT_VARIATION_PASSWORD
            senha.setSelection(senha.text.length)
        }
        findViewById<Button>(R.id.novaLista).setOnClickListener { novaLista() }
        findViewById<Button>(R.id.renomearLista).setOnClickListener { renomearLista() }
        findViewById<Button>(R.id.excluirLista).setOnClickListener { excluirLista() }
        findViewById<Button>(R.id.importar).setOnClickListener { importar() }
        findViewById<Button>(R.id.salvar).setOnClickListener { salvar(avisar = true) }
        botaoIniciar.setOnClickListener { iniciar() }
        botaoParar.setOnClickListener { pararBot() }
        spinnerListas.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(pai: AdapterView<*>?, view: View?, posicao: Int, id: Long) {
                if (!atualizandoListas) trocarLista(config.listas.keys.elementAt(posicao))
            }

            override fun onNothingSelected(pai: AdapterView<*>?) {}
        }

        carregarLog()
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun configurarNavegador() {
        navegador.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            // Sem o "; wv" o Instagram trata como o Chrome normal do celular
            userAgentString = userAgentString.replace("; wv", "").replace(Regex("Version/[\\d.]+ "), "")
        }
        CookieManager.getInstance().setAcceptCookie(true)
        CookieManager.getInstance().setAcceptThirdPartyCookies(navegador, true)
        navegador.webViewClient = object : WebViewClient() {
            // Links para abrir o app do Instagram (intent://, instagram://) ficam bloqueados
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean =
                request.url.scheme !in listOf("http", "https")
        }
        navegador.loadUrl("https://www.instagram.com/")
    }

    private fun mostrarNavegador() {
        painelConfig.visibility = View.GONE
    }

    // ---- Configurações na tela ----
    private fun mostrarConfig() {
        usuario.setText(config.usuario)
        senha.setText(config.senha)
        lembrarSenha.isChecked = config.lembrar
        limite.setText(config.limite.toString())
        pausa.setText(config.pausaMinutos.toString())
        esperaMin.setText(config.esperaMin.toString())
        esperaMax.setText(config.esperaMax.toString())
        atualizarListas()
    }

    // ---- Listas de perfis ----
    private fun guardarListaAtual() {
        config.listas[config.listaAtual] = lerUrls(textoUrls.text.toString())
    }

    /** Atualiza o Spinner e mostra os perfis da lista selecionada */
    private fun atualizarListas() {
        atualizandoListas = true
        val nomes = config.listas.keys.toList()
        spinnerListas.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, nomes)
        spinnerListas.setSelection(nomes.indexOf(config.listaAtual), false)
        textoUrls.setText(config.urls.joinToString("\n"))
        // O Spinner avisa a seleção depois do layout, então libera só no próximo ciclo da tela
        spinnerListas.post { atualizandoListas = false }
    }

    private fun trocarLista(nome: String) {
        if (nome == config.listaAtual) return
        guardarListaAtual()
        config.listaAtual = nome
        atualizarListas()
    }

    private fun pedirNome(titulo: String, inicial: String = "", aoConfirmar: (String) -> Unit) {
        val campo = EditText(this).apply { setText(inicial); setSingleLine() }
        AlertDialog.Builder(this)
            .setTitle(titulo)
            .setMessage("Nome da lista:")
            .setView(campo)
            .setPositiveButton("OK") { _, _ ->
                val nome = campo.text.toString().trim()
                when {
                    nome.isEmpty() || nome == inicial -> {}
                    nome in config.listas -> erro("Já existe uma lista chamada \"$nome\".")
                    else -> aoConfirmar(nome)
                }
            }
            .setNegativeButton("Cancelar", null)
            .show()
    }

    private fun novaLista() = pedirNome("Nova lista") { nome ->
        guardarListaAtual()
        config.listas[nome] = emptyList()
        config.listaAtual = nome
        atualizarListas()
        textoUrls.requestFocus()
    }

    private fun renomearLista() = pedirNome("Renomear lista", config.listaAtual) { nome ->
        guardarListaAtual()
        // Recria o mapa para manter a ordem das listas
        config.listas = LinkedHashMap(config.listas.mapKeys { (n, _) -> if (n == config.listaAtual) nome else n })
        config.listaAtual = nome
        atualizarListas()
    }

    private fun excluirLista() {
        if (config.listas.size == 1) {
            erro("Precisa existir pelo menos uma lista.")
            return
        }
        AlertDialog.Builder(this)
            .setTitle("Excluir lista")
            .setMessage("Excluir a lista \"${config.listaAtual}\"?")
            .setPositiveButton("Excluir") { _, _ ->
                config.listas.remove(config.listaAtual)
                config.listaAtual = config.listas.keys.first()
                atualizarListas()
            }
            .setNegativeButton("Cancelar", null)
            .show()
    }

    /** Cola o config.json da versão de PC para trazer as listas e configurações */
    private fun importar() {
        val campo = EditText(this).apply {
            hint = "Cole aqui o conteúdo do config.json"
            minLines = 6
            gravity = android.view.Gravity.TOP
        }
        AlertDialog.Builder(this)
            .setTitle("Importar config.json")
            .setView(campo)
            .setPositiveButton("Importar") { _, _ ->
                try {
                    config.lerJson(JSONObject(campo.text.toString()))
                    mostrarConfig()
                    config.salvar(this)
                    aviso("Importado: ${config.listas.size} lista(s).")
                } catch (e: Exception) {
                    erro("Não consegui ler o JSON: ${e.message}")
                }
            }
            .setNegativeButton("Cancelar", null)
            .show()
    }

    /** Lê os campos da tela para o config; retorna false se algo estiver inválido */
    private fun lerConfig(): Boolean {
        guardarListaAtual()
        val numeros = listOf(limite, pausa, esperaMin, esperaMax).map { it.text.toString().toIntOrNull() }
        if (numeros.any { it == null }) {
            erro("As configurações precisam ser números inteiros.")
            return false
        }
        val (lim, pau, min, max) = numeros.map { it!! }
        if (config.urls.isEmpty()) {
            erro("A lista \"${config.listaAtual}\" está vazia. Coloque pelo menos um perfil alvo.")
            return false
        }
        if (min > max) {
            erro("A espera mínima não pode ser maior que a máxima.")
            return false
        }
        if (lim < 1 || pau < 1 || min < 1) {
            erro("Os valores precisam ser maiores que zero.")
            return false
        }
        config.usuario = usuario.text.toString().trim()
        config.senha = senha.text.toString()
        config.lembrar = lembrarSenha.isChecked
        config.limite = lim
        config.pausaMinutos = pau
        config.esperaMin = min
        config.esperaMax = max
        return true
    }

    private fun salvar(avisar: Boolean): Boolean {
        if (!lerConfig()) return false
        config.salvar(this)
        // Mostra as URLs já arrumadas
        atualizarListas()
        if (avisar) aviso("Configurações salvas.")
        return true
    }

    // ---- Bot ----
    private fun iniciar() {
        if (!salvar(avisar = false)) return
        val novoBot = Bot(navegador, config, ::log, ::mostrarNavegador)
        bot = novoBot
        botaoIniciar.isEnabled = false
        botaoParar.isEnabled = true
        status.text = "Rodando"
        // Com a tela apagada o Android pausa o navegador
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        Thread {
            try {
                novoBot.executar()
            } catch (e: Exception) {
                log("⚠️ Erro: ${e.message}")
            } finally {
                runOnUiThread { aoTerminar() }
            }
        }.start()
    }

    private fun pararBot() {
        bot?.parar = true
        botaoParar.isEnabled = false
        status.text = "Parando..."
    }

    private fun aoTerminar() {
        bot = null
        botaoIniciar.isEnabled = true
        botaoParar.isEnabled = false
        status.text = "Parado"
        window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
    }

    // ---- Log ----
    /** Grava no log.txt do app e mostra na tela (pode ser chamado da thread do bot) */
    private fun log(mensagem: String) {
        // Pega a hora atual no formato: 2025-09-10 14:30:15
        val agora = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US).format(Date())
        val linha = "[$agora] $mensagem\n"
        synchronized(arquivoLog) { arquivoLog.appendText(linha) }
        runOnUiThread {
            adicionarAoLog(linha)
            ultimaLinha.text = mensagem.trim()
        }
    }

    private fun adicionarAoLog(linha: String) {
        linhasLog.addLast(linha)
        while (linhasLog.size > 300) linhasLog.removeFirst()
        textoLog.text = linhasLog.joinToString("")
    }

    /** Mostra o final do log das execuções anteriores */
    private fun carregarLog() {
        if (!arquivoLog.exists()) return
        arquivoLog.readLines().takeLast(100).forEach { linhasLog.addLast("$it\n") }
        textoLog.text = linhasLog.joinToString("")
    }

    private fun erro(mensagem: String) {
        AlertDialog.Builder(this).setTitle("Erro").setMessage(mensagem).setPositiveButton("OK", null).show()
    }

    private fun aviso(mensagem: String) {
        AlertDialog.Builder(this).setMessage(mensagem).setPositiveButton("OK", null).show()
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        when {
            painelConfig.visibility != View.VISIBLE -> painelConfig.visibility = View.VISIBLE
            // Com o bot rodando, só esconde o app em vez de fechar
            bot != null -> moveTaskToBack(true)
            else -> super.onBackPressed()
        }
    }

    override fun onDestroy() {
        bot?.parar = true
        navegador.destroy()
        super.onDestroy()
    }
}

package com.diegocop.automatizador

import android.Manifest
import android.annotation.SuppressLint
import android.app.Activity
import android.app.AlertDialog
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.PowerManager
import android.provider.Settings
import android.text.InputType
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.CheckBox
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.ScrollView
import android.widget.Spinner
import android.widget.TextView
import org.json.JSONObject

class MainActivity : Activity() {
    private lateinit var navegador: FrameLayout
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
    private lateinit var totalGeral: TextView

    private lateinit var config: Config
    private val linhasLog = ArrayDeque<String>()

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
        totalGeral = findViewById(R.id.totalGeral)

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
        findViewById<Button>(R.id.zerarTotal).setOnClickListener { zerarTotal() }
        findViewById<Button>(R.id.limparLog).setOnClickListener { limparLog() }
        mostrarTotalGeral()
        spinnerListas.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(pai: AdapterView<*>?, view: View?, posicao: Int, id: Long) {
                if (!atualizandoListas) trocarLista(config.listas.keys.elementAt(posicao))
            }

            override fun onNothingSelected(pai: AdapterView<*>?) {}
        }

        carregarLog()

        Automacao.aoLogar = { linha, mensagem ->
            if (Automacao.rodando && botaoParar.isEnabled) status.text = "Rodando · ${Automacao.totalCliques} seguidos"
            adicionarAoLog(linha)
            ultimaLinha.text = mensagem.trim()
            mostrarTotalGeral()
        }
        Automacao.aoTerminar = ::aoTerminar
        Automacao.aoPedirNavegador = ::mostrarNavegador
        if (Automacao.rodando) mostrarRodando() else aoTerminar()
    }

    override fun onStart() {
        super.onStart()
        Automacao.telaVisivel = true
        // Pega o navegador de volta da janela flutuante
        Automacao.servico?.janela?.esconder()
        Automacao.mover(this, navegador, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
    }

    override fun onStop() {
        super.onStop()
        Automacao.telaVisivel = false
        // App minimizado com o bot rodando: o navegador vai para a janela flutuante
        if (Automacao.rodando && !Automacao.pausado) Automacao.servico?.janela?.mostrar()
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
        pedirPermissoes { BotService.iniciar(this, config); mostrarRodando() }
    }

    /** Notificação, janela flutuante e bateria: o que o app precisa para rodar minimizado */
    private fun pedirPermissoes(continuar: () -> Unit) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
        ) {
            requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 1)
        }
        pedirOtimizacaoBateria()
        if (Settings.canDrawOverlays(this)) {
            continuar()
            return
        }
        AlertDialog.Builder(this)
            .setTitle("Rodar com o app minimizado")
            .setMessage(
                "Para o bot continuar funcionando enquanto você usa outros apps, permita " +
                    "\"Sobrepor a outros apps\" (o navegador fica numa janelinha no canto da tela).\n\n" +
                    "Sem essa permissão o bot só funciona com o app aberto."
            )
            .setPositiveButton("Abrir configurações") { _, _ ->
                startActivity(Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName")))
            }
            .setNegativeButton("Iniciar assim mesmo") { _, _ -> continuar() }
            .show()
    }

    /** Pede uma vez para o Android não pausar o app para economizar bateria */
    @SuppressLint("BatteryLife")
    private fun pedirOtimizacaoBateria() {
        val prefs = getSharedPreferences("config", MODE_PRIVATE)
        val energia = getSystemService(PowerManager::class.java)
        if (energia.isIgnoringBatteryOptimizations(packageName) || prefs.getBoolean("pediuBateria", false)) return
        prefs.edit().putBoolean("pediuBateria", true).apply()
        startActivity(Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, Uri.parse("package:$packageName")))
    }

    private fun pararBot() {
        BotService.parar(this)
        botaoParar.isEnabled = false
        status.text = "Parando..."
    }

    private fun mostrarRodando() {
        botaoIniciar.isEnabled = false
        botaoParar.isEnabled = true
        status.text = "Rodando · ${Automacao.totalCliques} seguidos"
        // Com o app aberto, a tela não apaga enquanto o bot roda
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
    }

    private fun mostrarTotalGeral() {
        totalGeral.text = "Total seguido (todas as execuções): ${Automacao.totalGeral(this)}"
    }

    private fun zerarTotal() {
        AlertDialog.Builder(this)
            .setTitle("Zerar total")
            .setMessage("Zerar o total de ${Automacao.totalGeral(this)} perfis seguidos?")
            .setPositiveButton("Zerar") { _, _ ->
                Automacao.zerarTotalGeral(this)
                mostrarTotalGeral()
            }
            .setNegativeButton("Cancelar", null)
            .show()
    }

    private fun aoTerminar() {
        botaoIniciar.isEnabled = true
        botaoParar.isEnabled = false
        status.text = if (Automacao.totalCliques > 0) "Parado · ${Automacao.totalCliques} seguidos" else "Parado"
        window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
    }

    // ---- Log ----
    /** As linhas mais recentes ficam em cima */
    private fun adicionarAoLog(linha: String) {
        // Mensagens com quebras de linha ("***FIM DO PROGRAMA***") viram uma linha só
        val umaLinha = linha.replace(Regex("\\s*\n\\s*"), " ").trim()
        if (umaLinha.isEmpty()) return
        linhasLog.addFirst("$umaLinha\n")
        while (linhasLog.size > 300) linhasLog.removeLast()
        textoLog.text = linhasLog.joinToString("")
    }

    /** Mostra o final do log das execuções anteriores */
    private fun carregarLog() {
        val arquivoLog = Automacao.arquivoLog(this)
        if (!arquivoLog.exists()) return
        arquivoLog.readLines().filter { it.isNotBlank() }.takeLast(100).forEach(::adicionarAoLog)
    }

    private fun limparLog() {
        AlertDialog.Builder(this)
            .setTitle("Limpar log")
            .setMessage("Apagar todo o log?")
            .setPositiveButton("Limpar") { _, _ ->
                Automacao.limparLog(this)
                linhasLog.clear()
                textoLog.text = ""
            }
            .setNegativeButton("Cancelar", null)
            .show()
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
            Automacao.rodando -> moveTaskToBack(true)
            else -> super.onBackPressed()
        }
    }

    override fun onDestroy() {
        // O bot continua no serviço; só desliga os avisos para esta tela
        Automacao.aoLogar = null
        Automacao.aoTerminar = null
        Automacao.aoPedirNavegador = null
        Automacao.liberar(applicationContext, navegador)
        super.onDestroy()
    }
}

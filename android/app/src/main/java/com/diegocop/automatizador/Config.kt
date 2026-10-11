package com.diegocop.automatizador

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject

// Lista usada na primeira vez que o app abre (a mesma do automatizador.py)
val URLS_PADRAO = listOf(
    "https://www.instagram.com/centralcaprichoso/",
    "https://www.instagram.com/boigarantido/",
    "https://www.instagram.com/canalgarantido/",
    "https://www.instagram.com/portal.garantido/",
    "https://www.instagram.com/garantidoreioficial/",
    "https://www.instagram.com/prince_amodoboi/",
    "https://www.instagram.com/boicaprichoso/",
    "https://www.instagram.com/raca.azul/",
    "https://www.instagram.com/lojacantocaprichoso/",
    "https://www.instagram.com/paulo_george__/",
)

/** Mesmo formato do config.json da versão de PC, então dá para importar o arquivo de lá */
class Config(
    var usuario: String = "",
    var senha: String = "",
    var lembrar: Boolean = false,
    var listas: LinkedHashMap<String, List<String>> = linkedMapOf("Principal" to URLS_PADRAO),
    var listaAtual: String = "Principal",
    var limite: Int = 15,          // seguidas por ciclo
    var pausaMinutos: Int = 60,    // pausa depois de atingir o limite
    var esperaMin: Int = 4,        // espera aleatória entre ações (segundos)
    var esperaMax: Int = 15,
) {
    val urls: List<String> get() = listas[listaAtual].orEmpty()

    fun paraJson(comSenha: Boolean): JSONObject {
        val jsonListas = JSONObject()
        listas.forEach { (nome, urls) -> jsonListas.put(nome, JSONArray(urls)) }
        return JSONObject()
            .put("usuario", usuario)
            .put("senha", if (comSenha) senha else "")
            .put("urls", JSONArray(urls))
            .put("listas", jsonListas)
            .put("listaAtual", listaAtual)
            .put("limite", limite)
            .put("pausaMinutos", pausaMinutos)
            .put("esperaMin", esperaMin)
            .put("esperaMax", esperaMax)
    }

    /** Copia os campos que existirem no JSON (config.json do PC ou o salvo pelo app) */
    fun lerJson(json: JSONObject) {
        usuario = json.optString("usuario", usuario)
        senha = json.optString("senha", senha)
        lembrar = senha.isNotEmpty()
        limite = json.optInt("limite", limite)
        pausaMinutos = json.optInt("pausaMinutos", pausaMinutos)
        esperaMin = json.optInt("esperaMin", esperaMin)
        esperaMax = json.optInt("esperaMax", esperaMax)

        val jsonListas = json.optJSONObject("listas")
        if (jsonListas != null && jsonListas.length() > 0) {
            listas = linkedMapOf()
            jsonListas.keys().forEach { nome -> listas[nome] = lerArray(jsonListas.getJSONArray(nome)) }
        } else if (json.has("urls")) {
            // Configs antigas só tinham "urls": vira a primeira lista
            listas = linkedMapOf("Principal" to lerArray(json.getJSONArray("urls")))
        }
        listaAtual = json.optString("listaAtual", listaAtual)
        if (listaAtual !in listas) listaAtual = listas.keys.first()
    }

    fun salvar(context: Context) {
        context.getSharedPreferences("config", Context.MODE_PRIVATE).edit()
            .putString("json", paraJson(comSenha = lembrar).toString())
            .apply()
    }

    companion object {
        fun carregar(context: Context): Config {
            val config = Config()
            val texto = context.getSharedPreferences("config", Context.MODE_PRIVATE).getString("json", null)
            if (texto != null) {
                runCatching { config.lerJson(JSONObject(texto)) }
            }
            return config
        }

        private fun lerArray(array: JSONArray): List<String> =
            lerUrls((0 until array.length()).joinToString("\n") { array.getString(it) })
    }
}

fun lerUrls(texto: String): List<String> =
    texto.lines().map(::normalizarUrl).filter { it.isNotEmpty() }.distinct()  // remove vazias e repetidas

/** Aceita 'https://www.instagram.com/perfil/', 'instagram.com/perfil', '@perfil' ou 'perfil' */
fun normalizarUrl(texto: String): String {
    val limpo = texto.trim()
    if (limpo.isEmpty()) return ""
    val perfil = (if ("instagram.com/" in limpo) limpo.substringAfter("instagram.com/") else limpo)
        .trimStart('@').trim('/').substringBefore('/').substringBefore('?')
    return if (perfil.isNotEmpty()) "https://www.instagram.com/$perfil/" else ""
}

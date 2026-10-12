package com.diegocop.automatizador

import android.annotation.SuppressLint
import android.content.Context
import android.content.Intent
import android.graphics.PixelFormat
import android.provider.Settings
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.webkit.WebView
import android.widget.FrameLayout
import kotlin.math.abs

/**
 * Janelinha por cima dos outros apps com o navegador em miniatura.
 * Com o navegador visível o Android continua desenhando a página, e o Instagram
 * continua carregando a lista de seguidores mesmo com o app minimizado.
 */
class JanelaFlutuante(private val context: Context) {
    private val wm = context.getSystemService(WindowManager::class.java)
    private var container: FrameLayout? = null

    // A página é desenhada no tamanho da tela e reduzida para caber na janelinha
    private val escala = 0.3f

    val aberta: Boolean get() = container != null

    @SuppressLint("ClickableViewAccessibility")
    fun mostrar() {
        if (aberta || !Settings.canDrawOverlays(context)) return
        val tela = context.resources.displayMetrics
        val larguraPagina = tela.widthPixels
        val alturaPagina = tela.heightPixels

        val params = WindowManager.LayoutParams(
            (larguraPagina * escala).toInt(),
            (alturaPagina * escala).toInt(),
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT,
        ).apply {
            gravity = Gravity.TOP or Gravity.END
            x = 16
            y = 200
        }

        val novo = FrameLayout(context)
        novo.elevation = 8f
        novo.clipChildren = true
        Automacao.mover(context, novo, FrameLayout.LayoutParams(larguraPagina, alturaPagina))
        (novo.getChildAt(0)).apply {
            pivotX = 0f
            pivotY = 0f
            scaleX = escala
            scaleY = escala
        }

        // Uma camada por cima do navegador: arrastar move a janela, tocar abre o app
        val toque = View(context)
        var inicioX = 0f
        var inicioY = 0f
        var janelaX = 0
        var janelaY = 0
        toque.setOnTouchListener { _, evento ->
            when (evento.action) {
                MotionEvent.ACTION_DOWN -> {
                    inicioX = evento.rawX
                    inicioY = evento.rawY
                    janelaX = params.x
                    janelaY = params.y
                }
                MotionEvent.ACTION_MOVE -> {
                    // gravity END: o x conta a partir da direita
                    params.x = janelaX - (evento.rawX - inicioX).toInt()
                    params.y = janelaY + (evento.rawY - inicioY).toInt()
                    wm.updateViewLayout(novo, params)
                }
                MotionEvent.ACTION_UP -> {
                    if (abs(evento.rawX - inicioX) < 10 && abs(evento.rawY - inicioY) < 10) abrirApp()
                }
            }
            true
        }
        novo.addView(toque, FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT))

        wm.addView(novo, params)
        container = novo
    }

    fun esconder() {
        val atual = container ?: return
        // Solta o navegador só se ele ainda estiver aqui (a tela do app pode já ter pego de volta)
        (0 until atual.childCount).map(atual::getChildAt).filterIsInstance<WebView>().forEach(atual::removeView)
        wm.removeView(atual)
        container = null
    }

    private fun abrirApp() {
        context.startActivity(
            Intent(context, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        )
    }
}

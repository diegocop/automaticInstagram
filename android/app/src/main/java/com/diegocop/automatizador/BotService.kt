package com.diegocop.automatizador

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import android.os.PowerManager

/**
 * Mantém o bot rodando com o app minimizado: notificação fixa (o Android não mata o app)
 * e trava de CPU (as esperas continuam contando com a tela apagada).
 */
class BotService : Service() {
    lateinit var janela: JanelaFlutuante
        private set
    private var trava: PowerManager.WakeLock? = null

    override fun onCreate() {
        super.onCreate()
        Automacao.servico = this
        janela = JanelaFlutuante(this)
        getSystemService(NotificationManager::class.java).createNotificationChannel(
            NotificationChannel(CANAL, "Automatizador rodando", NotificationManager.IMPORTANCE_LOW)
        )
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            PARAR -> Automacao.bot?.parar = true
            INICIAR -> iniciar()
        }
        return START_NOT_STICKY
    }

    private fun iniciar() {
        val config = Automacao.configPendente
        if (Automacao.rodando || config == null) return

        val notificacao = notificacao("Iniciando...")
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            startForeground(ID_NOTIFICACAO, notificacao, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        } else {
            startForeground(ID_NOTIFICACAO, notificacao)
        }
        trava = getSystemService(PowerManager::class.java)
            .newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "automatizador:bot")
            .apply { acquire() }

        val bot = Bot(
            Automacao.navegador(this),
            config,
            log = { Automacao.log(this, it) },
            mostrarNavegador = { Automacao.aoPedirNavegador?.invoke() },
        )
        Automacao.bot = bot
        Thread {
            try {
                bot.executar()
            } catch (e: Exception) {
                Automacao.log(this, "⚠️ Erro: ${e.message}")
            } finally {
                android.os.Handler(mainLooper).post { terminar() }
            }
        }.start()
    }

    private fun terminar() {
        Automacao.bot = null
        trava?.takeIf { it.isHeld }?.release()
        trava = null
        janela.esconder()
        Automacao.aoTerminar?.invoke()
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    fun atualizarNotificacao(texto: String) {
        if (!Automacao.rodando) return
        getSystemService(NotificationManager::class.java).notify(ID_NOTIFICACAO, notificacao(texto))
    }

    private fun notificacao(texto: String): Notification {
        val abrir = PendingIntent.getActivity(
            this, 0, Intent(this, MainActivity::class.java), PendingIntent.FLAG_IMMUTABLE
        )
        val parar = PendingIntent.getService(
            this, 1, Intent(this, BotService::class.java).setAction(PARAR), PendingIntent.FLAG_IMMUTABLE
        )
        return Notification.Builder(this, CANAL)
            .setSmallIcon(android.R.drawable.stat_notify_sync)
            .setContentTitle("Automatizador rodando")
            .setContentText(texto)
            .setContentIntent(abrir)
            .addAction(Notification.Action.Builder(null, "Parar", parar).build())
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .build()
    }

    override fun onDestroy() {
        Automacao.bot?.parar = true
        janela.esconder()
        trava?.takeIf { it.isHeld }?.release()
        Automacao.servico = null
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    companion object {
        const val INICIAR = "iniciar"
        const val PARAR = "parar"
        private const val CANAL = "bot"
        private const val ID_NOTIFICACAO = 1

        fun iniciar(context: Context, config: Config) {
            Automacao.configPendente = config
            context.startForegroundService(Intent(context, BotService::class.java).setAction(INICIAR))
        }

        fun parar(context: Context) {
            context.startService(Intent(context, BotService::class.java).setAction(PARAR))
        }
    }
}

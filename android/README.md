# Automatizador — versão Android

Mesma lógica do `automatizador.py`, mas usando um navegador interno (WebView) no lugar do Playwright.

## Gerar o APK

Precisa do JDK 17 e do Android SDK (aqui ficam em `~/android-dev`):

```bash
export JAVA_HOME=~/android-dev/jdk ANDROID_HOME=~/android-dev/sdk
./gradlew assembleRelease
```

O APK sai em `app/build/outputs/apk/release/app-release.apk`.

## Usar

- Instale o APK no celular (permita "instalar apps de fontes desconhecidas").
- Para trazer as listas do PC, toque em **Importar** e cole o conteúdo do `config.json`.
- Deixe o app aberto enquanto ele roda: com o app minimizado ou a tela desligada o Android pausa o navegador.

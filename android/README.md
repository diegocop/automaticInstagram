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
- Para rodar com o app minimizado, permita "Sobrepor a outros apps" quando o app pedir: o navegador
  vai para uma janelinha no canto da tela (arraste para mover, toque para abrir o app) e uma notificação
  mostra o andamento, com o botão Parar.
- Tire o app da otimização de bateria. Com a tela desligada o Android para de desenhar a página, então
  o bot pode falhar até a tela ligar de novo.

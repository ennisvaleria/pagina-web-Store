# Aplicación móvil de TecStore

Esta app Capacitor abre el sitio Django publicado en `https://test.coous.qzz.io`.
El servidor sigue ejecutando Django; la app necesita internet y los cambios
publicados en el servidor se reflejan sin recompilar la app.

## Preparar el proyecto

Desde esta carpeta:

```bash
npm install
npx cap add android
npx cap add ios
npm run sync
```

Los comandos para agregar una plataforma se ejecutan una sola vez. Después de
cambiar `capacitor.config.json`, ejecuta `npm run sync`.

## Compilar

- **Android:** abre el proyecto con `npm run android` y compílalo desde Android
  Studio. Se requiere Android Studio, Android SDK y JDK.
- **iPhone:** abre el proyecto con `npm run ios` y compílalo desde Xcode en una
  Mac. Apple requiere macOS/Xcode para generar y firmar la app de iOS.

Antes de publicar en tiendas, confirma que `appId` en
`capacitor.config.json` sea el identificador de paquete definitivo y propio.

## Consideraciones

- Esta es una envoltura web, no una app Django sin conexión.
- La app carga la página remota directamente y no guarda una copia local del
  sitio.
- Una app que solo muestra una web puede no cumplir los requisitos de
  funcionalidad mínima de App Store. Conviene agregar funciones móviles de
  valor antes de solicitar publicación.

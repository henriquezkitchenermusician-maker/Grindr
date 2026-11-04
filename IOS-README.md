# Open Grind para iPhone — compilación automática

Este repositorio compila **Open Grind** (código oficial, licencia MIT) para iPhone
usando los servidores Mac gratuitos de GitHub. Cada 6 horas revisa si el repositorio
oficial cambió; si cambió, genera un `.ipa` nuevo y actualiza `source.json`.
SideStore (en tu iPhone) lee esa fuente y te ofrece la actualización.

> No es una versión oficial. Open Grind dice que su versión oficial para iOS llegará
> por tiendas alternativas; cuando salga, conviene pasarse a esa.

## Parte 1 — GitHub (una sola vez, ~10 min, desde el navegador)

1. Crea una cuenta en https://github.com (gratis).
2. Botón **New repository** → nombre `open-grind-ios` → **Public**
   (público = minutos de Mac gratis e ilimitados; privado gasta el cupo muy rápido).
3. **Add file → Upload files** y arrastra todo el contenido de esta carpeta
   (incluida la carpeta `.github`). Commit.
   - Si el navegador no sube `.github`: **Add file → Create new file**, escribe
     `.github/workflows/build-ios.yml` como nombre y pega el contenido.
4. Pestaña **Settings → Actions → General → Workflow permissions** →
   marca **Read and write permissions** → Save.
5. Pestaña **Actions** → si pide activarlas, acepta → elige **Build Open Grind for iOS**
   → **Run workflow** (marca *force*) → espera ~20–40 min.
6. Al terminar verás un Release con `OpenGrind.ipa`, y `source.json` quedará relleno.

Tu URL de fuente será:

```
https://raw.githubusercontent.com/henriquezkitchenermusician-maker/Grindr/auto-update/source.json
```

## Parte 2 — iPhone con SideStore (una vez + 1 vez con computadora)

El `.ipa` sale **sin firmar**; SideStore lo firma con tu Apple ID gratis.

1. Sigue la guía oficial: https://docs.sidestore.io (necesitas una computadora
   **una sola vez** para instalar SideStore y crear el "pairing file").
2. En SideStore → **Sources → +** → pega tu URL de fuente.
3. Instala **Open Grind** desde esa fuente.
4. Desde ahí, cuando haya versión nueva, SideStore la muestra en **Updates**.

Límites del Apple ID gratis: la firma dura **7 días** (SideStore la renueva desde el
mismo iPhone con su VPN local), y máximo 3 apps sideloaded.
Con una cuenta de desarrollador de Apple (99 USD/año) la firma dura 1 año.

Alternativas: AltStore (misma fuente), o Feather / tiendas con certificado.

## Si la compilación falla

En **Actions** abre la ejecución en rojo y mira el paso que falló:
- *Generar proyecto Xcode* / *Compilar*: suele ser un cambio en el proyecto oficial.
  Reintenta con **Run workflow** más tarde; si persiste, copia el error.
- *Clonar*: el servidor oficial estaba caído; el workflow usa el espejo de GitHub
  automáticamente en la siguiente ejecución.

## Seguridad

Instala solo `.ipa` que salgan de **tu propio** repositorio. Open Grind publicó un
aviso (2026-10-22) sobre clientes de Grindr para iPhone de terceros que robaban fotos
y ubicación. Este workflow compila solo el código oficial, en el commit exacto,
y guarda el SHA-256 de cada `.ipa` en el Release.

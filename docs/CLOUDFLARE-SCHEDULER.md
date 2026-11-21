# Activar el programador externo de MAMA Tracker

Esta alternativa usa un Cloudflare Worker con Cron Trigger para iniciar el workflow existente de GitHub Actions cada 30 minutos. **No consulta YouTube ni almacena la API key de YouTube**: solo solicita a GitHub que ejecute `.github/workflows/update.yml`. La API key `YT_API_KEY` permanece en GitHub Secrets.

## 1. Crear un token de GitHub de permisos mínimos

1. Abre https://github.com/settings/personal-access-tokens/new
2. Crea un **Fine-grained personal access token**.
3. Resource owner: `luisequeira612-commits`.
4. Repository access: **Only select repositories** → `mama-tracker`.
5. Repository permissions: **Actions → Read and write**. No añadas Contents, Administration ni otros permisos.
6. Pon una expiración razonable y crea el token.
7. Copia el token temporalmente. No lo envíes por chat ni lo guardes en el repositorio.

El endpoint de GitHub para iniciar un workflow requiere permiso **Actions: write** en un fine-grained token.

## 2. Crear el Worker en Cloudflare

1. Abre https://dash.cloudflare.com/ e inicia sesión o crea una cuenta gratuita.
2. Entra en **Workers & Pages** → **Create** → **Create Worker**.
3. Pon el nombre `mama-tracker-scheduler` y despliega el Worker inicial.
4. Abre el Worker, pulsa **Edit code** y reemplaza el contenido por el archivo `cloudflare/worker.js` de este repositorio. Guarda y despliega.

El Worker no necesita una URL pública ni un dominio propio.

## 3. Guardar el token como secreto

En el Worker, abre **Settings** → **Variables and Secrets** → **Add**:

- Type: **Secret**
- Variable name: `GITHUB_TOKEN`
- Value: el fine-grained token creado en el paso 1.

Guarda el secreto. No lo añadas como variable de texto plano, no lo pongas en el código y no lo subas a GitHub.

## 4. Configurar el horario

En **Settings** → **Triggers** → **Cron Triggers**, añade:

```text
13,43 * * * *
```

Los horarios de Cloudflare Cron usan UTC. Este horario coincide con el intervalo de 30 minutos que se pretendía usar en GitHub Actions.

## 5. Comprobar que funciona

1. Abre https://github.com/luisequeira612-commits/mama-tracker/actions
2. Busca una ejecución nueva de **Update MAMA stats** cuyo evento sea `workflow_dispatch`.
3. Comprueba que termine en verde.
4. Abre https://luisequeira612-commits.github.io/mama-tracker/ y verifica que el campo de última actualización cambie.

Si no aparece la ejecución, revisa **Workers & Pages → mama-tracker-scheduler → Logs / Observability**. El Worker registra el código HTTP de error, nunca el token.

## Seguridad y límites

- El token solo tiene acceso al repositorio `mama-tracker` y permiso `Actions: write`.
- `YT_API_KEY` sigue exclusivamente en GitHub Secrets.
- El Worker no recibe la clave de YouTube ni las estadísticas.
- No hay endpoint HTTP de activación; solo un Cron Trigger.
- Si el token se revoca o expira, el Worker dejará de iniciar el workflow. Se puede sustituir el secreto `GITHUB_TOKEN` sin cambiar el código.
- No se debe fusionar el cambio que retira el cron de GitHub hasta que el Worker esté desplegado y verificado. Mientras tanto, el workflow actual de `main` no cambia.

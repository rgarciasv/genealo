/**
 * FamilySearch - Descargador de Imágenes de Libros Parroquiales (VERSIÓN 2 MEJORADA)
 * ==============================================================
 * San Juan Bautista · Bautismos enero 1801 – abril 1852
 * Elemento 16 de 19 — 379 imágenes
 * 
 * MEJORAS EN V2:
 * - Navegación exacta: En lugar de pulsar la "flecha derecha", busca el cajetín del 
 *   número de imagen, escribe el número exacto y pulsa Enter. Esto evita saltos dobles 
 *   o quedarse atascado.
 * - Verificación estricta: No descarga hasta confirmar que el número en pantalla coincide.
 * 
 * INSTRUCCIONES:
 * 1. Abre FamilySearch y navega al ELEMENTO 16 (Bautismos 1801-1852)
 * 2. Entra en la vista de la PRIMERA imagen (haz click en la miniatura 1 para abrir el visor)
 * 3. Abre DevTools (F12) → pestaña Console
 * 4. Pega este script completo y pulsa Enter
 * 
 * CONTROLES:
 *   Parar:     window._FS_STOP = true
 *   Reanudar:  descargarDesde(50)    ← desde la imagen 50
 *   Prueba:    descargarDesde(1, 5)  ← solo las 5 primeras para probar
 */

(async function () {
    'use strict';

    // ─── CONFIGURACIÓN ──────────────────────────────────────
    const TOTAL_IMAGES = 379; // Actualizado para el elemento 16
    const MIN_DELAY_MS = 4000;
    const MAX_DELAY_MS = 7000;
    const WAIT_LOAD_MS = 3500;
    const STORAGE_KEY = 'fs_scraper_state_elemento_16';
    // ─────────────────────────────────────────────────────────

    window._FS_STOP = false;

    const sleep = ms => new Promise(r => setTimeout(r, ms));
    const randDelay = () => sleep(MIN_DELAY_MS + Math.random() * (MAX_DELAY_MS - MIN_DELAY_MS));

    const log = msg => console.log(`%c[FS] ${msg}`, 'color:#2196F3;font-weight:bold');
    const ok = msg => console.log(`%c[FS] ✓ ${msg}`, 'color:#4CAF50;font-weight:bold');
    const err = msg => console.log(`%c[FS] ✗ ${msg}`, 'color:#F44336;font-weight:bold');

    // ─── LOCALIZAR ELEMENTOS DEL DOM ──────────────────────────

    function getInputImagen() {
        // Buscar el input "Imagen X de 379"
        const inputs = document.querySelectorAll('input');
        for (const input of inputs) {
            // Criterios para identificar el input correcto
            if (input.type === 'number') return input;
            if (input.className.includes('page') || input.className.includes('image')) return input;
            if (input.ariaLabel && input.ariaLabel.toLowerCase().includes('imagen')) return input;
            if (input.parentElement && input.parentElement.textContent.includes('de ' + TOTAL_IMAGES)) return input;
            if (input.parentElement && input.parentElement.textContent.includes('de 379')) return input;
        }
        return inputs.length > 0 ? inputs[0] : null;
    }

    function getImagenActual() {
        const input = getInputImagen();
        if (input) {
            const val = parseInt(input.value);
            if (!isNaN(val) && val >= 1 && val <= TOTAL_IMAGES) {
                return val;
            }
        }
        // Fallback: buscar texto "Imagen X de 379"
        const textos = document.querySelectorAll('span, div, label');
        for (const el of textos) {
            const match = el.textContent?.match(new RegExp(`(\\d+)\\s+de\\s+(?:379|${TOTAL_IMAGES})`));
            if (match) return parseInt(match[1]);
        }
        return null;
    }

    // ─── NAVEGACIÓN PRECISA ───────────────────────────────────

    function irAImagenInput(numeroDestino) {
        const input = getInputImagen();
        if (!input) {
            err('No se encontró el campo de texto de la imagen.');
            return false;
        }

        // Truco para cambiar el valor en inputs controlados por React
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeInputValueSetter.call(input, numeroDestino);
        
        // Disparar eventos para que React se entere del cambio
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Simular pulsar Enter
        input.dispatchEvent(new KeyboardEvent('keydown', { 
            key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true 
        }));
        input.dispatchEvent(new KeyboardEvent('keyup', { 
            key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true 
        }));

        return true;
    }



    async function esperarImagen(numeroEsperado) {
        let intentos = 0;
        const maxIntentos = 30; // 15 segundos máximo
        while (intentos < maxIntentos) {
            const actual = getImagenActual();
            if (actual === numeroEsperado) {
                await sleep(1500); // Dar tiempo al lienzo para que pinte la imagen real
                return true;
            }
            await sleep(500);
            intentos++;
        }
        return false;
    }

    // ─── DESCARGA ────────────────────────────────────────────

    function clickDescargar() {
        // Seleccionar los botones de descarga posibles
        const btn1 = document.querySelector('[data-testid="download-image-button"]');
        if (btn1 && btn1.getAttribute('aria-disabled') !== 'true' && btn1.offsetParent !== null) {
            btn1.click();
            return true;
        }
        
        const botones = document.querySelectorAll('button');
        for (const btn of botones) {
            const txt = (btn.ariaLabel || btn.title || btn.textContent || '').toLowerCase();
            if ((txt.includes('descargar') || txt.includes('download')) && btn.offsetParent !== null) {
                btn.click();
                return true;
            }
        }
        return false;
    }

    // ─── LOOP PRINCIPAL ──────────────────────────────────────

    async function descargarLoop(desde, hasta) {
        log(`🚀 Descargando imágenes ${desde} a ${hasta} (${hasta - desde + 1} en total)`);
        log(`⏹ Parar: window._FS_STOP = true`);
        console.log('');

        let descargadas = 0;
        let fallidas = [];

        for (let i = desde; i <= hasta; i++) {
            if (window._FS_STOP) {
                log(`⏸ Parado en imagen ${i}. Reanudar: descargarDesde(${i})`);
                break;
            }

            const progreso = `${i - desde + 1}/${hasta - desde + 1}`;
            log(`── [${progreso}] Imagen ${i}/${TOTAL_IMAGES} ──`);

            // Navegar a la imagen 'i' explícitamente mediante el cuadro de texto
            const actual = getImagenActual();
            if (actual !== i) {
                log(`Navegando a la imagen ${i} mediante el cajetín numérico...`);
                
                irAImagenInput(i);
                const llego = await esperarImagen(i);
                
                if (!llego) {
                    err(`No se pudo llegar a la imagen ${i}. Reintentando...`);
                    irAImagenInput(i);
                    await esperarImagen(i);
                }
            }

            // Esperar a que cargue la alta resolución
            await sleep(WAIT_LOAD_MS);

            // Verificar que seguimos en la imagen correcta antes de descargar
            if (getImagenActual() === i) {
                if (clickDescargar()) {
                    ok(`Descarga iniciada: imagen ${i}`);
                    descargadas++;
                } else {
                    err(`Botón de descarga no encontrado en imagen ${i}`);
                    fallidas.push(i);
                }
            } else {
                err(`Desincronización detectada en imagen ${i}. Nos saltamos.`);
                fallidas.push(i);
            }

            // Guardar progreso
            localStorage.setItem(STORAGE_KEY, JSON.stringify({
                lastCompleted: i, descargadas, fallidas,
                timestamp: new Date().toISOString()
            }));

            // Delay humano
            if (i < hasta) {
                await randDelay();
            }
        }

        // Resumen
        console.log('');
        log(`════════════════════════════════════`);
        log(`RESUMEN:`);
        log(`  ✓ Descargadas: ${descargadas}`);
        if (fallidas.length > 0) {
            err(`  ✗ Fallidas: ${fallidas.length} → [${fallidas.join(', ')}]`);
            log(`  Puedes reintentar las fallidas llamando a: descargarDesde(N, N)`);
        }
        log(`  📁 Revisa tu carpeta de Descargas`);
        log(`════════════════════════════════════`);
    }

    // ─── API GLOBAL ──────────────────────────────────────────

    window.descargarDesde = function (n, hasta) {
        window._FS_STOP = false;
        descargarLoop(n, hasta || TOTAL_IMAGES);
    };

    // Iniciar
    log(`Empezando descarga desde la imagen actual...`);
    const imgActual = getImagenActual() || 1;
    await descargarLoop(imgActual, TOTAL_IMAGES);

})();

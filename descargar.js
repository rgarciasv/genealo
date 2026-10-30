/**
 * FamilySearch - Descargador de Imágenes de Libros Parroquiales
 * ==============================================================
 * San Juan Bautista · Bautismos julio 1752 – diciembre 1800
 * Elemento 15 de 19 — 276 imágenes
 * 
 * INSTRUCCIONES:
 * 1. Abre FamilySearch y navega al ELEMENTO 15 (el libro de Bautismos)
 * 2. Entra en la vista de la PRIMERA imagen (click en la miniatura 1)
 * 3. Abre DevTools (F12) → pestaña Console
 * 4. Pega este script completo y pulsa Enter
 * 
 * CONTROLES:
 *   Parar:     window._FS_STOP = true
 *   Reanudar:  descargarDesde(50)    ← desde imagen 50
 *   Test (5):  descargarDesde(1, 5)  ← solo las 5 primeras
 */

(async function () {
    'use strict';

    // ─── CONFIGURACIÓN ──────────────────────────────────────
    const TOTAL_IMAGES = 276;
    const MIN_DELAY_MS = 4000;
    const MAX_DELAY_MS = 8000;
    const WAIT_LOAD_MS = 3000;
    const STORAGE_KEY = 'fs_scraper_state';
    // ─────────────────────────────────────────────────────────

    window._FS_STOP = false;

    const sleep = ms => new Promise(r => setTimeout(r, ms));
    const randDelay = () => sleep(MIN_DELAY_MS + Math.random() * (MAX_DELAY_MS - MIN_DELAY_MS));

    const log = msg => console.log(`%c[FS] ${msg}`, 'color:#2196F3;font-weight:bold');
    const ok = msg => console.log(`%c[FS] ✓ ${msg}`, 'color:#4CAF50;font-weight:bold');
    const err = msg => console.log(`%c[FS] ✗ ${msg}`, 'color:#F44336;font-weight:bold');

    // ─── DESCARGA ────────────────────────────────────────────

    function clickDescargar() {
        const btn = document.querySelector('[data-testid="download-image-button"]');
        if (btn && btn.getAttribute('aria-disabled') !== 'true') {
            btn.click();
            return true;
        }
        // Fallback
        const btn2 = document.querySelector('[aria-label="Descargar"]');
        if (btn2) { btn2.click(); return true; }
        return false;
    }

    // ─── NAVEGACIÓN: FLECHA DERECHA ──────────────────────────
    // La flecha derecha navega entre IMÁGENES dentro del mismo
    // elemento (libro), no entre elementos del rollo.

    function irSiguienteImagen() {
        // Simular pulsación de tecla ArrowRight en el documento
        const eventDown = new KeyboardEvent('keydown', {
            key: 'ArrowRight',
            code: 'ArrowRight',
            keyCode: 39,
            which: 39,
            bubbles: true,
            cancelable: true
        });
        const eventUp = new KeyboardEvent('keyup', {
            key: 'ArrowRight',
            code: 'ArrowRight',
            keyCode: 39,
            which: 39,
            bubbles: true,
            cancelable: true
        });

        // Enviar al elemento activo o al viewer
        const target = document.querySelector('[data-testid*="TH-"]')
            || document.activeElement
            || document.body;
        target.dispatchEvent(eventDown);
        target.dispatchEvent(eventUp);

        // También probar en document por si el viewer no captura
        document.dispatchEvent(eventDown);
        document.dispatchEvent(eventUp);

        return true;
    }

    // ─── LEER NÚMERO DE IMAGEN ACTUAL ────────────────────────

    function getImagenActual() {
        // Buscar el input "Imagen X de 276"
        const inputs = document.querySelectorAll('input');
        for (const input of inputs) {
            const val = parseInt(input.value);
            if (!isNaN(val) && val >= 1 && val <= TOTAL_IMAGES && input.offsetParent !== null) {
                return val;
            }
        }
        // Fallback: buscar texto "Imagen X de 276" o "X de 276"
        const textos = document.querySelectorAll('span, div, label');
        for (const el of textos) {
            const match = el.textContent?.match(/(\d+)\s+de\s+276/);
            if (match) return parseInt(match[1]);
        }
        return null;
    }

    // ─── ESPERAR CAMBIO DE IMAGEN ─────────────────────────────

    async function esperarCambioImagen(imagenAnterior) {
        let intentos = 0;
        const maxIntentos = 20; // 10 segundos máximo
        while (intentos < maxIntentos) {
            const actual = getImagenActual();
            if (actual && actual !== imagenAnterior) {
                await sleep(1500); // Extra para renderizado
                return actual;
            }
            await sleep(500);
            intentos++;
        }
        return null; // No cambió
    }

    // ─── LOOP PRINCIPAL ──────────────────────────────────────

    async function descargarLoop(desde, hasta) {
        log(`🚀 Descargando imágenes ${desde} a ${hasta} (${hasta - desde + 1} en total)`);
        log(`⏹ Parar: window._FS_STOP = true`);
        log(`▶ Reanudar: descargarDesde(N)`);
        log(`ℹ️ Navegación: usando tecla → (flecha derecha)`);
        console.log('');

        let descargadas = 0;
        let fallidas = [];

        // Verificar que estamos en la imagen correcta
        const actual = getImagenActual();
        if (actual !== null && actual !== desde) {
            log(`Actualmente en imagen ${actual}, necesitas estar en imagen ${desde}`);
            log(`Usa las flechas del teclado para navegar a imagen ${desde}, luego ejecuta: descargarDesde(${desde})`);
            return;
        }

        for (let i = desde; i <= hasta; i++) {
            if (window._FS_STOP) {
                log(`⏸ Parado en imagen ${i}. Reanudar: descargarDesde(${i})`);
                break;
            }

            const progreso = `${i - desde + 1}/${hasta - desde + 1}`;
            log(`── [${progreso}] Imagen ${i}/${TOTAL_IMAGES} ──`);

            // Esperar un poco para que la imagen esté cargada
            await sleep(WAIT_LOAD_MS);

            // Descargar
            if (clickDescargar()) {
                ok(`Descarga iniciada: imagen ${i}`);
                descargadas++;
            } else {
                err(`Botón no encontrado: imagen ${i}`);
                fallidas.push(i);
            }

            // Guardar progreso
            localStorage.setItem(STORAGE_KEY, JSON.stringify({
                lastCompleted: i, descargadas, fallidas,
                timestamp: new Date().toISOString()
            }));

            // Delay humano
            await randDelay();

            // Navegar a siguiente imagen (flecha derecha)
            if (i < hasta && !window._FS_STOP) {
                const imgAntes = getImagenActual();
                irSiguienteImagen();

                const imgDespues = await esperarCambioImagen(imgAntes);
                if (imgDespues) {
                    log(`Navegado a imagen ${imgDespues}`);
                } else {
                    // Si no detectamos cambio, puede que haya cambiado igual
                    log(`Navegación enviada (flecha →). Continuando...`);
                    await sleep(2000);
                }
            }
        }

        // Resumen
        console.log('');
        log(`════════════════════════════════════`);
        log(`RESUMEN:`);
        log(`  ✓ Descargadas: ${descargadas}`);
        if (fallidas.length > 0) {
            err(`  ✗ Fallidas: ${fallidas.length} → [${fallidas.join(', ')}]`);
        }
        log(`  📁 Las imágenes se descargaron a tu carpeta de Descargas`);
        log(`════════════════════════════════════`);
    }

    // ─── API GLOBAL ──────────────────────────────────────────

    window.descargarDesde = function (n, hasta) {
        window._FS_STOP = false;
        descargarLoop(n, hasta || TOTAL_IMAGES);
    };

    // Comprobar sesión anterior
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    if (saved.lastCompleted && saved.lastCompleted < TOTAL_IMAGES) {
        const next = saved.lastCompleted + 1;
        log(`📋 Sesión anterior: última imagen = ${saved.lastCompleted}`);
        log(`   Continuar: descargarDesde(${next})`);
        log(`   Empezar de cero: descargarDesde(1)`);
        log(`   Test (5 imgs): descargarDesde(1, 5)`);
    } else {
        // Iniciar
        await descargarLoop(1, TOTAL_IMAGES);
    }

})();

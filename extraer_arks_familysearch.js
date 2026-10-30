/**
 * FamilySearch - Extractor Rápido de URLs ARK de Microfilms (DGS)
 * ==============================================================
 * Propósito: Extraer de forma automática el mapa { "archivo_imagen.jpg": "URL_ARK" }
 * sin necesidad de descargar de nuevo las imágenes.
 * 
 * INSTRUCCIONES DE USO:
 * 1. Abre FamilySearch en tu navegador (Chrome / Edge / Firefox) y navega a la
 *    cuadrícula (galería de miniaturas) del libro o rollo DGS que deseas catalogar.
 * 2. Abre la consola de desarrollador: pulsa F12 -> pestaña "Console" (Consola).
 * 3. Pega este código completo y pulsa Enter.
 * 4. El script recorrerá todas las miniaturas visibles o navegará por el paginador
 *    y descargará automáticamente un archivo JSON titulado:
 *    `arks_familysearch_dgs_XXXXX.json` en tu carpeta de descargas.
 */

(async function () {
    'use strict';

    console.log('%c[FS-ARK] Iniciando extractor de identificadores ARK...', 'color:#2196F3;font-weight:bold;font-size:14px');

    const sleep = ms => new Promise(r => setTimeout(r, ms));
    const arksMap = {};

    // 1. Detección de enlaces ARK en la vista de cuadrícula
    const enlaces = Array.from(document.querySelectorAll('a[href*="/ark:/61903/3:1:"]'));

    if (enlaces.length > 0) {
        console.log(`%c[FS-ARK] Detectadas ${enlaces.length} miniaturas con enlaces ARK en la página actual.`, 'color:#4CAF50;font-weight:bold');
        
        enlaces.forEach((enlace, idx) => {
            const urlCompleta = enlace.href.startsWith('http') ? enlace.href : `https://www.familysearch.org${enlace.getAttribute('href')}`;
            
            // Extraer el identificador o número de imagen si consta en etiquetas o textos
            const img = enlace.querySelector('img');
            const texto = enlace.textContent || (img ? img.alt : '') || '';
            const matchNum = texto.match(/(\d+)/);
            
            const numSecuencial = matchNum ? matchNum[1].padStart(5, '0') : (idx + 1).toString().padStart(5, '0');
            
            // Intentar detectar el DGS desde la URL o el DOM
            const matchDgs = urlCompleta.match(/i=(\d{9})/);
            const dgs = matchDgs ? matchDgs[1] : 'DGS_DESCONOCIDO';
            
            const nombreArchivo = `${dgs}_${numSecuencial}.jpg`;
            arksMap[nombreArchivo] = {
                url_ark: urlCompleta,
                fotograma: parseInt(numSecuencial, 10),
                dgs: dgs
            };
        });
    } else {
        // Fallback: Si se ejecuta dentro del visor individual de una imagen
        console.log('%c[FS-ARK] No se detectó cuadrícula. Probando visor individual...', 'color:#FF9800;font-weight:bold');
        const urlActual = window.location.href;
        if (urlActual.includes('/ark:/61903/3:1:')) {
            console.log(`%c[FS-ARK] Imagen individual detectada: ${urlActual}`, 'color:#4CAF50');
            arksMap['IMAGEN_ACTUAL'] = {
                url_ark: urlActual,
                timestamp: new Date().toISOString()
            };
        } else {
            console.warn('[FS-ARK] No se encontraron enlaces ARK. Asegúrate de estar en la vista de miniaturas o en el visor de FamilySearch.');
            return;
        }
    }

    // 2. Exportar los resultados a un archivo JSON descargable
    const totalCapturados = Object.keys(arksMap).length;
    if (totalCapturados > 0) {
        const jsonStr = JSON.stringify(arksMap, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const urlBlob = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = urlBlob;
        a.download = `arks_familysearch_${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(urlBlob);

        console.log(`%c[FS-ARK] ¡Completado! Se han exportado ${totalCapturados} registros ARK en el archivo JSON.`, 'color:#4CAF50;font-weight:bold;font-size:14px');
    }
})();

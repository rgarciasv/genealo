---
name: transcripcion-diplomatica-parroquial
description: >-
  Motor de extracción y transcripción paleográfica diplomática folio a folio o por
  microlotes. Aplica el Protocolo de Fusión de Tomas Hermanas [Regla L-20] para cotejar
  tomas base y de corrección sin duplicados, resuelve partidas rotas o divididas al
  pie de página [Regla L-25], aplica particionado por cara en folios de densidad
  extrema (>12 asientos) y genera salida estructurada en JSON Schema estricto junto
  con Markdown diplomático.
---

# Transcripción Paleográfica Diplomática y Fusión de Tomas Hermanas

Esta skill establece las directivas ecdóticas para extraer, transcribir y estructurar actas sacramentales históricas a partir de imágenes de manuscritos del siglo XVI al XIX.

---

## 1. Protocolo de Fusión de Tomas Hermanas (`[L-20]`)

En los microfilms de FamilySearch, cuando un folio presentaba roturas, costura apretada en el lomo (*gutter shadow*) o pie cortado, el operador disparaba dos tomas sucesivas: una **toma base** y una **toma de corrección** (ej. `004306112_01872.jpg` y `01873.jpg`, `01876.jpg` y `01877.jpg`).

> [!WARNING]
> Un procesamiento ciego de ambas imágenes duplicaría el 100% de las partidas de ese folio.

* **Procedimiento Operativo:**
  1. Identificar en la guía `02` si la imagen forma parte de una pareja de tomas hermanas.
  2. Enviar **ambas imágenes simultáneamente** en el contexto de la llamada a la IA.
  3. Instruir al modelo:
     *"Analiza conjuntamente las dos tomas complementarias. Utiliza la toma de corrección para restituir el texto oculto en el lomo o mutilado en la toma base. Genera una única transcripción continua y depurada con CERO DUPLICADOS."*
  4. Registrar en los metadatos de la transcripción que el asiento fue contrastado en ambas fuentes fotográficas.

---

## 2. Tratamiento de Partidas Bipartitas / Cortadas al Pie (`[L-25]`)

Cuando una partida arranca en las últimas líneas de una página y concluye en la siguiente (intra-imagen verso $\rightarrow$ recto, o inter-imagen recto $N \rightarrow$ verso $N+1$):
* **No dividir el acta en dos fragmentos huérfanos.**
* La partida se reconstruye como **una única entidad diplomática**.
* Se añade un marcador de salto: `[SALTO DE FOLIO: f. 12v -> f. 13r]`.
* En el grafo (ArcadeDB), el acta apunta a ambos fotogramas como soportes físicos de origen.

---

## 3. Particionado por Plana en Folios de Densidad Extrema

Cuando un folio abierto contiene más de **12 asientos sacramentales** (habitual en años de peste o alta natalidad):
* Para evitar el agotamiento de tokens o truncamientos silenciosos en el modelo de lenguaje, la transcripción debe solicitarse **desglosada por plana**:
  1. Turno 1: Transcripción diplomática de la **Plana Izquierda (Verso)**.
  2. Turno 2: Transcripción diplomática de la **Plana Derecha (Recto)**.
  3. Ensamblado final unificado en memoria antes de persistir.

---

## 4. Estructura de Salida JSON Schema Canónica

Cada partida extraída debe respetar el formato JSON Schema estricto del proyecto:

```json
{
  "id_acta": "NRDL-BAUT-15940123-01",
  "tipo_sacramento": "BAUTISMO",
  "parroquia_codigo": "NRDL",
  "fecha_literal": "veinte y tres dias del mes de henero de mill y quinientos y noventa y quatro",
  "fecha_iso": "1594-01-23",
  "folio_manuscrito": "1r",
  "soporte_digital": {
    "fotograma_primario": "004306112_01873.jpg",
    "fotograma_secundario": "004306112_01872.jpg",
    "lado": "derecha"
  },
  "bautizado": {
    "nombre": "Sebastian",
    "sexo": "M",
    "legitimo": true
  },
  "padres": {
    "padre": "Matheo Sanchez",
    "madre": "Maria Hernandez",
    "vecindad": "Navarredondilla"
  },
  "padrinos": [
    {
      "nombre": "Alonso Gonzalez",
      "calidad": "PADRINO"
    }
  ],
  "ministro": "Alonso del Valle",
  "marginalia": "+ murio nino",
  "texto_diplomatico": "En veinte y tres dias del mes de henero de mill y quini[entos y noventa y quatro]...",
  "dudas_paleograficas": []
}
```

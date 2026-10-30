$carpetas = @(
    "C:\TRABAJOS\personal\genealo\imagenes\rollo 004306112",
    "C:\TRABAJOS\personal\genealo\imagenes\rollo 004306113"
)

foreach ($carpeta in$carpetas) {
    if (-not (Test-Path $carpeta)) {
        Write-Host "`n[!] La carpeta no existe, saltando: $carpeta" -ForegroundColor Yellow
        continue
    }

    $rollo = if ($carpeta -match "rollo (\d{9})") { $matches[1] } else { $null }
    if (-not $rollo) { continue }

    Write-Host "`n=================================================" -ForegroundColor Cyan
    Write-Host "Analizando rollo: DGS $rollo" -ForegroundColor Cyan
    Write-Host "Ruta: $carpeta" -ForegroundColor Cyan
    Write-Host "=================================================" -ForegroundColor Cyan

    $archivosSueltos = Get-ChildItem -Path$carpeta -Filter "*.jpg"
    
    $grupos =$archivosSueltos | Where-Object { $_.Name -match "$rollo`_(\d{5})" } | Group-Object {
        [regex]::Match($_.Name, "$rollo`_(\d{5})").Groups[1].Value
    }

    $borradosDuplicados = 0$conservados = 0

    foreach ($grupo in$grupos) {
        $numImg =$grupo.Name
        $archivos =$grupo.Group
        $nombreLimpio = "${rollo}_${numImg}.jpg"
        
        $archivoPrincipal =$archivos | Where-Object { $_.Name -eq$nombreLimpio } | Select-Object -First 1

        if (-not $archivoPrincipal) {$archivoPrincipal = $archivos[0]$rutaNueva = Join-Path -Path $carpeta -ChildPath$nombreLimpio
            Rename-Item -Path $archivoPrincipal.FullName -NewName$nombreLimpio -Force
            $archivoPrincipal = Get-Item -Path$rutaNueva
        }

        foreach ($f in$archivos) {
            if ($f.FullName -ne$archivoPrincipal.FullName) {
                Remove-Item -Path $f.FullName -Force$borradosDuplicados++
            }
        }

        $conservados++
    }

    Write-Host "--- RESULTADOS DE LA LIMPIEZA ($rollo) ---" -ForegroundColor Green
    Write-Host "Copias duplicadas eliminadas: $borradosDuplicados"
    Write-Host "Imágenes útiles en la carpeta: $conservados"
}
# Informe de verificación Go

Copia esta plantilla y rellena cada campo con la salida real. No declares un estado sin evidencia.

## Resultado de la verificación Go

```text
Estado: completado | parcial | bloqueado
Raíz verificada: <ruta relativa>
Comandos ejecutados:
- gofmt -l .: <sin salida | ficheros listados>
- go build ./...: <ok | error>
- go test ./...: <ok | fallos>
- go vet ./...: <ok | hallazgos>
- go test -race ./...: <ok | no aplica | no disponible>
- golangci-lint run: <ok | no configurado | no disponible>
Pruebas añadidas: <lista>
Pruebas modificadas: <lista>
Cobertura: <dato si existe; no es un objetivo>
No verificado: <lista con motivo, o "ninguno">
```

## Fallos y bloqueos

| Comprobación | Estado | Evidencia | Acción |
|---|---|---|---|
| | | | |

## Comportamientos cubiertos

| Comportamiento | Capa | Test |
|---|---|---|
| | | |

## Comportamientos no cubiertos

| Comportamiento | Motivo | Riesgo |
|---|---|---|
| | | |

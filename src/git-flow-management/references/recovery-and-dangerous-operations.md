# Recuperación y operaciones peligrosas

Usa esta referencia solo ante una petición explícita de recuperar, sobrescribir, borrar o reescribir historial.

## Autorización específica

Expón datos o historia que podrían perderse, alcance local o remoto, alternativas seguras y el comando exacto. Exige una confirmación que autorice ese comando concreto. Una aprobación genérica no sirve.

## Orden de recuperación

1. Inspecciona estado, historial y reflog.
2. Identifica commits recuperables y preserva evidencia.
3. Prefiere revertir o crear un commit correctivo.
4. Usa reset destructivo, clean, force push o borrado solo cuando el usuario acepte expresamente sus consecuencias.

No encadenes comandos destructivos. Verifica después de cada comando autorizado.

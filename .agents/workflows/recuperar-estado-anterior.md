---
description: Cómo recuperar el estado estable de abril 2026 en caso de emergencia
---

Este flujo de trabajo permite regresar la aplicación al punto exacto en el que se encontraba el 3 de abril de 2026, antes de iniciar las reformas estéticas.

### Pasos para el Agente (o el usuario):

1. **Verificar el estado actual**:
   - Ejecutar `git status` para ver en qué punto estamos.

2. **Regresar al "Punto de Guardado"**:
   - Ejecutar `git checkout v-funcional-abril-2026`. 
   - Esto pondrá todos los archivos de la aplicación exactamente como estaban antes de las reformas.

3. **Para deshacer cambios en la rama de reformas y re-empezar**:
   - Si los cambios en la rama `reforma-cine` no te gustan y quieres borrarlos todos:
   - Ejecutar `git reset --hard v-funcional-abril-2026`.

> [!IMPORTANT]  
> Recuerda que siempre trabajamos sobre la rama `reforma-cine`. La rama `main` se mantiene intacta como copia de seguridad adicional en GitHub.

# Frontend - IRA Municipal

Este frontend es un scaffold Next.js en TypeScript que usa Mapbox GL JS.

Pasos para ejecutar localmente:

1. Ir a la carpeta `frontend`.
2. Instalar dependencias: `npm install`.
3. Crear `.env.local` con `NEXT_PUBLIC_MAPBOX_TOKEN=tu_token`.
4. Ejecutar: `npm run dev`.

El mapa está centrado en Colombia y consumirá el endpoint `/municipios` del backend.

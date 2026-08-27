/// <reference types="vite/client" />

interface Window {
  secretApi: {
    ping: () => Promise<{ ok: boolean }>;
  };
}

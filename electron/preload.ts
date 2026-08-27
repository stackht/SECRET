import { contextBridge, ipcRenderer } from "electron";

declare global {
  interface Window {
    secretApi: {
      ping: () => Promise<{ ok: boolean }>;
    };
  }
}

contextBridge.exposeInMainWorld("secretApi", {
  ping: () => ipcRenderer.invoke("secret:ping")
});

export type SecretApi = Window["secretApi"];

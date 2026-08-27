import { app, BrowserWindow, ipcMain } from "electron";
import path from "node:path";

const isDev = !app.isPackaged;

function createWindow() {
  const win = new BrowserWindow({
    width: 1600,
    height: 1000,
    minWidth: 1280,
    minHeight: 780,
    backgroundColor: "#080A0F",
    title: "SECRET",
    webPreferences: {
      preload: path.join(app.getAppPath(), "dist-electron", "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  if (isDev) {
    win.loadURL("http://localhost:5173");
    win.webContents.openDevTools({ mode: "detach" });
  } else {
    win.loadFile(path.join(app.getAppPath(), "dist", "index.html"));
    win.webContents.openDevTools({ mode: "detach" });
  }

  win.webContents.on("render-process-gone", (_, details) => {
    console.error("render-process-gone", details);
  });
  win.webContents.on("console-message", (_, level, message, line, sourceId) => {
    console.log(`[renderer:${level}] ${message} (${sourceId}:${line})`);
  });
}

app.whenReady().then(() => {
  ipcMain.handle("secret:ping", () => ({ ok: true }));
  createWindow();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

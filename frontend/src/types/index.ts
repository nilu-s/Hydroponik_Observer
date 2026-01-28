export type Setup = {
  setupId: string;
  name: string;
  port: string | null;
  cameraPort: string | null;
  valueIntervalMinutes: number;
  photoIntervalMinutes: number;
};

export type NodeInfo = {
  port: string;
  alias?: string;
  kind: "real" | "dummy";
  status: "online" | "offline" | "unknown";
  fw?: string;
  mode?: "real" | "debug";
};

export type CameraDevice = {
  cameraId: string;
  deviceId: string;
  alias?: string;
  pnpDeviceId?: string;
  containerId?: string;
  friendlyName?: string;
  status?: "online" | "offline";
};

export type Reading = {
  ts: number;
  ph?: number;
  ec?: number;
  temp?: number;
  status: string[];
};

export type StoredReading = {
  id: number;
  setup_id: string;
  node_id: string;
  ts: number;
  ph: number | null;
  ec: number | null;
  temp: number | null;
  status_json: string;
};

export type StoredPhoto = {
  id: number;
  setup_id: string;
  camera_id: string;
  ts: number;
  path: string;
};

export type WsClientMsg =
  | { t: "sub"; setupId: string }
  | { t: "unsub"; setupId: string };

export type WsServerMsg =
  | ({ t: "reading"; setupId: string } & Reading)
  | { t: "cameraDevices"; devices: CameraDevice[] }
  | { t: "device"; setupId: string; node?: string; camera?: string }
  | { t: "reset"; reason?: string }
  | { t: "error"; setupId?: string; msg: string };

import { getBackendBaseUrl } from "./backend-url";
import { CameraDevice, NodeInfo, Reading, Setup } from "../types";

const getAuthHeaders = (): Record<string, string> => {
  const token = localStorage.getItem("sensorhub.jwt");
  if (!token) {
    return {};
  }
  return { Authorization: `Bearer ${token}` };
};

const getCsrfHeaders = (): Record<string, string> => {
  const token = localStorage.getItem("sensorhub.csrf");
  if (!token) {
    return {};
  }
  return { "X-CSRF-Token": token };
};

const buildHeaders = (headers?: HeadersInit): HeadersInit => ({
  ...getAuthHeaders(),
  ...getCsrfHeaders(),
  ...(headers ?? {}),
});

const handleResponse = async <T,>(res: Response): Promise<T> => {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return (await res.json()) as T;
};

export const getSetups = async (): Promise<Setup[]> => {
  const res = await fetch(`${getBackendBaseUrl()}/api/setups`, {
    headers: buildHeaders(),
  });
  return handleResponse<Setup[]>(res);
};

export const createSetup = async (name: string): Promise<Setup> => {
  const res = await fetch(`${getBackendBaseUrl()}/api/setups`, {
    method: "POST",
    headers: buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ name }),
  });
  return handleResponse<Setup>(res);
};

export const patchSetup = async (
  setupId: string,
  patch: Partial<Setup>
): Promise<Setup> => {
  const res = await fetch(`${getBackendBaseUrl()}/api/setups/${setupId}`, {
    method: "PATCH",
    headers: buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(patch),
  });
  return handleResponse<Setup>(res);
};

export const deleteSetup = async (setupId: string): Promise<void> => {
  const res = await fetch(`${getBackendBaseUrl()}/api/setups/${setupId}`, {
    method: "DELETE",
    headers: buildHeaders(),
  });
  await handleResponse(res);
};

export const getNodes = async (): Promise<NodeInfo[]> => {
  const res = await fetch(`${getBackendBaseUrl()}/api/nodes`, {
    headers: buildHeaders(),
  });
  return handleResponse<NodeInfo[]>(res);
};

export const deleteNode = async (port: string): Promise<void> => {
  const res = await fetch(`${getBackendBaseUrl()}/api/nodes/${port}`, {
    method: "DELETE",
    headers: buildHeaders(),
  });
  await handleResponse(res);
};

export const updateNodeAlias = async (port: string, alias: string): Promise<NodeInfo> => {
  const res = await fetch(`${getBackendBaseUrl()}/api/nodes/${port}`, {
    method: "PATCH",
    headers: buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ alias }),
  });
  return handleResponse<NodeInfo>(res);
};

export const sendNodeCommand = async (
  port: string,
  payload: Record<string, unknown>
): Promise<Record<string, unknown>> => {
  const res = await fetch(`${getBackendBaseUrl()}/api/nodes/${port}/command`, {
    method: "POST",
    headers: buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  return handleResponse<Record<string, unknown>>(res);
};

export const setNodeMode = async (port: string, mode: "real" | "debug"): Promise<void> => {
  await sendNodeCommand(port, { t: "set_mode", mode });
};

export const setNodeSim = async (
  port: string,
  payload: { ph?: number; ec?: number; temp?: number }
): Promise<void> => {
  await sendNodeCommand(port, {
    t: "set_sim",
    simPh: payload.ph,
    simEc: payload.ec,
    simTemp: payload.temp,
  });
};

export const requestNodeReading = async (port: string): Promise<Record<string, unknown>> => {
  return sendNodeCommand(port, { t: "get_all" });
};

export const getCameraDevices = async (): Promise<CameraDevice[]> => {
  const res = await fetch(`${getBackendBaseUrl()}/api/cameras/devices`, {
    headers: buildHeaders(),
  });
  return handleResponse<CameraDevice[]>(res);
};

export const deleteCamera = async (cameraId: string): Promise<void> => {
  const res = await fetch(
    `${getBackendBaseUrl()}/api/cameras/${encodeURIComponent(cameraId)}`,
    {
    method: "DELETE",
    headers: buildHeaders(),
    }
  );
  await handleResponse(res);
};

export const updateCameraAlias = async (
  cameraId: string,
  alias: string | null
): Promise<CameraDevice> => {
  const res = await fetch(
    `${getBackendBaseUrl()}/api/cameras/${encodeURIComponent(cameraId)}`,
    {
      method: "PATCH",
      headers: buildHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ alias }),
    }
  );
  return handleResponse<CameraDevice>(res);
};

export const getReading = async (setupId: string): Promise<Reading | null> => {
  const res = await fetch(`${getBackendBaseUrl()}/api/setups/${setupId}/reading`, {
    headers: buildHeaders(),
  });
  return handleResponse<Reading | null>(res);
};

export const captureReading = async (setupId: string): Promise<Reading> => {
  const res = await fetch(`${getBackendBaseUrl()}/api/setups/${setupId}/capture-reading`, {
    method: "POST",
    headers: buildHeaders(),
  });
  return handleResponse<Reading>(res);
};

export const capturePhoto = async (setupId: string) => {
  const res = await fetch(`${getBackendBaseUrl()}/api/setups/${setupId}/capture-photo`, {
    method: "POST",
    headers: buildHeaders(),
  });
  return handleResponse(res);
};

export const getHistory = async (setupId: string, limit = 200) => {
  const res = await fetch(
    `${getBackendBaseUrl()}/api/setups/${setupId}/history?limit=${limit}`,
    {
      headers: buildHeaders(),
    }
  );
  return handleResponse(res);
};

export const exportAllData = async (): Promise<Blob> => {
  const res = await fetch(`${getBackendBaseUrl()}/api/export/all`, {
    headers: buildHeaders(),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.blob();
};

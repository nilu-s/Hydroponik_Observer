import { useEffect, useState } from "react";

import {
  deleteCamera,
  deleteNode,
  exportAllData,
  getCameraDevices,
  getNodes,
  requestNodeReading,
  setNodeMode,
  updateCameraAlias,
  updateNodeAlias,
} from "../services/api";
import { CameraDevice, NodeInfo } from "../types";

type Props = {
  onBack: () => void;
};

const SettingsPage = ({ onBack }: Props) => {
  const normalizeCameraId = (cameraIdValue: string) => {
    return cameraIdValue.replace(/^fallback:/i, "");
  };

  const [nodes, setNodes] = useState<NodeInfo[]>([]);
  const [cameraDevices, setCameraDevices] = useState<CameraDevice[]>([]);
  const [refreshError, setRefreshError] = useState<string | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedCameraId, setSelectedCameraId] = useState<string | null>(null);
  const [nodeState, setNodeState] = useState<
    Record<
      string,
      {
        name: string;
        mode: "real" | "debug";
        status: string;
        isBusy: boolean;
      }
    >
  >({});
  const [cameraState, setCameraState] = useState<
    Record<
      string,
      {
        alias: string;
      }
    >
  >({});

  const loadData = async () => {
    try {
      const [nodeData, cameraData] = await Promise.all([getNodes(), getCameraDevices()]);
      setNodes(nodeData);
      setCameraDevices(cameraData);
      setRefreshError(null);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to refresh data.";
      setRefreshError(message);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      Promise.all([getNodes(), getCameraDevices()])
        .then(([nodeData, cameraData]) => {
          setNodes(nodeData);
          setCameraDevices(cameraData);
          setRefreshError(null);
        })
        .catch((error) => {
          const message = error instanceof Error ? error.message : "Failed to refresh data.";
          setRefreshError(message);
        });
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setNodeState((prev) => {
      const next = { ...prev };
      nodes.forEach((node) => {
        const nodeKey = node.nodeId ?? node.port ?? "";
        if (!nodeKey) {
          return;
        }
        if (!next[nodeKey]) {
          next[nodeKey] = {
            name: node.alias ?? node.port ?? node.nodeId ?? nodeKey,
            mode: node.mode ?? "real",
            status: "",
            isBusy: false,
          };
        } else if (
          node.alias &&
          (next[nodeKey].name === node.nodeId || next[nodeKey].name === node.port)
        ) {
          next[nodeKey] = {
            ...next[nodeKey],
            name: node.alias,
          };
        }
      });
      return next;
    });
  }, [nodes]);

  useEffect(() => {
    setCameraState((prev) => {
      const next = { ...prev };
      cameraDevices.forEach((camera) => {
        if (!next[camera.cameraId]) {
          next[camera.cameraId] = {
            alias:
              camera.alias ?? camera.friendlyName ?? normalizeCameraId(camera.cameraId),
          };
        } else if (camera.alias && next[camera.cameraId].alias === camera.cameraId) {
          next[camera.cameraId] = {
            ...next[camera.cameraId],
            alias: camera.alias,
          };
        }
      });
      return next;
    });
  }, [cameraDevices]);

  const updateNodeState = (
    nodeId: string,
    patch: Partial<(typeof nodeState)[string]>
  ) => {
    setNodeState((prev) => ({
      ...prev,
      [nodeId]: {
        ...(prev[nodeId] ?? {
          mode: "real",
          status: "",
          isBusy: false,
        }),
        ...patch,
      },
    }));
  };

  const handleExportAll = async () => {
    try {
      const blob = await exportAllData();
      const now = new Date();
      const stamp = now
        .toISOString()
        .replace(/[:.]/g, "-")
        .replace("T", "_")
        .slice(0, 19);
      const fileName = `sensorhub-export_${stamp}.zip`;
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Export failed";
      alert(message);
    }
  };


  const handleDeleteNode = async (nodeId: string) => {
    if (!window.confirm(`Delete node ${nodeId}? This also deletes its photos.`)) {
      return;
    }
    try {
      await deleteNode(nodeId);
      await loadData();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Delete failed";
      alert(message);
    }
  };

  const handleDeleteCamera = async (cameraId: string) => {
    if (!window.confirm(`Delete camera ${cameraId}?`)) {
      return;
    }
    try {
      await deleteCamera(cameraId);
      await loadData();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Delete failed";
      alert(message);
    }
  };

  const handleModeChange = async (nodeId: string, mode: "real" | "debug") => {
    updateNodeState(nodeId, { mode, isBusy: true, status: "" });
    try {
      await setNodeMode(nodeId, mode);
      updateNodeState(nodeId, { status: "Mode updated." });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Command failed";
      updateNodeState(nodeId, { status: message });
    } finally {
      updateNodeState(nodeId, { isBusy: false });
    }
  };

  const handleReadNow = async (nodeId: string) => {
    updateNodeState(nodeId, { isBusy: true, status: "" });
    try {
      const response = await requestNodeReading(nodeId);
      updateNodeState(nodeId, { status: `Reply: ${JSON.stringify(response)}` });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Command failed";
      updateNodeState(nodeId, { status: message });
    } finally {
      updateNodeState(nodeId, { isBusy: false });
    }
  };

  const selectedNode = selectedNodeId
    ? nodes.find((item) => (item.nodeId ?? item.port) === selectedNodeId) ?? null
    : null;
  const selectedState = selectedNodeId ? nodeState[selectedNodeId] ?? null : null;
  const selectedAlias =
    selectedNode && selectedState
      ? selectedNode.alias ?? selectedNode.port ?? selectedNode.nodeId
      : null;
  const selectedCamera = selectedCameraId
    ? cameraDevices.find((item) => item.cameraId === selectedCameraId) ?? null
    : null;
  const selectedCameraState = selectedCameraId ? cameraState[selectedCameraId] ?? null : null;
  const selectedCameraAlias = selectedCamera
    ? selectedCamera.alias ??
      selectedCamera.friendlyName ??
      normalizeCameraId(selectedCamera.cameraId)
    : null;

  const handleCloseModal = async () => {
    if (selectedNode && selectedState && selectedAlias !== null) {
      const trimmed = selectedState.name.trim();
      const nextAlias = trimmed.length ? trimmed : selectedNode.nodeId;
      if (nextAlias !== selectedAlias) {
        try {
          await updateNodeAlias(selectedNode.nodeId, nextAlias);
        } catch {
          // Ignore save errors on close to avoid blocking UX.
        }
      }
    }
    setSelectedNodeId(null);
  };

  const handleCloseCameraModal = async () => {
    if (selectedCamera && selectedCameraState && selectedCameraAlias !== null) {
      const trimmed = selectedCameraState.alias.trim();
      const nextAlias = trimmed.length ? trimmed : null;
      if (nextAlias !== selectedCameraAlias) {
        try {
          await updateCameraAlias(selectedCamera.cameraId, nextAlias);
        } catch {
          // Ignore save errors on close to avoid blocking UX.
        }
      }
    }
    setSelectedCameraId(null);
  };

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Settings</h1>
          <p className="subtitle">Global node and camera configuration</p>
          {refreshError && <p className="hint error">{refreshError}</p>}
        </div>
        <div className="header-actions">
          <button className="button" onClick={onBack}>
            Back
          </button>
          <button className="button" onClick={handleExportAll}>
            Export
          </button>
        </div>
      </header>

      <div className="settings-stack">
        <div className="section">
          <div className="section-title">Nodes</div>
          {nodes.length === 0 && <div className="hint">No nodes found.</div>}
          <div className="device-grid is-compact">
            {nodes
              .map((node) => ({
                ...node,
                key: node.nodeId ?? node.port ?? "",
              }))
              .filter((node) => node.key)
              .map((node) => (
              <button
                key={node.key}
                type="button"
                className={`tile device-tile is-compact${
                  selectedNodeId === node.key ? " is-active" : ""
                } node-tile`}
                onClick={() => setSelectedNodeId(node.key)}
              >
                <div className="device-title">
                  {node.key} · {node.alias ?? node.port ?? node.nodeId ?? node.key}
                </div>
                <div className="hint">
                  {node.status} · {node.mode ?? "unknown"}
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="section">
          <div className="section-title">Cameras</div>
          <div className="device-grid">
            {cameraDevices.length === 0 && <div className="hint">No cameras found.</div>}
            {cameraDevices.map((camera) => (
              <div
                key={camera.cameraId}
                role="button"
                tabIndex={0}
                className={`tile device-tile${
                  selectedCameraId === camera.cameraId ? " is-active" : ""
                }`}
                onClick={() => setSelectedCameraId(camera.cameraId)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    setSelectedCameraId(camera.cameraId);
                  }
                }}
              >
                <div className="device-title">
                  {camera.alias ||
                    camera.friendlyName ||
                    normalizeCameraId(camera.cameraId)}
                </div>
                <div className="hint">
                  {camera.friendlyName ? `${camera.friendlyName} · ` : ""}
                  {camera.status ?? "offline"}
                </div>
                <div className="device-actions">
                  <button
                    className="button small danger"
                    onClick={(event) => {
                      event.stopPropagation();
                      handleDeleteCamera(camera.cameraId);
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {selectedNode && selectedState && (
        <div className="modal-overlay">
          <div
            className="modal modal-node"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <div className="modal-title">Node details</div>
                <div className="modal-subtitle">
                  {selectedNode.kind} · {selectedNode.status} · mode:{" "}
                  {selectedNode.mode ?? "unknown"}
                </div>
              </div>
              <button className="button small" onClick={handleCloseModal}>
                Close
              </button>
            </div>
            <div className="modal-divider" />
            <div className="row grid-two">
              <div className="field">
                <label className="label">Alias</label>
                <input
                  className="input compact"
                  value={selectedState.name}
                  onChange={(event) =>
                    updateNodeState(selectedNode.nodeId, { name: event.target.value })
                  }
                  placeholder={selectedNode.port ?? selectedNode.nodeId}
                />
              </div>
            </div>
            <div className="row grid-two">
              <div className="field">
                <label className="label">Mode</label>
                <select
                  className="select"
                  value={selectedState.mode}
                  onChange={(event) =>
                    handleModeChange(
                      selectedNode.nodeId,
                      event.target.value as "real" | "debug"
                    )
                  }
                >
                  <option value="real">real</option>
                  <option value="debug">debug</option>
                </select>
              </div>
              <div className="field">
                <label className="label">Actions</label>
                <div className="row compact">
                  <button
                    className="button small"
                  onClick={() => handleReadNow(selectedNode.nodeId)}
                    disabled={selectedState.isBusy}
                  >
                    Read now
                  </button>
                </div>
              </div>
            </div>
            {selectedState.status && <div className="hint">{selectedState.status}</div>}
            <div className="modal-actions modal-footer">
              <button
                className="button small danger"
                onClick={() => handleDeleteNode(selectedNode.nodeId)}
              >
                Delete node
              </button>
            </div>
          </div>
        </div>
      )}

      {selectedCamera && selectedCameraState && (
        <div className="modal-overlay">
          <div
            className="modal modal-node"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <div className="modal-title">Camera details</div>
                <div className="modal-subtitle">{selectedCamera.status ?? "offline"}</div>
              </div>
              <button className="button small" onClick={handleCloseCameraModal}>
                Close
              </button>
            </div>
            <div className="modal-divider" />
            <div className="row grid-two">
              <div className="field">
                <label className="label">Alias</label>
                <input
                  className="input compact"
                  value={selectedCameraState.alias}
                  onChange={(event) =>
                    setCameraState((prev) => ({
                      ...prev,
                      [selectedCamera.cameraId]: {
                        ...(prev[selectedCamera.cameraId] ?? {
                          alias: selectedCamera.alias ?? selectedCamera.cameraId,
                        }),
                        alias: event.target.value,
                      },
                    }))
                  }
                  placeholder={normalizeCameraId(selectedCamera.cameraId)}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsPage;

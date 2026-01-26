import { useEffect, useMemo, useState } from "react";

import {
  deleteCamera,
  deleteNode,
  exportAllData,
  getCameraDevices,
  getNodes,
  requestNodeReading,
  setNodeMode,
  updateNodeName,
} from "../services/api";
import { CameraDevice, NodeInfo } from "../types";

type Props = {
  onBack: () => void;
};

const SettingsPage = ({ onBack }: Props) => {
  const [nodes, setNodes] = useState<NodeInfo[]>([]);
  const [cameraDevices, setCameraDevices] = useState<CameraDevice[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
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

  const loadData = async () => {
    const [nodeData, cameraData] = await Promise.all([getNodes(), getCameraDevices()]);
    setNodes(nodeData);
    setCameraDevices(cameraData);
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      getNodes().then(setNodes).catch(() => null);
      getCameraDevices().then(setCameraDevices).catch(() => null);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setNodeState((prev) => {
      const next = { ...prev };
      nodes.forEach((node) => {
        if (!next[node.nodeId]) {
          next[node.nodeId] = {
            name: node.name ?? node.nodeId,
            mode: node.mode ?? "real",
            status: "",
            isBusy: false,
          };
        } else if (node.name && next[node.nodeId].name === node.nodeId) {
          next[node.nodeId] = {
            ...next[node.nodeId],
            name: node.name,
          };
        }
      });
      return next;
    });
  }, [nodes]);

  const activeNodes = useMemo(
    () => nodes.filter((node) => node.nodeId !== "DUMMY"),
    [nodes]
  );

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

  const handleRename = async (nodeId: string) => {
    const current = nodeState[nodeId];
    if (!current) {
      return;
    }
    updateNodeState(nodeId, { isBusy: true, status: "" });
    try {
      await updateNodeName(nodeId, current.name);
      updateNodeState(nodeId, { status: "Name updated." });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Rename failed";
      updateNodeState(nodeId, { status: message });
    } finally {
      updateNodeState(nodeId, { isBusy: false });
    }
  };

  const selectedNode = selectedNodeId
    ? activeNodes.find((item) => item.nodeId === selectedNodeId) ?? null
    : null;
  const selectedState = selectedNodeId ? nodeState[selectedNodeId] ?? null : null;

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Settings</h1>
          <p className="subtitle">Global node and camera configuration</p>
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
          {activeNodes.length === 0 && <div className="hint">No nodes found.</div>}
          <div className="device-grid is-compact">
            {activeNodes.map((node) => (
              <button
                key={node.nodeId}
                type="button"
                className={`tile device-tile is-compact${
                  selectedNodeId === node.nodeId ? " is-active" : ""
                } node-tile`}
                onClick={() => setSelectedNodeId(node.nodeId)}
              >
                <div className="device-title">{node.name ?? node.nodeId}</div>
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
              <div key={camera.cameraId} className="tile device-tile">
                <div className="device-title">{camera.friendlyName || camera.cameraId}</div>
                <div className="hint">{camera.status ?? "offline"}</div>
                <div className="device-actions">
                  <button
                    className="button small danger"
                    onClick={() => handleDeleteCamera(camera.cameraId)}
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
        <div className="modal-overlay" onClick={() => setSelectedNodeId(null)}>
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
              <button className="button small" onClick={() => setSelectedNodeId(null)}>
                Close
              </button>
            </div>
            <div className="modal-divider" />
            <div className="row grid-two">
              <div className="field">
                <label className="label">Name</label>
                <input
                  className="input compact"
                  value={selectedState.name}
                  onChange={(event) =>
                    updateNodeState(selectedNode.nodeId, { name: event.target.value })
                  }
                  placeholder={selectedNode.nodeId}
                />
              </div>
              <div className="field">
                <label className="label">Name Action</label>
                <div className="row compact">
                  <button
                    className="button small"
                    onClick={() => handleRename(selectedNode.nodeId)}
                    disabled={selectedState.isBusy}
                  >
                    Save name
                  </button>
                </div>
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
    </div>
  );
};

export default SettingsPage;

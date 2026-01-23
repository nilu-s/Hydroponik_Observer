import { FC, useEffect, useMemo, useState } from "react";

import { CameraDevice, NodeInfo } from "../../types";

type Props = {
  isOpen: boolean;
  nodes: NodeInfo[];
  cameraDevices: CameraDevice[];
  onClose: () => void;
  onDeleteNode: (nodeId: string) => void;
  onDeleteCamera: (cameraId: string) => void;
  onExportAll: () => void;
  onSetNodeMode: (nodeId: string, mode: "real" | "debug") => Promise<void>;
  onSetNodeSim: (
    nodeId: string,
    payload: { ph?: number; ec?: number; temp?: number }
  ) => Promise<void>;
  onRenameNode: (nodeId: string, name: string) => Promise<void>;
  onRequestNodeReading: (nodeId: string) => Promise<Record<string, unknown>>;
  onResetNodeSim: (nodeId: string) => Promise<void>;
};

const SettingsModal: FC<Props> = ({
  isOpen,
  nodes,
  cameraDevices,
  onClose,
  onDeleteNode,
  onDeleteCamera,
  onExportAll,
  onSetNodeMode,
  onSetNodeSim,
  onRenameNode,
  onRequestNodeReading,
  onResetNodeSim,
}) => {
  if (!isOpen) {
    return null;
  }

  const [nodeState, setNodeState] = useState<
    Record<
      string,
      {
        name: string;
        mode: "real" | "debug";
        simPh: string;
        simEc: string;
        simTemp: string;
        status: string;
        isBusy: boolean;
      }
    >
  >({});
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  useEffect(() => {
    setNodeState((prev) => {
      const next = { ...prev };
      nodes.forEach((node) => {
        if (!next[node.nodeId]) {
          next[node.nodeId] = {
            name: node.name ?? node.nodeId,
            mode: node.mode ?? "real",
            simPh: "",
            simEc: "",
            simTemp: "",
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
          simPh: "",
          simEc: "",
          simTemp: "",
          status: "",
          isBusy: false,
        }),
        ...patch,
      },
    }));
  };

  const handleSendMode = async (nodeId: string) => {
    const current = nodeState[nodeId];
    if (!current) {
      return;
    }
    updateNodeState(nodeId, { isBusy: true, status: "" });
    try {
      await onSetNodeMode(nodeId, current.mode);
      updateNodeState(nodeId, { status: "Mode updated." });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Command failed";
      updateNodeState(nodeId, { status: message });
    } finally {
      updateNodeState(nodeId, { isBusy: false });
    }
  };

  const handleSendSim = async (nodeId: string) => {
    const current = nodeState[nodeId];
    if (!current) {
      return;
    }
    const payload: { ph?: number; ec?: number; temp?: number } = {};
    if (current.simPh.trim() !== "") {
      payload.ph = Number(current.simPh);
    }
    if (current.simEc.trim() !== "") {
      payload.ec = Number(current.simEc);
    }
    if (current.simTemp.trim() !== "") {
      payload.temp = Number(current.simTemp);
    }
    updateNodeState(nodeId, { isBusy: true, status: "" });
    try {
      await onSetNodeSim(nodeId, payload);
      updateNodeState(nodeId, { status: "Sim values sent." });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Command failed";
      updateNodeState(nodeId, { status: message });
    } finally {
      updateNodeState(nodeId, { isBusy: false });
    }
  };

  const handleResetSim = async (nodeId: string) => {
    updateNodeState(nodeId, { isBusy: true, status: "" });
    try {
      await onResetNodeSim(nodeId);
      updateNodeState(nodeId, { status: "Simulation reset to random." });
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
      const response = await onRequestNodeReading(nodeId);
      updateNodeState(
        nodeId,
        { status: `Reply: ${JSON.stringify(response)}` }
      );
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
      await onRenameNode(nodeId, current.name);
      updateNodeState(nodeId, { status: "Name updated." });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Rename failed";
      updateNodeState(nodeId, { status: message });
    } finally {
      updateNodeState(nodeId, { isBusy: false });
    }
  };

  return (
    <div className="modal-overlay">
      <div className="wizard compact-modal">
        <div className="wizard-header">
          <div>
            <div className="wizard-title">Settings</div>
            <div className="wizard-subtitle">Manage nodes and cameras</div>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Close settings">
            ✕
          </button>
        </div>
        <div className="wizard-content">
          <div className="wizard-actions-right">
            <button className="button" onClick={onExportAll}>
              Export data
            </button>
          </div>
          <div className="device-group">
            <div className="device-group-title">
              {selectedNodeId ? "Node settings" : "Nodes"}
            </div>
            {selectedNodeId ? (
              (() => {
                const node = activeNodes.find((item) => item.nodeId === selectedNodeId);
                const state = selectedNodeId ? nodeState[selectedNodeId] : undefined;
                if (!node || !state) {
                  return (
                    <div className="hint">
                      Node not found.{" "}
                      <button
                        className="button small"
                        onClick={() => setSelectedNodeId(null)}
                      >
                        Back
                      </button>
                    </div>
                  );
                }
                return (
                  <div className="tile device-tile">
                    <div className="row compact">
                      <button
                        className="button small"
                        onClick={() => setSelectedNodeId(null)}
                      >
                        Back to nodes
                      </button>
                    </div>
                    <div className="device-title">{node.name ?? node.nodeId}</div>
                    <div className="hint">
                      {node.kind} · {node.status} · mode: {node.mode ?? "unknown"}
                    </div>
                    <div className="section compact">
                      <div className="row grid-two">
                        <div className="field">
                          <label className="label">Name</label>
                          <input
                            className="input compact"
                            value={state?.name ?? node.name ?? node.nodeId}
                            onChange={(event) =>
                              updateNodeState(node.nodeId, { name: event.target.value })
                            }
                            placeholder={node.nodeId}
                          />
                        </div>
                        <div className="field">
                          <label className="label">Name Action</label>
                          <div className="row compact">
                            <button
                              className="button small"
                              onClick={() => handleRename(node.nodeId)}
                              disabled={state?.isBusy}
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
                            value={state?.mode ?? node.mode ?? "real"}
                            onChange={(event) =>
                              updateNodeState(node.nodeId, {
                                mode: event.target.value as "real" | "debug",
                              })
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
                              onClick={() => handleSendMode(node.nodeId)}
                              disabled={state?.isBusy}
                            >
                              Send mode
                            </button>
                            <button
                              className="button small"
                              onClick={() => handleReadNow(node.nodeId)}
                              disabled={state?.isBusy}
                            >
                              Read now
                            </button>
                            <button
                              className="button small"
                              onClick={() => handleResetSim(node.nodeId)}
                              disabled={state?.isBusy}
                            >
                              Reset sim
                            </button>
                          </div>
                        </div>
                      </div>
                      <div className="row grid-two">
                        <div className="field">
                          <label className="label">Sim pH</label>
                          <input
                            className="input compact"
                            value={state?.simPh ?? ""}
                            onChange={(event) =>
                              updateNodeState(node.nodeId, {
                                simPh: event.target.value,
                              })
                            }
                            placeholder="6.2"
                          />
                        </div>
                        <div className="field">
                          <label className="label">Sim EC</label>
                          <input
                            className="input compact"
                            value={state?.simEc ?? ""}
                            onChange={(event) =>
                              updateNodeState(node.nodeId, {
                                simEc: event.target.value,
                              })
                            }
                            placeholder="1.7"
                          />
                        </div>
                      </div>
                      <div className="row grid-two">
                        <div className="field">
                          <label className="label">Sim Temp</label>
                          <input
                            className="input compact"
                            value={state?.simTemp ?? ""}
                            onChange={(event) =>
                              updateNodeState(node.nodeId, {
                                simTemp: event.target.value,
                              })
                            }
                            placeholder="21.3"
                          />
                        </div>
                        <div className="field">
                          <label className="label">Sim Action</label>
                          <div className="row compact">
                            <button
                              className="button small"
                              onClick={() => handleSendSim(node.nodeId)}
                              disabled={state?.isBusy}
                            >
                              Send sim
                            </button>
                          </div>
                        </div>
                      </div>
                      {state?.status && <div className="hint">{state.status}</div>}
                    </div>
                    <div className="device-actions">
                      <button
                        className="button small danger"
                        onClick={() => onDeleteNode(node.nodeId)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                );
              })()
            ) : (
              <div className="device-grid is-compact">
                {activeNodes.length === 0 && <div className="hint">No nodes found.</div>}
                {activeNodes.map((node) => (
                  <button
                    key={node.nodeId}
                    type="button"
                    className="tile device-tile is-compact"
                    onClick={() => setSelectedNodeId(node.nodeId)}
                  >
                    <div className="device-title">{node.name ?? node.nodeId}</div>
                    <div className="hint">
                      {node.status} · {node.mode ?? "unknown"}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
          {!selectedNodeId && (
            <div className="device-group">
              <div className="device-group-title">Cameras</div>
              <div className="device-grid">
                {cameraDevices.length === 0 && <div className="hint">No cameras found.</div>}
                {cameraDevices.map((camera) => (
                  <div key={camera.cameraId} className="tile device-tile">
                    <div className="device-title">{camera.friendlyName || camera.cameraId}</div>
                    <div className="hint">{camera.status ?? "offline"}</div>
                    <div className="device-actions">
                      <button
                        className="button small danger"
                        onClick={() => onDeleteCamera(camera.cameraId)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;

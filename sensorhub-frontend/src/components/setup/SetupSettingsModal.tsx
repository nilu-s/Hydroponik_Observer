import { FC, ReactNode } from "react";

import { CameraDevice, NodeInfo } from "../../types";

type Props = {
  isOpen: boolean;
  setupName: string;
  isSavingName: boolean;
  nodeId: string | null;
  cameraPort: string | null;
  nodes: NodeInfo[];
  cameraOptions: CameraDevice[];
  sharedNodeIds: Set<string>;
  sharedCameraIds: Set<string>;
  onClose: () => void;
  onNameChange: (value: string) => void;
  onSaveName: () => void;
  onNodeChange: (nodeId: string | null) => void;
  onCameraChange: (cameraPort: string | null) => void;
  onDeleteSetup: () => void;
  children: ReactNode;
};

const SetupSettingsModal: FC<Props> = ({
  isOpen,
  setupName,
  isSavingName,
  nodeId,
  cameraPort,
  nodes,
  cameraOptions,
  sharedNodeIds,
  sharedCameraIds,
  onClose,
  onNameChange,
  onSaveName,
  onNodeChange,
  onCameraChange,
  onDeleteSetup,
  children,
}) => {
  if (!isOpen) {
    return null;
  }

  const normalizeCameraId = (cameraIdValue: string) => {
    return cameraIdValue.replace(/^fallback:/i, "");
  };

  return (
    <div className="modal-overlay">
      <div className="wizard compact-modal">
        <div className="wizard-header">
          <div className="wizard-header-title">
            <div className="wizard-title">Setup settings</div>
            <div className="wizard-subtitle">Name and frequencies</div>
          </div>
          <button
            className="icon-button wizard-header-close"
            onClick={onClose}
            aria-label="Close settings"
          >
            ✕
          </button>
        </div>
        <div className="wizard-content setup-settings-content">
          <div className="setup-settings-compact">
            <div className="setup-row">
              <label className="label">Name</label>
              <input
                className="input compact"
                value={setupName}
                onChange={(event) => onNameChange(event.target.value)}
              />
              <button
                className="button small"
                onClick={onSaveName}
                disabled={isSavingName}
              >
                Save
              </button>
            </div>
            <div className="setup-row">
              <label className="label">Node</label>
              <select
                className={`select${sharedNodeIds.has(nodeId ?? "") ? " select-shared" : ""}`}
                value={nodeId ?? ""}
                onChange={(event) => onNodeChange(event.target.value || null)}
              >
                <option value="">None</option>
                {nodes
                  .map((node) => ({
                    ...node,
                    key: node.nodeId ?? node.port ?? "",
                  }))
                  .filter((node) => node.key)
                  .map((node) => (
                    <option
                      key={node.key}
                      value={node.key}
                      className={sharedNodeIds.has(node.key) ? "option-shared" : ""}
                    >
                      {node.key} · {(node.alias ?? node.port ?? node.nodeId ?? node.key)} ({node.kind})
                      {sharedNodeIds.has(node.key) ? " • shared" : ""}
                    </option>
                  ))}
              </select>
            </div>
            <div className="setup-row">
              <label className="label">Camera</label>
              <select
                className={`select${
                  sharedCameraIds.has(cameraPort ?? "") ? " select-shared" : ""
                }`}
                value={cameraPort ?? ""}
                onChange={(event) => onCameraChange(event.target.value || null)}
              >
                <option value="">Noone</option>
                {cameraOptions.map((camera) => (
                  <option
                    key={camera.cameraId}
                    value={camera.cameraId}
                    className={sharedCameraIds.has(camera.cameraId) ? "option-shared" : ""}
                  >
                    {(camera.alias ||
                      camera.friendlyName ||
                      normalizeCameraId(camera.cameraId)) +
                      (camera.status === "offline" ? " • offline" : "") +
                      (sharedCameraIds.has(camera.cameraId) ? " • shared" : "")}
                  </option>
                ))}
              </select>
            </div>
            <div className="setup-row setup-row-stack">
              <div className="section-title">Frequencies</div>
              {children}
            </div>
          </div>
        </div>
        <div className="setup-settings-actions">
          <button className="button" onClick={onClose}>
            Close
          </button>
          <button className="button danger" onClick={onDeleteSetup}>
            Delete setup
          </button>
        </div>
      </div>
    </div>
  );
};

export default SetupSettingsModal;

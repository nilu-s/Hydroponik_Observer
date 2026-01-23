import { FC, ReactNode } from "react";

import { CameraDevice, NodeInfo } from "../../types";

type Props = {
  isOpen: boolean;
  setupName: string;
  isSavingName: boolean;
  nodeId: string | null;
  cameraId: string | null;
  nodes: NodeInfo[];
  cameraOptions: CameraDevice[];
  sharedNodeIds: Set<string>;
  sharedCameraIds: Set<string>;
  onClose: () => void;
  onNameChange: (value: string) => void;
  onSaveName: () => void;
  onNodeChange: (nodeId: string | null) => void;
  onCameraChange: (cameraId: string | null) => void;
  onDeleteSetup: () => void;
  children: ReactNode;
};

const SetupSettingsModal: FC<Props> = ({
  isOpen,
  setupName,
  isSavingName,
  nodeId,
  cameraId,
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

  return (
    <div className="modal-overlay">
      <div className="wizard compact-modal">
        <div className="wizard-header">
          <div className="wizard-header-title">
            <div className="wizard-title">Setup settings</div>
            <div className="wizard-subtitle">Name and frequencies</div>
          </div>
          <div className="wizard-header-actions">
            <button className="button danger" onClick={onDeleteSetup}>
              Delete setup
            </button>
          </div>
          <button className="icon-button wizard-header-close" onClick={onClose} aria-label="Close settings">
            ✕
          </button>
        </div>
        <div className="wizard-content">
          <div className="section compact">
            <div className="section-title">Assignments</div>
            <div className="row grid-two">
              <div className="field">
                <label className="label">Node</label>
                <select
                  className={`select${sharedNodeIds.has(nodeId ?? "") ? " select-shared" : ""}`}
                  value={nodeId ?? ""}
                  onChange={(event) => onNodeChange(event.target.value || null)}
                >
                  <option value="">None</option>
                  {nodes.map((node) => (
                    <option
                      key={node.nodeId}
                      value={node.nodeId}
                      className={sharedNodeIds.has(node.nodeId) ? "option-shared" : ""}
                    >
                      {node.nodeId} ({node.kind})
                      {sharedNodeIds.has(node.nodeId) ? " • shared" : ""}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field">
                <label className="label">Camera</label>
                <select
                  className={`select${sharedCameraIds.has(cameraId ?? "") ? " select-shared" : ""}`}
                  value={cameraId ?? ""}
                  onChange={(event) => onCameraChange(event.target.value || null)}
                >
                  <option value="">None</option>
                  {cameraOptions.map((camera) => (
                    <option
                      key={camera.cameraId}
                      value={camera.cameraId}
                      className={sharedCameraIds.has(camera.cameraId) ? "option-shared" : ""}
                    >
                      {(camera.friendlyName || camera.cameraId) +
                        (camera.status === "offline" ? " • offline" : "") +
                        (sharedCameraIds.has(camera.cameraId) ? " • shared" : "")}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          <div className="section compact">
            <div className="section-title">Setup name</div>
            <div className="row compact">
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
                Save name
              </button>
            </div>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
};

export default SetupSettingsModal;

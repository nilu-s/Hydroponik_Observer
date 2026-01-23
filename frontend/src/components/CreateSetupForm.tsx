import { useMemo, useState } from "react";

import { CameraDevice, NodeInfo, Setup } from "../types";

type CreatePayload = {
  name: string;
  nodeId: string;
  cameraId: string;
  valueIntervalSec: number;
  photoIntervalSec: number;
};

type Props = {
  setups: Setup[];
  nodes: NodeInfo[];
  cameraDevices: CameraDevice[];
  onCreate: (payload: CreatePayload) => Promise<void>;
};

const CreateSetupForm = ({ setups, nodes, cameraDevices, onCreate }: Props) => {
  const [isOpen, setIsOpen] = useState(false);
  const [name, setName] = useState("");
  const [nodeId, setNodeId] = useState("");
  const [cameraId, setCameraId] = useState("");
  const [valueIntervalMinutes, setValueIntervalMinutes] = useState(30);
  const [photoIntervalMinutes, setPhotoIntervalMinutes] = useState(720);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const assignedNodes = useMemo(
    () => new Set(setups.map((setup) => setup.nodeId).filter(Boolean)),
    [setups]
  );
  const assignedCameras = useMemo(
    () => new Set(setups.map((setup) => setup.cameraId).filter(Boolean)),
    [setups]
  );

  const isNodeShared = !!nodeId && assignedNodes.has(nodeId);
  const isCameraShared = !!cameraId && assignedCameras.has(cameraId);

  const cameraOptions = cameraDevices;

  const shortDeviceId = (deviceId: string) => {
    if (!deviceId) {
      return "";
    }
    const compact = deviceId.replace(/^@device:pnp:/i, "");
    return compact.length > 32 ? `...${compact.slice(-32)}` : compact;
  };

  const shortPnpId = (pnpDeviceId?: string) => {
    if (!pnpDeviceId) {
      return "";
    }
    return pnpDeviceId.length > 32 ? `...${pnpDeviceId.slice(-32)}` : pnpDeviceId;
  };

  const resetWizard = () => {
    setName("");
    setNodeId("");
    setCameraId("");
    setValueIntervalMinutes(30);
    setPhotoIntervalMinutes(720);
  };

  const closeWizard = () => {
    setIsOpen(false);
    resetWizard();
  };

  const handleCreate = async () => {
    if (!name.trim() || !nodeId || !cameraId || isSubmitting) {
      return;
    }
    setIsSubmitting(true);
    try {
      await onCreate({
        name: name.trim(),
        nodeId,
        cameraId,
        valueIntervalSec: valueIntervalMinutes * 60,
        photoIntervalSec: photoIntervalMinutes * 60,
      });
      closeWizard();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <div className="create-form">
        <button className="button primary" onClick={() => setIsOpen(true)}>
          New setup
        </button>
      </div>

      {isOpen && (
        <div className="modal-overlay">
          <div className="wizard compact-modal">
            <div className="wizard-header">
              <div>
                <div className="wizard-title">New setup</div>
                <div className="wizard-subtitle">Assign node and camera</div>
              </div>
              <button className="icon-button" onClick={closeWizard}>
                ✕
              </button>
            </div>

            <div className="wizard-content">
              <div className="wizard-panel">
                <label className="label">Setup name</label>
                <input
                  className="input"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  placeholder="e.g. Greenhouse A"
                />
              </div>
              <div className="wizard-panel">
                <label className="label">Node</label>
                <select
                  className="select"
                  value={nodeId}
                  onChange={(event) => setNodeId(event.target.value)}
                >
                  <option value="">Select node</option>
                  {nodes.map((node) => (
                    <option key={node.nodeId} value={node.nodeId}>
                      {node.name ?? node.nodeId}
                      {assignedNodes.has(node.nodeId) ? " • shared" : ""}
                    </option>
                  ))}
                </select>
                {isNodeShared && (
                  <div className="hint">Warning: This node is already assigned.</div>
                )}
              </div>
              <div className="wizard-panel">
                <label className="label">Camera</label>
                <select
                  className="select"
                  value={cameraId}
                  onChange={(event) => setCameraId(event.target.value)}
                >
                  <option value="">Select camera</option>
                  {cameraOptions.map((camera) => (
                    <option key={camera.cameraId} value={camera.cameraId}>
                      {(camera.friendlyName || camera.cameraId) +
                        (camera.deviceId
                          ? ` · ${shortDeviceId(camera.deviceId)}`
                          : camera.pnpDeviceId
                          ? ` · ${shortPnpId(camera.pnpDeviceId)}`
                          : "") +
                        (camera.status === "offline" ? " • offline" : "") +
                        (assignedCameras.has(camera.cameraId) ? " • shared" : "")}
                    </option>
                  ))}
                </select>
                {isCameraShared && (
                  <div className="hint">Warning: This camera is already assigned.</div>
                )}
              </div>
              <div className="wizard-panel">
                <div className="row grid-two">
                  <div className="field">
                    <label className="label">Value interval</label>
                    <input
                      className="input"
                      type="number"
                      min={1}
                      max={1440}
                      step={1}
                      value={valueIntervalMinutes}
                      onChange={(event) =>
                        setValueIntervalMinutes(Number(event.target.value))
                      }
                    />
                    <div className="hint">Minutes</div>
                  </div>
                  <div className="field">
                    <label className="label">Photo interval</label>
                    <input
                      className="input"
                      type="number"
                      min={1}
                      max={1440}
                      step={1}
                      value={photoIntervalMinutes}
                      onChange={(event) =>
                        setPhotoIntervalMinutes(Number(event.target.value))
                      }
                    />
                    <div className="hint">Minutes</div>
                  </div>
                </div>
                <div className="hint">Range: 1 min – 24 h.</div>
              </div>
            </div>

            <div className="wizard-actions">
              <button className="button" onClick={closeWizard}>
                Cancel
              </button>
              <button
                className="button primary"
                onClick={handleCreate}
                disabled={isSubmitting || !name.trim() || !nodeId || !cameraId}
              >
                Create setup
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default CreateSetupForm;

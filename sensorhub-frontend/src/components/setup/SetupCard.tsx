import { useEffect, useMemo, useState } from "react";

import { CameraDevice, NodeInfo, Reading, Setup } from "../../types";
import CameraPreview from "../camera/CameraPreview";
import SettingsButton from "../common/SettingsButton";
import Timeline from "../timeline/Timeline";
import FrequencyControls from "./FrequencyControls";
import SetupSettingsModal from "./SetupSettingsModal";

type Props = {
  setup: Setup;
  setups: Setup[];
  nodes: NodeInfo[];
  cameraDevices: CameraDevice[];
  reading: Reading | null;
  isExpanded: boolean;
  onToggle: () => void;
  onDelete: () => Promise<void>;
  onPatch: (patch: Partial<Setup>) => Promise<void>;
  onCaptureReading: () => Promise<void>;
  onCapturePhoto: () => Promise<void>;
};

const SetupCard = ({
  setup,
  setups,
  nodes,
  cameraDevices,
  reading,
  isExpanded,
  onToggle,
  onDelete,
  onPatch,
  onCaptureReading,
  onCapturePhoto,
}: Props) => {
  const [name, setName] = useState(setup.name);
  const [isSavingName, setIsSavingName] = useState(false);
  const [isCapturingReading, setIsCapturingReading] = useState(false);
  const [isCapturingPhoto, setIsCapturingPhoto] = useState(false);
  const [photoError, setPhotoError] = useState("");
  const [timelineKey, setTimelineKey] = useState(0);
  const [showSettings, setShowSettings] = useState(false);
  useEffect(() => {
    setName(setup.name);
  }, [setup.name]);

  const setupNodeId = setup.nodeId ?? null;
  const nodeLabel = useMemo(() => {
    if (!setupNodeId) {
      return "None";
    }
    const node = nodes.find((item) => item.nodeId === setupNodeId);
    if (!node) {
      return setupNodeId;
    }
    const label = node.alias ?? node.nodeId ?? setupNodeId;
    return label;
  }, [nodes, setupNodeId]);
  const nodeMode = useMemo(() => {
    if (!setupNodeId) {
      return "unknown";
    }
    const node = nodes.find((item) => item.nodeId === setupNodeId);
    return node?.mode ?? "unknown";
  }, [nodes, setupNodeId]);
  const nodeStatus = useMemo(() => {
    if (!setupNodeId) {
      return null;
    }
    const node = nodes.find((item) => item.nodeId === setupNodeId);
    return node?.status ?? "unknown";
  }, [nodes, setupNodeId]);

  const handleNameSave = async () => {
    if (!name.trim() || name.trim() === setup.name) {
      return;
    }
    setIsSavingName(true);
    try {
      await onPatch({ name: name.trim() });
    } finally {
      setIsSavingName(false);
    }
  };

  const handleNodeChange = async (value: string | null) => {
    await onPatch({ nodeId: value });
  };

  const handleCameraChange = async (value: string | null) => {
    await onPatch({ cameraPort: value });
  };

  const handleCaptureReading = async () => {
    if (!setupNodeId) {
      return;
    }
    setIsCapturingReading(true);
    try {
      await onCaptureReading();
      setTimelineKey((prev) => prev + 1);
    } finally {
      setIsCapturingReading(false);
    }
  };

  const handleCapturePhoto = async () => {
    if (!setup.cameraPort) {
      return;
    }
    setIsCapturingPhoto(true);
    setPhotoError("");
    try {
      await onCapturePhoto();
      setTimelineKey((prev) => prev + 1);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Capture failed";
      setPhotoError(message);
    } finally {
      setIsCapturingPhoto(false);
    }
  };

  const isNodeShared =
    !!setupNodeId &&
    setups.some((item) => item.setupId !== setup.setupId && item.nodeId === setupNodeId);
  const isCameraShared =
    !!setup.cameraPort &&
    setups.some(
      (item) => item.setupId !== setup.setupId && item.cameraPort === setup.cameraPort
    );
  const sharedNodeIds = useMemo(() => {
    const map = new Map<string, number>();
    setups.forEach((item) => {
      if (item.nodeId) {
        map.set(item.nodeId, (map.get(item.nodeId) ?? 0) + 1);
      }
    });
    return new Set(
      Array.from(map.entries())
        .filter(([, count]) => count > 1)
        .map(([id]) => id)
    );
  }, [setups]);

  const sharedCameraIds = useMemo(() => {
    const map = new Map<string, number>();
    setups.forEach((item) => {
      if (item.cameraPort) {
        map.set(item.cameraPort, (map.get(item.cameraPort) ?? 0) + 1);
      }
    });
    return new Set(
      Array.from(map.entries())
        .filter(([, count]) => count > 1)
        .map(([id]) => id)
    );
  }, [setups]);
  const isCameraKnown =
    !!setup.cameraPort &&
    cameraDevices.some((camera) => camera.cameraId === setup.cameraPort);
  const cameraOptions =
    setup.cameraPort && !isCameraKnown
      ? [
          {
            cameraId: setup.cameraPort,
            deviceId: "",
            friendlyName: `Unbekannt (${setup.cameraPort})`,
            status: "offline" as const,
          },
          ...cameraDevices,
        ]
      : cameraDevices;

  const cameraLabel = useMemo(() => {
    if (!setup.cameraPort) {
      return "None";
    }
    const device = cameraOptions.find((camera) => camera.cameraId === setup.cameraPort);
    if (!device) {
      return setup.cameraPort;
    }
    return device.alias || device.friendlyName || device.cameraId;
  }, [cameraOptions, setup.cameraPort]);
  const cameraStatus = useMemo(() => {
    if (!setup.cameraPort) {
      return null;
    }
    const device = cameraDevices.find((camera) => camera.cameraId === setup.cameraPort);
    return device?.status ?? "unknown";
  }, [cameraDevices, setup.cameraPort]);
  const isNodeDisconnected = !!setupNodeId && nodeStatus !== "online";
  const isCameraDisconnected = !!setup.cameraPort && cameraStatus !== "online";

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <button
            className="icon-button"
            onClick={onToggle}
            aria-label={isExpanded ? "Collapse setup" : "Expand setup"}
            title={isExpanded ? "Collapse" : "Expand"}
          >
            {isExpanded ? "▾" : "▸"}
          </button>
          {setup.name}
        </div>
        <div className="card-live">
          <div className="card-live-item">pH {reading?.ph ?? "--"}</div>
          <div className="card-live-item">EC {reading?.ec ?? "--"} mS/cm</div>
          <div className="card-live-item">Temp {reading?.temp ?? "--"} °C</div>
        </div>
        <div className="card-camera-preview">
          <CameraPreview
            setupId={setup.setupId}
            cameraPort={setup.cameraPort}
            cameraStatus={
              setup.cameraPort
                ? cameraDevices.find((camera) => camera.cameraId === setup.cameraPort)?.status
                : undefined
            }
            compact
          />
        </div>
        <div className="card-actions">
          <button
            className="icon-button icon-button-lg icon-button-labeled"
            onClick={handleCaptureReading}
            aria-label="Capture values"
            title="Capture values"
            disabled={!setupNodeId || isCapturingReading}
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M5 3h11l3 3v14a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zm2 2v6h10V6.5L14.5 5H7zm0 9v5h10v-5H7zm2 1h6v3H9v-3z" />
            </svg>
            <span>Werte speichern</span>
          </button>
          <button
            className="icon-button icon-button-lg icon-button-labeled"
            onClick={handleCapturePhoto}
            aria-label="Capture photo"
            title="Capture photo"
            disabled={!setup.cameraPort || isCapturingPhoto}
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M9 4h6l1.5 2H20a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h3.5L9 4zm3 4a5 5 0 1 0 0 10 5 5 0 0 0 0-10zm0 2.2a2.8 2.8 0 1 1 0 5.6 2.8 2.8 0 0 1 0-5.6z" />
            </svg>
            <span>Foto aufnehmen</span>
          </button>
        </div>
        <div className="card-header-right">
          <div className="card-meta">
            <div
              className={`header-chip node${isNodeShared ? " is-shared" : ""}${
                isNodeDisconnected ? " is-offline" : ""
              }${nodeMode === "debug" ? " is-debug" : ""}`}
            >
              <span className="header-value">{nodeLabel}</span>
            </div>
            <div
              className={`header-chip camera${isCameraShared ? " is-shared" : ""}${
                isCameraDisconnected ? " is-offline" : ""
              }`}
            >
              <span className="header-value">{cameraLabel}</span>
            </div>
          </div>
          <div className="card-settings">
            <SettingsButton
              onClick={() => setShowSettings(true)}
              isActive={showSettings}
            />
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="card-body expanded-layout">
          <div className="timeline-full">
            <Timeline key={`${setup.setupId}-${timelineKey}`} setup={setup} />
          </div>
          <div className="expanded-right expanded-full">
            {photoError && <div className="hint">{photoError}</div>}
          </div>
        </div>
      )}

      <SetupSettingsModal
        isOpen={showSettings}
        setupName={name}
        isSavingName={isSavingName}
        nodeId={setupNodeId}
        cameraPort={setup.cameraPort}
        nodes={nodes}
        cameraOptions={cameraOptions}
        sharedNodeIds={sharedNodeIds}
        sharedCameraIds={sharedCameraIds}
        onClose={() => setShowSettings(false)}
        onNameChange={setName}
        onSaveName={handleNameSave}
        onNodeChange={handleNodeChange}
        onCameraChange={handleCameraChange}
        onDeleteSetup={onDelete}
      >
        <FrequencyControls setup={setup} onPatch={onPatch} />
      </SetupSettingsModal>
    </div>
  );
};

export default SetupCard;

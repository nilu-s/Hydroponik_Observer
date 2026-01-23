import { useEffect, useMemo, useRef, useState } from "react";

import {
  capturePhoto,
  captureReading,
  createSetup,
  deleteCamera,
  deleteNode,
  deleteSetup,
  exportAllData,
  getCameraDevices,
  getNodes,
  getReading,
  getSetups,
  patchSetup,
  requestNodeReading,
  setNodeMode,
  setNodeSim,
} from "./api";
import { CameraDevice, NodeInfo, Reading, Setup, WsServerMsg } from "./types";
import { LiveWsClient } from "./ws";
import CreateSetupForm from "./components/CreateSetupForm";
import SetupCard from "./components/SetupCard";
import SettingsButton from "./components/settings-button";
import SettingsModal from "./components/settings-modal";

const App = () => {
  const [setups, setSetups] = useState<Setup[]>([]);
  const [nodes, setNodes] = useState<NodeInfo[]>([]);
  const [cameraDevices, setCameraDevices] = useState<CameraDevice[]>([]);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [showSettings, setShowSettings] = useState(false);
  const [liveReadings, setLiveReadings] = useState<Record<string, Reading | null>>(
    {}
  );
  const [wsStatus, setWsStatus] = useState<
    "connected" | "disconnected" | "connecting"
  >("connecting");
  const [pendingDelete, setPendingDelete] = useState<Setup | null>(null);

  const wsRef = useRef<LiveWsClient | null>(null);
  const subscribedIdsRef = useRef<Set<string>>(new Set());

  const handleWsMsg = (msg: WsServerMsg) => {
    if (msg.t === "reading") {
      setLiveReadings((prev) => ({ ...prev, [msg.setupId]: msg }));
      return;
    }
    if (msg.t === "cameraDevices") {
      setCameraDevices(msg.devices);
    }
  };

  const loadBaseData = async () => {
    const [setupsData, nodesData, cameraDeviceData] = await Promise.all([
      getSetups(),
      getNodes(),
      getCameraDevices(),
    ]);
    setSetups(setupsData);
    setNodes(nodesData);
    setCameraDevices(cameraDeviceData);
  };

  useEffect(() => {
    loadBaseData();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      getNodes().then(setNodes).catch(() => null);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const client = new LiveWsClient(handleWsMsg, setWsStatus);
    wsRef.current = client;
    client.connect();
    return () => client.close();
  }, []);

  useEffect(() => {
    const nextIds = new Set(setups.map((setup) => setup.setupId));
    const prevIds = subscribedIdsRef.current;
    const client = wsRef.current;
    if (client) {
      nextIds.forEach((setupId) => {
        if (!prevIds.has(setupId)) {
          client.subscribe(setupId);
        }
      });
      prevIds.forEach((setupId) => {
        if (!nextIds.has(setupId)) {
          client.unsubscribe(setupId);
        }
      });
    }
    subscribedIdsRef.current = nextIds;
  }, [setups]);

  useEffect(() => {
    if (!setups.length) {
      return;
    }
    const loadReadings = async () => {
      const results = await Promise.all(
        setups.map(async (setup) => {
          try {
            const reading = await getReading(setup.setupId);
            return { setupId: setup.setupId, reading };
          } catch {
            return null;
          }
        })
      );
      setLiveReadings((prev) => {
        const next = { ...prev };
        results.forEach((result) => {
          if (result) {
            next[result.setupId] = result.reading ?? null;
          }
        });
        return next;
      });
    };
    loadReadings();
  }, [setups]);

  const handleCreate = async (payload: {
    name: string;
    nodeId: string;
    cameraId: string;
    valueIntervalSec: number;
    photoIntervalSec: number;
  }) => {
    const created = await createSetup(payload.name);
    const patched = await patchSetup(created.setupId, {
      nodeId: payload.nodeId,
      cameraId: payload.cameraId,
      valueIntervalSec: payload.valueIntervalSec,
      photoIntervalSec: payload.photoIntervalSec,
    });
    setSetups((prev) => [...prev, patched]);
  };

  const handleDelete = async (setupId: string) => {
    const setup = setups.find((item) => item.setupId === setupId) || null;
    setPendingDelete(setup);
  };

  const handleDeleteNode = async (nodeId: string) => {
    if (!window.confirm(`Delete node ${nodeId}? This also deletes its photos.`)) {
      return;
    }
    try {
      await deleteNode(nodeId);
      setSetups((prev) =>
        prev.map((setup) =>
          setup.nodeId === nodeId ? { ...setup, nodeId: null } : setup
        )
      );
      await loadBaseData();
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
      setSetups((prev) =>
        prev.map((setup) =>
          setup.cameraId === cameraId ? { ...setup, cameraId: null } : setup
        )
      );
      await loadBaseData();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Delete failed";
      alert(message);
    }
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

  const handleSetNodeMode = async (nodeId: string, mode: "real" | "debug") => {
    try {
      await setNodeMode(nodeId, mode);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Command failed";
      alert(message);
    }
  };

  const handleSetNodeSim = async (
    nodeId: string,
    payload: { ph?: number; ec?: number; temp?: number }
  ) => {
    try {
      await setNodeSim(nodeId, payload);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Command failed";
      alert(message);
    }
  };

  const handleRequestNodeReading = async (nodeId: string) => {
    try {
      return await requestNodeReading(nodeId);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Command failed";
      alert(message);
      return {};
    }
  };

  const handleResetNodeSim = async (nodeId: string) => {
    await setNodeMode(nodeId, "real");
    await setNodeMode(nodeId, "debug");
  };

  const confirmDelete = async () => {
    if (!pendingDelete) {
      return;
    }
    const setupId = pendingDelete.setupId;
    try {
      await deleteSetup(setupId);
      setSetups((prev) => prev.filter((setup) => setup.setupId !== setupId));
      setExpanded((prev) => {
        const next = new Set(prev);
        next.delete(setupId);
        return next;
      });
      wsRef.current?.unsubscribe(setupId);
      setPendingDelete(null);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Delete failed";
      alert(message);
    }
  };

  const cancelDelete = () => {
    setPendingDelete(null);
  };

  const handlePatch = async (setupId: string, patch: Partial<Setup>) => {
    const updated = await patchSetup(setupId, patch);
    setSetups((prev) =>
      prev.map((setup) => (setup.setupId === setupId ? updated : setup))
    );
  };

  const handleCaptureReading = async (setupId: string) => {
    const reading = await captureReading(setupId);
    setLiveReadings((prev) => ({ ...prev, [setupId]: reading }));
  };

  const handleCapturePhoto = async (setupId: string) => {
    await capturePhoto(setupId);
  };

  const toggleExpanded = (setupId: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(setupId)) {
        next.delete(setupId);
      } else {
        next.add(setupId);
      }
      return next;
    });
  };

  const expandedIds = useMemo(() => new Set(expanded), [expanded]);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Sensorhub</h1>
          <p className="subtitle">Setups, live values, and camera preview</p>
        </div>
        <div className="header-actions">
          <div className="status">
            WebSocket:
            <span
              className={`badge ${
                wsStatus === "connected" ? "badge-ok" : "badge-warn"
              }`}
            >
              {wsStatus}
            </span>
          </div>
          <SettingsButton
            onClick={() => setShowSettings((prev) => !prev)}
            isActive={showSettings}
          />
        </div>
      </header>

      <CreateSetupForm
        setups={setups}
        nodes={nodes}
        cameraDevices={cameraDevices}
        onCreate={handleCreate}
      />

      <SettingsModal
        isOpen={showSettings}
        nodes={nodes}
        cameraDevices={cameraDevices}
        onClose={() => setShowSettings(false)}
        onDeleteNode={handleDeleteNode}
        onDeleteCamera={handleDeleteCamera}
        onExportAll={handleExportAll}
        onSetNodeMode={handleSetNodeMode}
        onSetNodeSim={handleSetNodeSim}
        onRequestNodeReading={handleRequestNodeReading}
        onResetNodeSim={handleResetNodeSim}
      />

      <div className="cards">
        {setups.length === 0 && (
          <div className="empty">No setups yet. Create one above.</div>
        )}
        {setups.map((setup) => (
          <SetupCard
            key={setup.setupId}
            setup={setup}
            setups={setups}
            nodes={nodes}
            cameraDevices={cameraDevices}
            reading={liveReadings[setup.setupId] ?? null}
            isExpanded={expandedIds.has(setup.setupId)}
            onToggle={() => toggleExpanded(setup.setupId)}
            onDelete={() => handleDelete(setup.setupId)}
            onPatch={(patch) => handlePatch(setup.setupId, patch)}
            onCaptureReading={() => handleCaptureReading(setup.setupId)}
            onCapturePhoto={() => handleCapturePhoto(setup.setupId)}
          />
        ))}
      </div>

      {pendingDelete && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-top-action">
              <button className="button danger" onClick={confirmDelete}>
                Delete setup
              </button>
            </div>
            <div className="modal-title">Delete setup</div>
            <div className="modal-body">
              Delete <strong>{pendingDelete.name}</strong>? This cannot be undone.
            </div>
            <div className="modal-actions">
              <button className="button" onClick={cancelDelete}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;

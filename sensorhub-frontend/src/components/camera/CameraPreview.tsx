import { useEffect, useMemo, useRef, useState } from "react";

import { getBackendBaseUrl } from "../../services/backend-url";

type Props = {
  setupId: string;
  cameraPort: string | null;
  cameraStatus?: "online" | "offline";
  compact?: boolean;
};

const CameraPreview = ({
  setupId,
  cameraPort,
  cameraStatus,
  compact = false,
}: Props) => {
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isRetrying, setIsRetrying] = useState(false);
  const [retryToken, setRetryToken] = useState(0);
  const retryTimer = useRef<number | null>(null);
  const retryCountRef = useRef(0);

  useEffect(() => {
    setHasError(false);
    setIsLoading(true);
    setIsRetrying(false);
    setRetryToken(0);
    retryCountRef.current = 0;
    if (retryTimer.current) {
      window.clearTimeout(retryTimer.current);
      retryTimer.current = null;
    }
  }, [setupId, cameraPort]);

  useEffect(() => {
    if (!cameraPort) {
      return;
    }
    if (cameraStatus === "offline") {
      if (retryTimer.current) {
        window.clearTimeout(retryTimer.current);
        retryTimer.current = null;
      }
      setHasError(true);
      setIsLoading(true);
      setIsRetrying(false);
      return;
    }
    setHasError(false);
    setIsRetrying(false);
    setIsLoading(true);
    setRetryToken((prev) => prev + 1);
  }, [cameraPort, cameraStatus]);

  if (!cameraPort) {
    return (
      <div className="section">
        <div className="section-title">Live camera</div>
        <div className="hint">No camera assigned.</div>
      </div>
    );
  }

  const streamSrc = useMemo(() => {
    const nonce = Date.now() + retryToken;
    const cameraParam = cameraPort ? `&camera=${encodeURIComponent(cameraPort)}` : "";
    return `${getBackendBaseUrl()}/api/setups/${setupId}/camera/stream?ts=${nonce}${cameraParam}`;
  }, [setupId, retryToken, cameraPort]);

  const handleLoad = () => {
    setHasError(false);
    setIsLoading(false);
    setIsRetrying(false);
    retryCountRef.current = 0;
  };

  const handleError = () => {
    if (cameraStatus === "offline") {
      setHasError(true);
      setIsLoading(true);
      setIsRetrying(false);
      return;
    }
    setHasError(true);
    setIsLoading(true);
    setIsRetrying(true);
    if (retryTimer.current) {
      return;
    }
    const attempt = retryCountRef.current;
    const delay = Math.min(1000 * Math.pow(2, attempt), 8000);
    retryTimer.current = window.setTimeout(() => {
      retryTimer.current = null;
      retryCountRef.current = Math.min(retryCountRef.current + 1, 6);
      setRetryToken((prev) => prev + 1);
    }, delay);
  };

  const isOffline = cameraStatus === "offline";
  const showLoader = hasError || isLoading || isOffline;
  const shouldHideImage = hasError || isOffline;
  const imageSrc = streamSrc;

  return (
    <div className={`section${compact ? " camera-preview-compact" : ""}`}>
      {!compact && <div className="section-title">Live camera</div>}
      <div className="camera-preview">
        {showLoader && (
          <div className="camera-loader">
            <div className="spinner" />
            <div className="hint">
              {cameraStatus === "offline"
                ? "Camera offline."
                : isRetrying
                ? "Reconnecting to camera..."
                : "Loading camera..."}
            </div>
          </div>
        )}
        <img
          key={`${setupId}-${cameraPort}-${retryToken}`}
          className={`camera-img${shouldHideImage ? " is-hidden" : ""}`}
          src={imageSrc}
          alt="Live camera stream"
          onLoad={handleLoad}
          onError={handleError}
        />
      </div>
    </div>
  );
};

export default CameraPreview;

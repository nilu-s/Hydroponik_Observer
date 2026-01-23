import { Reading } from "../types";

type Props = {
  reading: Reading | null;
  valueIntervalSec: number;
  nodeId: string | null;
};

const LiveValues = ({ reading, valueIntervalSec, nodeId }: Props) => {
  const now = Date.now();
  const maxAgeMs = valueIntervalSec * 3 * 1000;
  const isStale =
    !reading || !reading.ts || now - reading.ts > maxAgeMs || !nodeId;
  const statusLabel = isStale ? "offline" : "ok";

  const display = (value?: number, unit?: string) =>
    value === undefined ? "--" : `${value}${unit ?? ""}`;
  const timestamp = reading?.ts
    ? new Date(reading.ts).toLocaleTimeString()
    : "--";

  return (
    <div className="section">
      <div className="section-title">Live values</div>
      <div className={`badge ${isStale ? "badge-warn" : "badge-ok"}`}>
        {statusLabel}
      </div>
      <div className="tiles">
        <div className="tile">
          <div className="tile-label">pH (pH)</div>
          <div className="tile-value">{display(reading?.ph, " pH")}</div>
        </div>
        <div className="tile">
          <div className="tile-label">EC (mS/cm)</div>
          <div className="tile-value">{display(reading?.ec, " mS/cm")}</div>
        </div>
        <div className="tile">
          <div className="tile-label">Temp (°C)</div>
          <div className="tile-value">{display(reading?.temp, " °C")}</div>
        </div>
      </div>
      <div className="hint">Last update: {timestamp}</div>
    </div>
  );
};

export default LiveValues;

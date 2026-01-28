import { useEffect, useMemo, useRef, useState } from "react";

import { getHistory } from "../../services/api";
import { getBackendBaseUrl } from "../../services/backend-url";
import { Setup, StoredPhoto, StoredReading } from "../../types";

type TimelineEvent =
  | { type: "reading"; ts: number; reading: StoredReading }
  | { type: "photo"; ts: number; photo: StoredPhoto };

type HistoryResponse = {
  readings: StoredReading[];
  photos: StoredPhoto[];
};

type Props = {
  setup: Setup;
};

const Timeline = ({ setup }: Props) => {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [selected, setSelected] = useState<TimelineEvent | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [sliderTs, setSliderTs] = useState<number | null>(null);
  const [pair, setPair] = useState<{ readingTs: number | null; photoTs: number | null }>({
    readingTs: null,
    photoTs: null,
  });
  const playRef = useRef<number | null>(null);

  useEffect(() => {
    let mounted = true;
    const load = () => {
      getHistory(setup.setupId, 200)
        .then((data) => {
          const payload = data as HistoryResponse;
          if (!mounted) return;
          const readings = payload.readings.map((reading) => ({
            type: "reading" as const,
            ts: reading.ts,
            reading,
          }));
          const photos = payload.photos.map((photo) => ({
            type: "photo" as const,
            ts: photo.ts,
            photo,
          }));
          const merged = [...readings, ...photos].sort((a, b) => a.ts - b.ts);
          setEvents(merged);
          const latest = merged[merged.length - 1] ?? null;
          setSelected((current) => {
            if (!current) return latest;
            const stillExists = merged.find(
              (event) => event.ts === current.ts && event.type === current.type
            );
            return stillExists ?? latest;
          });
          setSliderTs((current) => current ?? latest?.ts ?? null);
          setPair({
            readingTs: readings[readings.length - 1]?.ts ?? null,
            photoTs: photos[photos.length - 1]?.ts ?? null,
          });
        })
        .catch(() => null);
    };
    load();
    const interval = window.setInterval(load, 10000);
    return () => {
      mounted = false;
      window.clearInterval(interval);
    };
  }, [setup.setupId]);

  useEffect(() => {
    if (!isPlaying) {
      if (playRef.current) {
        window.clearInterval(playRef.current);
        playRef.current = null;
      }
      return;
    }
    playRef.current = window.setInterval(() => {
      setSelected((current) => {
        if (!events.length) return current;
        const index = current
          ? events.findIndex((event) => event.ts === current.ts && event.type === current.type)
          : -1;
        const next = events[index + 1] ?? events[0];
        return next;
      });
    }, 1200);
    return () => {
      if (playRef.current) {
        window.clearInterval(playRef.current);
        playRef.current = null;
      }
    };
  }, [isPlaying, events]);

  useEffect(() => {
    if (selected?.ts) {
      setSliderTs(selected.ts);
    }
  }, [selected?.ts]);

  const readings = useMemo(
    () =>
      events.filter((event) => event.type === "reading") as {
        type: "reading";
        ts: number;
        reading: StoredReading;
      }[],
    [events]
  );
  const photos = useMemo(
    () =>
      events.filter((event) => event.type === "photo") as {
        type: "photo";
        ts: number;
        photo: StoredPhoto;
      }[],
    [events]
  );

  const findLatestReadingBefore = (ts: number) => {
    if (!readings.length) return null;
    return readings.reduce((latest, current) => {
      if (current.ts > ts) return latest;
      if (!latest) return current;
      return current.ts > latest.ts ? current : latest;
    }, null as null | (typeof readings)[number]);
  };

  const findLatestPhotoBefore = (ts: number) => {
    if (!photos.length) return null;
    return photos.reduce((latest, current) => {
      if (current.ts > ts) return latest;
      if (!latest) return current;
      return current.ts > latest.ts ? current : latest;
    }, null as null | (typeof photos)[number]);
  };

  const selectedReading = useMemo(() => {
    return pair.readingTs ? readings.find((event) => event.ts === pair.readingTs)?.reading ?? null : null;
  }, [pair.readingTs, readings]);

  const readingChart = useMemo(() => {
    if (readings.length < 2) {
      return null;
    }
    const minTs = readings[0]?.ts ?? 0;
    const maxTs = readings[readings.length - 1]?.ts ?? minTs;
    const rangeTs = Math.max(1, maxTs - minTs);
    const byKey = (key: "ec" | "ph" | "temp") =>
      readings.map((event) => ({
        ts: event.ts,
        value: typeof event.reading[key] === "number" ? event.reading[key] : null,
      }));
    const seriesStats = (items: { ts: number; value: number | null }[]) => {
      const values = items.map((item) => item.value).filter((value): value is number => value !== null);
      return {
        min: values.length ? Math.min(...values) : 0,
        max: values.length ? Math.max(...values) : 0,
        values,
        hasValues: values.length > 0,
      };
    };
    const CHART_LEFT = 2;
    const CHART_RIGHT = 2;
    const CHART_WIDTH = 100 - CHART_LEFT - CHART_RIGHT;
    const toDots = (
      items: { ts: number; value: number | null }[],
      minVal: number,
      maxVal: number
    ) => {
      const bandHeight = 22;
      const bandTop = 0;
      const rangeVal = maxVal - minVal;
      const padding = rangeVal === 0 ? 1 : rangeVal * 0.05;
      const scaleMin = minVal - padding;
      const scaleMax = maxVal + padding;
      const scaleRange = scaleMax - scaleMin;
      const minY = bandTop + 0.8;
      const maxY = bandTop + bandHeight - 0.8;
      return items
        .map((item) => {
          if (item.value === null) {
            return null;
          }
          const x = CHART_LEFT + ((item.ts - minTs) / rangeTs) * CHART_WIDTH;
          const y =
            scaleRange === 0
              ? bandTop + bandHeight / 2
              : bandTop + (1 - (item.value - scaleMin) / scaleRange) * bandHeight;
          return { x, y: Math.max(minY, Math.min(maxY, y)) };
        })
        .filter(Boolean) as { x: number; y: number }[];
    };
    const ecSeries = byKey("ec");
    const phSeries = byKey("ph");
    const tempSeries = byKey("temp");
    const ecStats = seriesStats(ecSeries);
    const phStats = seriesStats(phSeries);
    const tempStats = seriesStats(tempSeries);
    const ecDots = toDots(ecSeries, ecStats.min, ecStats.max);
    const phDots = toDots(phSeries, phStats.min, phStats.max);
    const tempDots = toDots(tempSeries, tempStats.min, tempStats.max);
    const markerTs = sliderTs ?? maxTs;
    const markerX = CHART_LEFT + ((markerTs - minTs) / rangeTs) * CHART_WIDTH;
    const markerReading = pair.readingTs
      ? readings.find((event) => event.ts === pair.readingTs) ?? null
      : null;
    return {
      ecDots,
      phDots,
      tempDots,
      markerX: Math.max(CHART_LEFT, Math.min(CHART_LEFT + CHART_WIDTH, markerX)),
      markerReading,
      ecStats,
      phStats,
      tempStats,
      minTs,
      maxTs,
    };
  }, [readings, sliderTs, pair.readingTs]);

  const selectedPhoto = useMemo(() => {
    return pair.photoTs ? photos.find((event) => event.ts === pair.photoTs)?.photo ?? null : null;
  }, [pair.photoTs, photos]);

  const minTs = events[0]?.ts;
  const maxTs = events[events.length - 1]?.ts;
  const formatDate = (ts?: number) => (ts ? new Date(ts).toLocaleString() : "--");

  const photoUrl = (path?: string) => {
    if (!path) return "";
    const normalized = path.replace(/\\/g, "/");
    const marker = "/data/";
    const idx = normalized.toLowerCase().indexOf(marker);
    const relative = idx >= 0 ? normalized.slice(idx) : normalized;
    return `${getBackendBaseUrl()}${relative}`;
  };

  useEffect(() => {
    if (!sliderTs) {
      return;
    }
    const latestReading = findLatestReadingBefore(sliderTs);
    const latestPhoto = findLatestPhotoBefore(sliderTs);
    setPair({
      readingTs: latestReading?.ts ?? null,
      photoTs: latestPhoto?.ts ?? null,
    });
  }, [sliderTs, readings, photos]);

  const handleSelect = (event: { ts: number; reading?: StoredReading; photo?: StoredPhoto }) => {
    setIsPlaying(false);
    if (event.reading) {
      setSelected({ type: "reading", ts: event.ts, reading: event.reading });
      setSliderTs(event.ts);
      return;
    }
    if (event.photo) {
      setSelected({ type: "photo", ts: event.ts, photo: event.photo });
      setSliderTs(event.ts);
    }
  };

  const findClosestEvent = (ts: number) => {
    if (!events.length) return null;
    return events.reduce((closest, current) => {
      if (!closest) return current;
      return Math.abs(current.ts - ts) < Math.abs(closest.ts - ts) ? current : closest;
    }, null as null | TimelineEvent);
  };

  const range = maxTs && minTs && maxTs > minTs ? maxTs - minTs : 1;
  const toPercent = (ts: number) => {
    const raw = ((ts - (minTs ?? ts)) / range) * 100;
    return 2 + raw * 0.96;
  };
  const sliderLabelStyle = useMemo(() => {
    const percent = toPercent(sliderTs ?? minTs ?? 0);
    if (percent <= 6) {
      return { left: "6%", transform: "translateX(0)" };
    }
    if (percent >= 94) {
      return { left: "94%", transform: "translateX(-100%)" };
    }
    return { left: `${percent}%`, transform: "translateX(-50%)" };
  }, [sliderTs, minTs, maxTs]);

  const formatStat = (value: number, hasValues: boolean) => (hasValues ? value.toFixed(2) : "--");

  return (
    <div className="section">
      <div className="section-title">Timeline</div>
      <div className="timeline-toolbar">
        <button className="button small" onClick={() => setIsPlaying(!isPlaying)}>
          {isPlaying ? "Stop timelapse" : "Play timelapse"}
        </button>
        <div className="timeline-latest">
          <div className="timeline-latest-item">
            EC {selectedReading?.ec !== undefined ? `${selectedReading.ec} mS/cm` : "--"}
          </div>
          <div className="timeline-latest-item">
            pH {selectedReading?.ph !== undefined ? `${selectedReading.ph} pH` : "--"}
          </div>
          <div className="timeline-latest-item">
            Temp {selectedReading?.temp !== undefined ? `${selectedReading.temp} °C` : "--"}
          </div>
        </div>
        <div className="hint">Events: {events.length}</div>
      </div>

      <div className="timeline-layout">
        <div className="timeline-photo">
          {selectedPhoto ? (
            <img className="camera-img" src={photoUrl(selectedPhoto.path)} alt="Captured" />
          ) : (
            <div className="timeline-placeholder">No photo selected.</div>
          )}
        </div>
        <div className="timeline-summary compact">
          <div className="tile">
            <div className="tile-label">EC (mS/cm)</div>
            <div className="tile-value">
              {selectedReading?.ec !== undefined ? `${selectedReading.ec} mS/cm` : "--"}
            </div>
          </div>
          <div className="tile">
            <div className="tile-label">pH (pH)</div>
            <div className="tile-value">
              {selectedReading?.ph !== undefined ? `${selectedReading.ph} pH` : "--"}
            </div>
          </div>
          <div className="tile">
            <div className="tile-label">Temp (°C)</div>
            <div className="tile-value">
              {selectedReading?.temp !== undefined ? `${selectedReading.temp} °C` : "--"}
            </div>
          </div>
        </div>
        <div className="timeline-chart">
          {readingChart ? (
            <>
              <div className="timeline-chart-layer">
                <div className="timeline-chart-panels">
                  {[
                    {
                      key: "ec",
                      label: "EC mS/cm",
                      dots: readingChart.ecDots,
                      stats: readingChart.ecStats,
                      dotClass: "timeline-chart-dot-ec",
                    },
                    {
                      key: "ph",
                      label: "pH pH",
                      dots: readingChart.phDots,
                      stats: readingChart.phStats,
                      dotClass: "timeline-chart-dot-ph",
                    },
                    {
                      key: "temp",
                      label: "Temp °C",
                      dots: readingChart.tempDots,
                      stats: readingChart.tempStats,
                      dotClass: "timeline-chart-dot-temp",
                    },
                  ].map((series) => (
                    <div key={series.key} className="timeline-series">
                      <div className="timeline-series-axis">
                        <div>{formatStat(series.stats.max, series.stats.hasValues)}</div>
                        <div>
                          {formatStat(
                            (series.stats.max + series.stats.min) / 2,
                            series.stats.hasValues
                          )}
                        </div>
                        <div>{formatStat(series.stats.min, series.stats.hasValues)}</div>
                      </div>
                      <svg
                        viewBox="0 -1 100 24"
                        preserveAspectRatio="none"
                        className="timeline-series-svg"
                      >
                        <rect x="0" y="0" width="100" height="22" className="timeline-chart-band" />
                        <line x1="0" x2="100" y1="11" y2="11" className="timeline-chart-grid" />
                        <line
                          x1={readingChart.markerX}
                          x2={readingChart.markerX}
                          y1="0"
                          y2="22"
                          className="timeline-chart-marker timeline-chart-marker-time"
                        />
                        {series.dots.map((dot, index) => (
                          <circle
                            key={`${series.key}-dot-${index}`}
                            cx={dot.x}
                            cy={dot.y}
                            r="0.8"
                            className={`timeline-chart-dot ${series.dotClass}`}
                          />
                        ))}
                      </svg>
                      <div className="timeline-series-label">{series.label}</div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="hint">Not enough readings for chart.</div>
          )}
        </div>
      </div>

      <div className="timeline-scroll">
        {events.length === 0 && <div className="hint">No stored readings or photos yet.</div>}
        {events.length > 0 && (
          <div className="timeline-axis-wrap">
            <div className="timeline-axis-line" />
            <div className="timeline-row">
              <div className="timeline-row-label">Values</div>
              <div className="timeline-track timeline-track-values">
                {readings.map((event) => (
                  <button
                    key={`reading-${event.ts}`}
                    className={`timeline-dot reading ${pair.readingTs === event.ts ? "active" : ""}`}
                    style={{ left: `${toPercent(event.ts)}%` }}
                    onClick={() => handleSelect(event)}
                    title={new Date(event.ts).toLocaleString()}
                  />
                ))}
              </div>
            </div>
            <div className="timeline-row">
              <div className="timeline-row-label">Photos</div>
              <div className="timeline-track timeline-track-photos">
                {photos.map((event) => (
                  <button
                    key={`photo-${event.ts}`}
                    className={`timeline-dot photo ${pair.photoTs === event.ts ? "active" : ""}`}
                    style={{ left: `${toPercent(event.ts)}%` }}
                    onClick={() => handleSelect(event)}
                    title={new Date(event.ts).toLocaleString()}
                  />
                ))}
              </div>
            </div>
            <div className="timeline-slider-wrap">
              <div className="timeline-slider-label floating" style={sliderLabelStyle}>
                {formatDate(sliderTs ?? minTs)}
              </div>
              <input
                className="timeline-slider"
                type="range"
                min={minTs ?? 0}
                max={maxTs ?? 0}
                step={1}
                value={sliderTs ?? minTs ?? 0}
                onChange={(event) => {
                  const next = Number(event.target.value);
                  const closest = findClosestEvent(next);
                  if (closest) {
                    setSliderTs(closest.ts);
                    setSelected(
                      closest.type === "reading"
                        ? { type: "reading", ts: closest.ts, reading: closest.reading }
                        : { type: "photo", ts: closest.ts, photo: closest.photo }
                    );
                  } else {
                    setSliderTs(next);
                  }
                }}
              />
              <div className="timeline-axis">
                <span>{formatDate(minTs)}</span>
                <span>{formatDate(maxTs)}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Timeline;

import { useEffect, useRef, useState } from "react";

import { Setup } from "../../types";

type Props = {
  setup: Setup;
  onPatch: (patch: Partial<Setup>) => Promise<void>;
};

const FrequencyControls = ({ setup, onPatch }: Props) => {
  const [valueIntervalMinutes, setValueIntervalMinutes] = useState(
    Math.round(setup.valueIntervalMinutes)
  );
  const [photoIntervalMinutes, setPhotoIntervalMinutes] = useState(
    Math.round(setup.photoIntervalMinutes)
  );
  const [isSaving, setIsSaving] = useState(false);
  const lastSavedRef = useRef<{ value: number; photo: number }>({
    value: Math.round(setup.valueIntervalMinutes),
    photo: Math.round(setup.photoIntervalMinutes),
  });

  useEffect(() => {
    const nextValue = Math.round(setup.valueIntervalMinutes);
    const nextPhoto = Math.round(setup.photoIntervalMinutes);
    setValueIntervalMinutes(nextValue);
    setPhotoIntervalMinutes(nextPhoto);
    lastSavedRef.current = { value: nextValue, photo: nextPhoto };
  }, [setup.valueIntervalMinutes, setup.photoIntervalMinutes]);

  const handleSave = async () => {
    const valueMinutes = Math.max(1, Math.min(1440, Number(valueIntervalMinutes) || 1));
    const photoMinutes = Math.max(1, Math.min(1440, Number(photoIntervalMinutes) || 1));
    setIsSaving(true);
    try {
      await onPatch({ valueIntervalMinutes: valueMinutes, photoIntervalMinutes: photoMinutes });
    } finally {
      setIsSaving(false);
    }
  };

  useEffect(() => {
    return () => {
      const { value, photo } = lastSavedRef.current;
      if (valueIntervalMinutes === value && photoIntervalMinutes === photo) {
        return;
      }
      void handleSave();
    };
  }, [valueIntervalMinutes, photoIntervalMinutes]);

  return (
    <div className="frequency-controls">
      <div className="row grid-two">
        <div className="field">
          <label className="label">Value interval (1–1440 min)</label>
          <div className="input-with-unit">
            <input
              className="input compact"
              type="number"
              min={1}
              max={1440}
              step={1}
              value={valueIntervalMinutes}
              onChange={(event) => setValueIntervalMinutes(Number(event.target.value))}
              placeholder="1–1440"
            />
            <span className="input-unit">min</span>
          </div>
        </div>
        <div className="field">
          <label className="label">Photo interval (1–1440 min)</label>
          <div className="input-with-unit">
            <input
              className="input compact"
              type="number"
              min={1}
              max={1440}
              step={1}
              value={photoIntervalMinutes}
              onChange={(event) => setPhotoIntervalMinutes(Number(event.target.value))}
              placeholder="1–1440"
            />
            <span className="input-unit">min</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FrequencyControls;

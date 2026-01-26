import { useEffect, useRef, useState } from "react";

import { Setup } from "../../types";

type Props = {
  setup: Setup;
  onPatch: (patch: Partial<Setup>) => Promise<void>;
};

const FrequencyControls = ({ setup, onPatch }: Props) => {
  const [valueIntervalMinutes, setValueIntervalMinutes] = useState(
    Math.round(setup.valueIntervalSec / 60)
  );
  const [photoIntervalMinutes, setPhotoIntervalMinutes] = useState(
    Math.round(setup.photoIntervalSec / 60)
  );
  const [isSaving, setIsSaving] = useState(false);
  const lastSavedRef = useRef<{ value: number; photo: number }>({
    value: Math.round(setup.valueIntervalSec / 60),
    photo: Math.round(setup.photoIntervalSec / 60),
  });

  useEffect(() => {
    const nextValue = Math.round(setup.valueIntervalSec / 60);
    const nextPhoto = Math.round(setup.photoIntervalSec / 60);
    setValueIntervalMinutes(nextValue);
    setPhotoIntervalMinutes(nextPhoto);
    lastSavedRef.current = { value: nextValue, photo: nextPhoto };
  }, [setup.valueIntervalSec, setup.photoIntervalSec]);

  const handleSave = async () => {
    const valueMinutes = Math.max(1, Math.min(1440, Number(valueIntervalMinutes) || 1));
    const photoMinutes = Math.max(1, Math.min(1440, Number(photoIntervalMinutes) || 1));
    const valueIntervalSec = valueMinutes * 60;
    const photoIntervalSec = photoMinutes * 60;
    setIsSaving(true);
    try {
      await onPatch({ valueIntervalSec, photoIntervalSec });
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

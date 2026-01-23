import { useEffect, useState } from "react";

import { Setup } from "../types";

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

  useEffect(() => {
    setValueIntervalMinutes(Math.round(setup.valueIntervalSec / 60));
    setPhotoIntervalMinutes(Math.round(setup.photoIntervalSec / 60));
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

  return (
    <div className="section">
      <div className="section-title">Frequencies</div>
      <div className="row grid-two">
        <div className="field">
          <label className="label">Value interval</label>
          <input
            className="input compact"
            type="number"
            min={1}
            max={1440}
            step={1}
            value={valueIntervalMinutes}
            onChange={(event) => setValueIntervalMinutes(Number(event.target.value))}
          />
          <div className="hint">Minutes</div>
        </div>
        <div className="field">
          <label className="label">Photo interval</label>
          <input
            className="input compact"
            type="number"
            min={1}
            max={1440}
            step={1}
            value={photoIntervalMinutes}
            onChange={(event) => setPhotoIntervalMinutes(Number(event.target.value))}
          />
          <div className="hint">Minutes</div>
        </div>
      </div>
      <div className="hint">Range: 1 min – 24 h.</div>
      <div className="hint">Live values update every 5s.</div>
      <button className="button" onClick={handleSave} disabled={isSaving}>
        Save frequencies
      </button>
    </div>
  );
};

export default FrequencyControls;

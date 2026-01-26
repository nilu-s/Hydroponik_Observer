import { FC } from "react";

type Props = {
  onClick: () => void;
  isActive?: boolean;
};

const SettingsButton: FC<Props> = ({ onClick, isActive = false }) => {
  return (
    <button
      className={`icon-button${isActive ? " is-active" : ""}`}
      onClick={onClick}
      aria-label="Toggle settings"
      title="Settings"
      type="button"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M19.14 12.94a7.8 7.8 0 0 0 .04-.94 7.8 7.8 0 0 0-.04-.94l2.11-1.65a.5.5 0 0 0 .12-.64l-2-3.46a.5.5 0 0 0-.6-.22l-2.49 1a7.2 7.2 0 0 0-1.63-.94l-.38-2.65A.5.5 0 0 0 11.8 1h-4a.5.5 0 0 0-.5.42l-.38 2.65c-.58.22-1.12.52-1.63.94l-2.49-1a.5.5 0 0 0-.6.22l-2 3.46a.5.5 0 0 0 .12.64l2.11 1.65c-.02.3-.04.62-.04.94s.02.64.04.94L.32 14.6a.5.5 0 0 0-.12.64l2 3.46c.13.23.4.32.64.22l2.49-1c.5.4 1.05.72 1.63.94l.38 2.65c.04.24.25.42.5.42h4c.25 0 .46-.18.5-.42l.38-2.65c.58-.22 1.12-.52 1.63-.94l2.49 1c.24.1.51.01.64-.22l2-3.46a.5.5 0 0 0-.12-.64l-2.11-1.66ZM9.8 15.5A3.5 3.5 0 1 1 13.3 12a3.5 3.5 0 0 1-3.5 3.5Z" />
      </svg>
    </button>
  );
};

export default SettingsButton;

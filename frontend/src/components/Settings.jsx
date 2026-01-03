import { useState, useEffect } from 'react';
import './Settings.css';

export default function Settings({
  modelsConfig,
  selectedCouncil,
  selectedChairman,
  onCouncilChange,
  onChairmanChange,
}) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!modelsConfig) return null;

  const { providers, chairman_eligible, defaults } = modelsConfig;

  // Get all available models grouped by provider
  const availableModels = [];
  Object.entries(providers).forEach(([providerName, providerData]) => {
    if (providerData.available) {
      providerData.models.forEach(model => {
        availableModels.push({
          id: model,
          label: model.split('/')[1] || model,
          provider: providerName
        });
      });
    }
  });

  // Chairman eligible models
  const chairmanModels = chairman_eligible
    .filter(model => {
      const provider = model.split('/')[0];
      return providers[provider]?.available;
    })
    .map(model => ({
      id: model,
      label: model.split('/')[1] || model
    }));

  const handleCouncilToggle = (modelId) => {
    const newSelection = selectedCouncil.includes(modelId)
      ? selectedCouncil.filter(m => m !== modelId)
      : [...selectedCouncil, modelId];

    onCouncilChange(newSelection);
  };

  const isCouncilSelected = (modelId) => selectedCouncil.includes(modelId);
  const canSelectMore = selectedCouncil.length < 3;
  const canDeselectMore = selectedCouncil.length > 1;

  return (
    <div className="settings">
      <div className="settings-header" onClick={() => setIsExpanded(!isExpanded)}>
        <span className="settings-title">Model Settings</span>
        <span className="settings-toggle">{isExpanded ? '▼' : '▶'}</span>
      </div>

      {isExpanded && (
        <div className="settings-content">
          {/* Council Models */}
          <div className="settings-section">
            <div className="settings-section-header">
              <span className="settings-section-title">Council Models</span>
              <span className="settings-hint">Select 1-3 models</span>
            </div>
            <div className="model-list">
              {availableModels.map(model => {
                const isSelected = isCouncilSelected(model.id);
                const isDisabled = !isSelected && !canSelectMore;

                return (
                  <div
                    key={model.id}
                    className={`model-option ${isDisabled ? 'disabled' : ''} ${isSelected ? 'selected' : ''}`}
                    onClick={() => {
                      if (!isDisabled && !(isSelected && !canDeselectMore)) {
                        handleCouncilToggle(model.id);
                      }
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={isSelected}
                      disabled={isDisabled || (isSelected && !canDeselectMore)}
                      onChange={() => {}}
                      onClick={(e) => e.stopPropagation()}
                    />
                    <span className="model-label">
                      <span className="model-name">{model.label}</span>
                      <span className="model-provider">{model.provider}</span>
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Chairman Model */}
          <div className="settings-section">
            <div className="settings-section-header">
              <span className="settings-section-title">Chairman Model</span>
              <span className="settings-hint">Synthesizes final answer</span>
            </div>
            <select
              className="chairman-select"
              value={selectedChairman}
              onChange={(e) => onChairmanChange(e.target.value)}
            >
              {chairmanModels.map(model => (
                <option key={model.id} value={model.id}>
                  {model.label}
                </option>
              ))}
            </select>
          </div>

          {/* Reset to Defaults */}
          <button
            className="reset-button"
            onClick={() => {
              onCouncilChange(defaults.council_models);
              onChairmanChange(defaults.chairman_model);
            }}
          >
            Reset to Defaults
          </button>
        </div>
      )}
    </div>
  );
}

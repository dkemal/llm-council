# Task: F1-FE-01 - Design Criteria Input UI Component

**Version**: 1.0.0
**Created**: 2026-01-02 11:45:00
**Last Updated**: 2026-01-02 11:45:00
**Status**: DRAFT (2026-01-02)
**Supersedes**: N/A
**Related Docs**:
  - `/.archie-tasks/epics/EPIC-F1-structured-criteria.md`
**Agent**: product-manager

---

## Task Summary

Design and implement the base Criteria Input UI component that allows users to define evaluation criteria before submitting a query.

## Complexity: M (4 hours)

## Dependencies
- None (can start in parallel with backend)

## Blocked By
- None

## Blocks
- F1-FE-02, F1-FE-03, F1-FE-04, F1-FE-05

---

## Technical Specification

### File Location
`/frontend/src/components/CriteriaInput.jsx` (new file)
`/frontend/src/components/CriteriaInput.css` (new file)

### Component Structure

```jsx
import React, { useState } from 'react';
import './CriteriaInput.css';

/**
 * CriteriaInput - Main criteria definition component
 *
 * Props:
 * - criteria: Current criteria array
 * - onCriteriaChange: Callback when criteria changes
 * - onOptionsChange: Callback when options change
 * - collapsed: Whether panel is collapsed
 * - onToggleCollapse: Toggle collapse callback
 */
export function CriteriaInput({
  criteria,
  onCriteriaChange,
  options,
  onOptionsChange,
  collapsed,
  onToggleCollapse
}) {
  const [newCriterionName, setNewCriterionName] = useState('');

  const addCriterion = () => {
    if (!newCriterionName.trim()) return;

    const newCriterion = {
      id: `c-${Date.now()}`,
      name: newCriterionName.trim(),
      type: 'scored',
      weight: 'P1',
      description: ''
    };

    onCriteriaChange([...criteria, newCriterion]);
    setNewCriterionName('');
  };

  const removeCriterion = (id) => {
    onCriteriaChange(criteria.filter(c => c.id !== id));
  };

  const updateCriterion = (id, updates) => {
    onCriteriaChange(
      criteria.map(c => c.id === id ? { ...c, ...updates } : c)
    );
  };

  return (
    <div className={`criteria-input ${collapsed ? 'collapsed' : ''}`}>
      <div className="criteria-header" onClick={onToggleCollapse}>
        <h3>Evaluation Criteria</h3>
        <span className="criteria-count">
          {criteria.length} criteria defined
        </span>
        <button className="collapse-btn">
          {collapsed ? '+' : '-'}
        </button>
      </div>

      {!collapsed && (
        <div className="criteria-content">
          {/* Quick Add */}
          <div className="criteria-add">
            <input
              type="text"
              placeholder="Add criterion (e.g., 'Pricing', 'Documentation')"
              value={newCriterionName}
              onChange={(e) => setNewCriterionName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addCriterion()}
            />
            <button onClick={addCriterion}>Add</button>
          </div>

          {/* Criteria List */}
          <div className="criteria-list">
            {criteria.map((criterion, index) => (
              <CriterionItem
                key={criterion.id}
                criterion={criterion}
                index={index}
                onUpdate={(updates) => updateCriterion(criterion.id, updates)}
                onRemove={() => removeCriterion(criterion.id)}
              />
            ))}
          </div>

          {/* Options Section */}
          <div className="options-section">
            <h4>Options to Compare (optional)</h4>
            <OptionsInput
              options={options}
              onChange={onOptionsChange}
            />
          </div>

          {/* Suggestions */}
          {criteria.length === 0 && (
            <div className="criteria-suggestions">
              <p>Quick start suggestions:</p>
              <div className="suggestion-chips">
                <button onClick={() => addPreset('api')}>API Selection</button>
                <button onClick={() => addPreset('vendor')}>Vendor Comparison</button>
                <button onClick={() => addPreset('architecture')}>Architecture Decision</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * CriterionItem - Single criterion row
 */
function CriterionItem({ criterion, index, onUpdate, onRemove }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={`criterion-item ${criterion.type}`}>
      <div className="criterion-main">
        <span className="criterion-index">{index + 1}</span>

        <input
          className="criterion-name"
          value={criterion.name}
          onChange={(e) => onUpdate({ name: e.target.value })}
        />

        <select
          className="criterion-weight"
          value={criterion.weight}
          onChange={(e) => onUpdate({ weight: e.target.value })}
        >
          <option value="P0">Critical (P0)</option>
          <option value="P1">Important (P1)</option>
          <option value="P2">Nice-to-have (P2)</option>
        </select>

        <label className="criterion-type-toggle">
          <input
            type="checkbox"
            checked={criterion.type === 'table_stakes'}
            onChange={(e) => onUpdate({
              type: e.target.checked ? 'table_stakes' : 'scored'
            })}
          />
          Must-have
        </label>

        <button className="expand-btn" onClick={() => setExpanded(!expanded)}>
          {expanded ? 'Less' : 'More'}
        </button>

        <button className="remove-btn" onClick={onRemove}>x</button>
      </div>

      {expanded && (
        <div className="criterion-details">
          <textarea
            placeholder="Description (optional) - helps AI understand what to evaluate"
            value={criterion.description || ''}
            onChange={(e) => onUpdate({ description: e.target.value })}
          />
        </div>
      )}
    </div>
  );
}

/**
 * OptionsInput - Options list input
 */
function OptionsInput({ options, onChange }) {
  const [newOption, setNewOption] = useState('');

  const addOption = () => {
    if (!newOption.trim()) return;
    onChange([...options, newOption.trim()]);
    setNewOption('');
  };

  const removeOption = (index) => {
    onChange(options.filter((_, i) => i !== index));
  };

  return (
    <div className="options-input">
      <div className="options-list">
        {options.map((option, index) => (
          <div key={index} className="option-chip">
            <span>{option}</span>
            <button onClick={() => removeOption(index)}>x</button>
          </div>
        ))}
      </div>
      <div className="option-add">
        <input
          type="text"
          placeholder="Add option (e.g., 'AWS Transcribe', 'Google Speech')"
          value={newOption}
          onChange={(e) => setNewOption(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addOption()}
        />
        <button onClick={addOption}>Add</button>
      </div>
    </div>
  );
}

export default CriteriaInput;
```

### CSS Structure

```css
/* /frontend/src/components/CriteriaInput.css */

.criteria-input {
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 16px;
}

.criteria-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  user-select: none;
}

.criteria-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.criteria-count {
  margin-left: auto;
  font-size: 12px;
  color: #666;
}

.collapse-btn {
  margin-left: 8px;
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
}

.criteria-content {
  padding: 0 16px 16px;
}

.criteria-add {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.criteria-add input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.criteria-add button {
  padding: 8px 16px;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.criteria-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.criterion-item {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 8px 12px;
}

.criterion-item.table_stakes {
  border-left: 3px solid #e74c3c;
}

.criterion-main {
  display: flex;
  align-items: center;
  gap: 8px;
}

.criterion-index {
  color: #999;
  font-size: 12px;
  width: 20px;
}

.criterion-name {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
}

.criterion-weight {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
}

.criterion-type-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #666;
}

.remove-btn {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
}

.remove-btn:hover {
  color: #e74c3c;
}

.criterion-details {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #eee;
}

.criterion-details textarea {
  width: 100%;
  min-height: 60px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
}

.options-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.options-section h4 {
  margin: 0 0 8px;
  font-size: 13px;
  color: #666;
}

.options-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.option-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: #e3f2fd;
  border-radius: 16px;
  font-size: 13px;
}

.option-chip button {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-size: 12px;
}

.criteria-suggestions {
  margin-top: 16px;
  padding: 12px;
  background: #fff3cd;
  border-radius: 4px;
}

.criteria-suggestions p {
  margin: 0 0 8px;
  font-size: 13px;
}

.suggestion-chips {
  display: flex;
  gap: 8px;
}

.suggestion-chips button {
  padding: 6px 12px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 16px;
  font-size: 12px;
  cursor: pointer;
}

.suggestion-chips button:hover {
  background: #f0f0f0;
}

/* Collapsed state */
.criteria-input.collapsed .criteria-content {
  display: none;
}
```

---

## Acceptance Criteria

- [ ] Component renders criteria input panel
- [ ] Users can add new criteria by name
- [ ] Users can remove criteria
- [ ] Users can set criterion weight (P0/P1/P2)
- [ ] Users can mark criteria as "Must-have" (table stakes)
- [ ] Users can add optional descriptions
- [ ] Users can define options to compare
- [ ] Panel is collapsible to save space
- [ ] Empty state shows quick-start suggestions
- [ ] Full keyboard accessibility

---

## Validation Steps

### Visual/Interactive Tests

1. **Add criterion flow**:
   - Type name in input
   - Press Enter or click Add
   - Verify criterion appears in list

2. **Edit criterion**:
   - Change name inline
   - Change weight dropdown
   - Toggle must-have checkbox
   - Add description via More button

3. **Remove criterion**:
   - Click X button
   - Verify removal from list

4. **Options flow**:
   - Add multiple options
   - Remove option via chip X
   - Verify chips display correctly

5. **Collapse/Expand**:
   - Click header to collapse
   - Verify count shows in header
   - Click to expand

### Accessibility Tests

1. Tab through all interactive elements
2. Verify focus states visible
3. Screen reader announces labels
4. Enter key works for form submission

---

## Implementation Notes

- Use controlled components for all inputs
- Debounce description textarea changes
- Consider localStorage for draft criteria persistence
- Keep component stateless - state managed by parent


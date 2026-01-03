# Task: F1-FE-06 - Create Scoring Matrix Component

**Version**: 1.0.0
**Created**: 2026-01-02 11:45:00
**Last Updated**: 2026-01-02 11:45:00
**Status**: DRAFT (2026-01-02)
**Supersedes**: N/A
**Related Docs**:
  - `/.archie-tasks/epics/EPIC-F1-structured-criteria.md`
  - `/.archie-tasks/backlog/F1-BE-07-scoring-matrix.md`
**Agent**: product-manager

---

## Task Summary

Create the visual scoring matrix component that displays option scores per criterion with color coding, rankings, and drill-down capability.

## Complexity: L (8 hours)

## Dependencies
- F1-BE-07 (Backend scoring matrix)

## Blocked By
- F1-BE-07

## Blocks
- F1-INT-02

---

## Technical Specification

### File Location
`/frontend/src/components/ScoringMatrix.jsx` (new file)
`/frontend/src/components/ScoringMatrix.css` (new file)

### Component Structure

```jsx
import React, { useState } from 'react';
import './ScoringMatrix.css';

/**
 * ScoringMatrix - Visual comparison grid
 *
 * Props:
 * - matrix: ScoringMatrix data from backend
 * - onCellClick: Callback when clicking a cell for details
 */
export function ScoringMatrix({ matrix, onCellClick }) {
  const [sortBy, setSortBy] = useState('rank');
  const [hoveredCell, setHoveredCell] = useState(null);

  if (!matrix || !matrix.options.length) {
    return <div className="matrix-empty">No scoring data available</div>;
  }

  const { options, criteria, recommendation, all_disqualified_warning } = matrix;

  // Sort options
  const sortedOptions = [...options].sort((a, b) => {
    if (sortBy === 'rank') return a.rank - b.rank;
    if (sortBy === 'score') return b.total_weighted_score - a.total_weighted_score;
    return 0;
  });

  return (
    <div className="scoring-matrix">
      {/* Header with recommendation */}
      <div className="matrix-header">
        <h3>Scoring Matrix</h3>
        {recommendation && (
          <div className="recommendation">{recommendation}</div>
        )}
        {all_disqualified_warning && (
          <div className="warning">{all_disqualified_warning}</div>
        )}
      </div>

      {/* Sort controls */}
      <div className="matrix-controls">
        <span>Sort by:</span>
        <button
          className={sortBy === 'rank' ? 'active' : ''}
          onClick={() => setSortBy('rank')}
        >
          Rank
        </button>
        <button
          className={sortBy === 'score' ? 'active' : ''}
          onClick={() => setSortBy('score')}
        >
          Total Score
        </button>
      </div>

      {/* Matrix table */}
      <div className="matrix-table-wrapper">
        <table className="matrix-table">
          <thead>
            <tr>
              <th className="option-header">Option</th>
              {criteria.map(c => (
                <th
                  key={c.id}
                  className={`criterion-header ${c.type}`}
                  title={c.type === 'table_stakes' ? 'Must-have requirement' : `Weight: ${c.weight}`}
                >
                  {c.name}
                  {c.type === 'table_stakes' && <span className="ts-badge">TS</span>}
                </th>
              ))}
              <th className="total-header">Total</th>
            </tr>
          </thead>
          <tbody>
            {sortedOptions.map((option, rowIndex) => (
              <tr
                key={option.option_name}
                className={option.disqualified ? 'disqualified' : ''}
              >
                <td className="option-cell">
                  <span className="rank-badge">#{option.rank}</span>
                  <span className="option-name">{option.option_name}</span>
                  {option.disqualified && (
                    <span className="dq-badge" title={option.disqualification_reason}>
                      DQ
                    </span>
                  )}
                </td>

                {criteria.map(criterion => {
                  const score = option.criterion_scores.find(
                    s => s.criterion_id === criterion.id
                  );
                  return (
                    <ScoreCell
                      key={criterion.id}
                      score={score}
                      criterionType={criterion.type}
                      isHovered={hoveredCell === `${option.option_name}-${criterion.id}`}
                      onMouseEnter={() => setHoveredCell(`${option.option_name}-${criterion.id}`)}
                      onMouseLeave={() => setHoveredCell(null)}
                      onClick={() => onCellClick && onCellClick(option, score)}
                    />
                  );
                })}

                <td className="total-cell">
                  <span className="total-score">
                    {option.total_weighted_score.toFixed(1)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="matrix-legend">
        <div className="legend-item">
          <span className="legend-color score-high"></span>
          <span>8-10: Excellent</span>
        </div>
        <div className="legend-item">
          <span className="legend-color score-medium"></span>
          <span>5-7: Adequate</span>
        </div>
        <div className="legend-item">
          <span className="legend-color score-low"></span>
          <span>1-4: Poor</span>
        </div>
        <div className="legend-item">
          <span className="ts-badge">TS</span>
          <span>Table Stakes (Must Pass)</span>
        </div>
      </div>
    </div>
  );
}

/**
 * ScoreCell - Individual score cell with color coding
 */
function ScoreCell({ score, criterionType, isHovered, onMouseEnter, onMouseLeave, onClick }) {
  if (!score) {
    return (
      <td className="score-cell no-data">
        <span>N/A</span>
      </td>
    );
  }

  // Determine cell class based on score
  let cellClass = 'score-cell';

  if (criterionType === 'table_stakes') {
    // Pass/fail styling
    if (score.pass_count > 0 && score.fail_count === 0) {
      cellClass += ' pass';
    } else if (score.fail_count > 0) {
      cellClass += ' fail';
    }
  } else {
    // Numeric score styling
    const avg = score.average_score;
    if (avg >= 8) cellClass += ' score-high';
    else if (avg >= 5) cellClass += ' score-medium';
    else if (avg !== null) cellClass += ' score-low';
  }

  // Add consensus indicator
  if (score.consensus === 'low') cellClass += ' low-consensus';

  return (
    <td
      className={cellClass}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      onClick={onClick}
    >
      {criterionType === 'table_stakes' ? (
        <span className="pass-fail">
          {score.fail_count > 0 ? 'FAIL' : 'PASS'}
        </span>
      ) : (
        <>
          <span className="score-value">
            {score.average_score?.toFixed(1) || 'N/A'}
          </span>
          {score.consensus === 'low' && (
            <span className="consensus-indicator" title="Low model agreement">!</span>
          )}
        </>
      )}

      {/* Hover tooltip */}
      {isHovered && score.model_scores && (
        <div className="score-tooltip">
          <div className="tooltip-header">Model Scores:</div>
          {Object.entries(score.model_scores).map(([model, s]) => (
            <div key={model} className="tooltip-row">
              <span className="model-name">{formatModelName(model)}</span>
              <span className="model-score">{s}</span>
            </div>
          ))}
          {score.std_dev !== null && (
            <div className="tooltip-footer">
              Range: {score.min_score}-{score.max_score} (SD: {score.std_dev})
            </div>
          )}
        </div>
      )}
    </td>
  );
}

/**
 * Format model name for display
 */
function formatModelName(modelId) {
  // "openai/gpt-4" -> "GPT-4"
  const parts = modelId.split('/');
  const name = parts[parts.length - 1];
  return name.replace('gpt-', 'GPT-').replace('claude-', 'Claude ');
}

export default ScoringMatrix;
```

### CSS Structure

```css
/* /frontend/src/components/ScoringMatrix.css */

.scoring-matrix {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.matrix-header {
  margin-bottom: 16px;
}

.matrix-header h3 {
  margin: 0 0 8px;
  font-size: 16px;
}

.recommendation {
  padding: 8px 12px;
  background: #e8f5e9;
  border-radius: 4px;
  font-size: 14px;
  color: #2e7d32;
}

.warning {
  padding: 8px 12px;
  background: #fff3cd;
  border-radius: 4px;
  font-size: 14px;
  color: #856404;
  margin-top: 8px;
}

.matrix-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 13px;
}

.matrix-controls button {
  padding: 4px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
}

.matrix-controls button.active {
  background: #4a90e2;
  color: white;
  border-color: #4a90e2;
}

.matrix-table-wrapper {
  overflow-x: auto;
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.matrix-table th,
.matrix-table td {
  padding: 10px 12px;
  text-align: center;
  border-bottom: 1px solid #e0e0e0;
}

.matrix-table th {
  background: #f5f5f5;
  font-weight: 600;
  white-space: nowrap;
}

.option-header {
  text-align: left !important;
  min-width: 150px;
}

.criterion-header {
  min-width: 80px;
}

.criterion-header.table_stakes {
  background: #ffebee;
}

.ts-badge {
  display: inline-block;
  padding: 2px 4px;
  background: #e74c3c;
  color: white;
  border-radius: 3px;
  font-size: 10px;
  margin-left: 4px;
}

.option-cell {
  text-align: left !important;
  display: flex;
  align-items: center;
  gap: 8px;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #4a90e2;
  color: white;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 600;
}

.option-name {
  font-weight: 500;
}

.dq-badge {
  padding: 2px 6px;
  background: #e74c3c;
  color: white;
  border-radius: 3px;
  font-size: 10px;
  cursor: help;
}

/* Disqualified row */
tr.disqualified {
  opacity: 0.6;
  background: #f9f9f9;
}

tr.disqualified .rank-badge {
  background: #999;
}

/* Score cell colors */
.score-cell {
  position: relative;
  cursor: pointer;
  transition: background 0.2s;
}

.score-cell:hover {
  background: #f0f0f0;
}

.score-cell.score-high {
  background: #c8e6c9;
}

.score-cell.score-medium {
  background: #fff9c4;
}

.score-cell.score-low {
  background: #ffcdd2;
}

.score-cell.pass {
  background: #c8e6c9;
}

.score-cell.fail {
  background: #ffcdd2;
}

.score-cell.no-data {
  color: #999;
  font-style: italic;
}

.score-value {
  font-weight: 600;
}

.consensus-indicator {
  display: inline-block;
  width: 14px;
  height: 14px;
  background: #ff9800;
  color: white;
  border-radius: 50%;
  font-size: 10px;
  font-weight: bold;
  margin-left: 4px;
}

.pass-fail {
  font-weight: 600;
  font-size: 11px;
}

.total-cell {
  background: #e3f2fd !important;
  font-weight: 600;
}

.total-score {
  font-size: 14px;
}

/* Tooltip */
.score-tooltip {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  min-width: 150px;
  text-align: left;
}

.tooltip-header {
  font-weight: 600;
  margin-bottom: 6px;
  font-size: 12px;
  color: #666;
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  padding: 2px 0;
}

.model-name {
  color: #666;
}

.model-score {
  font-weight: 500;
}

.tooltip-footer {
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid #eee;
  font-size: 11px;
  color: #999;
}

/* Legend */
.matrix-legend {
  display: flex;
  gap: 16px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #e0e0e0;
  font-size: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

.legend-color.score-high {
  background: #c8e6c9;
}

.legend-color.score-medium {
  background: #fff9c4;
}

.legend-color.score-low {
  background: #ffcdd2;
}
```

---

## Acceptance Criteria

- [ ] Matrix displays all options as rows
- [ ] Matrix displays all criteria as columns
- [ ] Cells are color-coded by score (green/yellow/red)
- [ ] Table Stakes show PASS/FAIL instead of numbers
- [ ] Disqualified options shown greyed out at bottom
- [ ] Rank badges show position (#1, #2, etc.)
- [ ] Hover reveals per-model scores
- [ ] Low consensus indicated with warning icon
- [ ] Sort by rank or total score
- [ ] Recommendation text displayed prominently
- [ ] Legend explains color coding
- [ ] Responsive: horizontal scroll on mobile

---

## Validation Steps

### Visual Tests

1. **Score colors**:
   - 8-10: Green
   - 5-7: Yellow
   - 1-4: Red
   - Table Stakes: Green (PASS) / Red (FAIL)

2. **Hover tooltip**:
   - Shows all model scores
   - Shows range and std dev
   - Positioned correctly

3. **Disqualified styling**:
   - Row greyed out
   - DQ badge visible
   - Rank badge grey

4. **Sorting**:
   - Rank button: Order by #1, #2...
   - Score button: Order by total descending

5. **Responsive**:
   - Table scrolls horizontally on narrow screens
   - Headers stay visible

### Data Tests

1. Test with 2 options, 3 criteria
2. Test with 5 options, 10 criteria (horizontal scroll)
3. Test with all options disqualified
4. Test with mixed pass/fail table stakes

---

## Implementation Notes

- Use CSS Grid for better alignment if table proves problematic
- Consider virtualization for very large matrices
- Tooltip positioning may need adjustment for edge cells
- Cache color calculations for performance


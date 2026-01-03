# Model Selection UI - ARCHIE Catalogue Solutions (Brainstorm)

**Version**: 1.0.0
**Created**: 2026-01-03 18:45:00
**Last Updated**: 2026-01-03 18:45:00
**Status**: 🟡 DRAFT (2026-01-03)
**Supersedes**: N/A
**Related Docs**:
- `/.prd/features/model-selection-v1.0.0.md`
- `/.archie-workspace/audits/model-selection-ux-design.md` (existing design spec)
**Agent**: wireframe-recommender

---

## Design Brief

**JTBD**: Multi-select 1-3 council models + single-select 1 chairman model from available options

**Constraints**:
- Sidebar width: 260px
- Settings panel context
- Must show model metadata (provider, cost tier, capabilities)
- Visual distinction between council vs chairman selection
- Mobile-responsive (Settings component will be full-screen modal on mobile)

**Data Structure**:
```typescript
interface Model {
  id: string;           // e.g., "openai/gpt-4o"
  name: string;         // e.g., "GPT-4o"
  provider: string;     // e.g., "OpenAI"
  costTier: "free" | "low" | "medium" | "high";
  capabilities: string[]; // ["reasoning", "fast", "multilingual"]
  available: boolean;   // based on configured API keys
}
```

**Context**: This document provides ALTERNATIVE solutions discovered through ARCHIE's 803-component catalogue search. The existing design spec (`model-selection-ux-design.md`) uses a collapsible sidebar approach with provider groups. These solutions explore different interaction patterns.

---

## ARCHIE Catalogue Search Results

**Components Found**:
- `spectrumui-multiple-selector-*` (10 variants, Quality: 70/100) - Tag-based multi-select
- `animateui-demo-primitives-radix-toggle-group` (Quality: 80/100) - Toggle groups
- `animateui-demo-components-base-radio-group` (Quality: 85/100) - Radio groups
- shadcn/ui components: ToggleGroup, RadioGroup, Card, Badge, Switch, Checkbox

**Sources**:
- Spectrum UI: ~60 components (mixed quality, external dependencies)
- Animate UI: ~450 components (high quality, Framer Motion)
- shadcn/ui: 48/48 components (production-ready, Radix primitives)

---

## Solution 1: Toggle Group + Radio Cards (RECOMMENDED)

**ARCHIE References**:
- `animateui-demo-primitives-radix-toggle-group` (Quality: 80/100)
- `shadcn/ui RadioGroup` + `shadcn/ui Card`
- `shadcn/ui Badge` for metadata

### Design Rationale
- Toggle groups excellent for multi-select with visual feedback
- Radio cards provide single-select with rich metadata display
- All shadcn-native components (high maintainability)
- Fits 260px sidebar width perfectly

### Layout Structure

```
┌─────────────────────────────────────┐
│ Settings                            │
├─────────────────────────────────────┤
│                                     │
│ Council Models (select 1-3)         │
│ ┌─────────┬─────────┬─────────┐    │
│ │  GPT-4  │ Claude │ Gemini  │    │ ← Toggle Group
│ │  [ON]   │  [ON]  │  [OFF]  │    │   type="multiple"
│ └─────────┴─────────┴─────────┘    │
│                                     │
│ Chairman Model                      │
│ ┌───────────────────────────────┐  │
│ │ ● GPT-4 Turbo                 │  │ ← Radio Card
│ │   OpenAI | Medium cost        │  │   (selected)
│ │   [reasoning][fast]           │  │
│ └───────────────────────────────┘  │
│ ┌───────────────────────────────┐  │
│ │ ○ Claude Opus                 │  │ ← Radio Card
│ │   Anthropic | High cost       │  │   (unselected)
│ │   [reasoning][thorough]       │  │
│ └───────────────────────────────┘  │
│                                     │
│ [Save Configuration]                │
└─────────────────────────────────────┘
```

### Code Snippet (Adapted Pattern)

```tsx
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';

export function ModelSelector({ models, config, onChange }) {
  return (
    <div className="space-y-6">
      {/* Council Models - Multi-Select */}
      <div>
        <Label>Council Models (select 1-3)</Label>
        <ToggleGroup
          type="multiple"
          value={config.councilModels}
          onValueChange={(value) =>
            value.length >= 1 && value.length <= 3 &&
            onChange({ ...config, councilModels: value })
          }
          className="grid grid-cols-3 gap-2 mt-2"
        >
          {models.filter(m => m.available).map(model => (
            <ToggleGroupItem
              key={model.id}
              value={model.id}
              className="flex flex-col items-center p-2 text-xs"
              disabled={
                config.councilModels.length >= 3 &&
                !config.councilModels.includes(model.id)
              }
            >
              <span className="font-medium">{model.name}</span>
              <span className="text-muted-foreground text-[10px]">
                {model.provider}
              </span>
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      </div>

      {/* Chairman Model - Single-Select */}
      <div>
        <Label>Chairman Model</Label>
        <RadioGroup
          value={config.chairmanModel}
          onValueChange={(value) =>
            onChange({ ...config, chairmanModel: value })
          }
          className="space-y-2 mt-2"
        >
          {models.filter(m => m.available).map(model => (
            <Card
              key={model.id}
              className={cn(
                "cursor-pointer transition-colors",
                config.chairmanModel === model.id && "border-primary"
              )}
              onClick={() => onChange({ ...config, chairmanModel: model.id })}
            >
              <CardContent className="p-3">
                <div className="flex items-start gap-2">
                  <RadioGroupItem value={model.id} id={model.id} />
                  <div className="flex-1 space-y-1">
                    <Label
                      htmlFor={model.id}
                      className="font-medium cursor-pointer"
                    >
                      {model.name}
                    </Label>
                    <div className="text-xs text-muted-foreground">
                      {model.provider} | {model.costTier} cost
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {model.capabilities.map(cap => (
                        <Badge
                          key={cap}
                          variant="outline"
                          className="text-[10px] px-1"
                        >
                          {cap}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </RadioGroup>
      </div>
    </div>
  );
}
```

### Pros
- All shadcn-native (zero custom components needed)
- Clear visual distinction (toggle vs radio cards)
- Compact for council (3-column toggle grid)
- Rich metadata display for chairman (cards)
- Accessible (built on Radix primitives)
- Easy validation (disable when 3 selected)

### Cons
- Toggle items limited to 2-line text (name + provider)
- Requires scrolling if 10+ chairman options

### ARCHIE Score: 94/100
- Layout match: 30/30 (perfect for settings panel)
- Components match: 38/40 (has all required, minor customization)
- Quality: 18/20 (shadcn production-ready)
- Context match: 8/10 (internal tool context)

---

## Solution 2: Multi-Selector Dropdown + Radio Cards

**ARCHIE References**:
- `spectrumui-multiple-selector-demo` (Quality: 70/100)
- `shadcn/ui RadioGroup` + `shadcn/ui Card`

### Design Rationale
- Dropdown saves vertical space for council selection
- Familiar pattern (similar to tag selectors)
- Same rich cards for chairman selection

### Layout Structure

```
┌─────────────────────────────────────┐
│ Settings                            │
├─────────────────────────────────────┤
│                                     │
│ Council Models (select 1-3)         │
│ ┌───────────────────────────────┐  │
│ │ [GPT-4] [Claude] [×]          │  │ ← Multi-Selector
│ │ Select frameworks...       ▼  │  │   (chip style)
│ └───────────────────────────────┘  │
│                                     │
│ Chairman Model                      │
│ [Same radio cards as Solution 1]   │
│                                     │
└─────────────────────────────────────┘
```

### Code Snippet

```tsx
import MultipleSelector from '@/components/ui/multiple-selector';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Card } from '@/components/ui/card';

export function ModelSelector({ models, config, onChange }) {
  const councilOptions = models
    .filter(m => m.available)
    .map(m => ({
      label: `${m.name} (${m.provider})`,
      value: m.id
    }));

  return (
    <div className="space-y-6">
      {/* Council Models - Multi-Selector Dropdown */}
      <div>
        <Label>Council Models (select 1-3)</Label>
        <MultipleSelector
          value={config.councilModels.map(id => ({
            label: models.find(m => m.id === id)?.name,
            value: id
          }))}
          onChange={(selected) => {
            if (selected.length >= 1 && selected.length <= 3) {
              onChange({
                ...config,
                councilModels: selected.map(s => s.value)
              });
            }
          }}
          options={councilOptions}
          placeholder="Select council models..."
          maxSelected={3}
          className="mt-2"
        />
      </div>

      {/* Chairman - Same as Solution 1 */}
    </div>
  );
}
```

### Pros
- Very compact (single input field)
- Scales to 100+ models without UI clutter
- Search capability built-in
- Familiar UX pattern

### Cons
- Requires external dependency (`spectrumui-multiple-selector`)
- Less immediate visibility (must click to see options)
- Chip tags can overflow on narrow screens

### ARCHIE Score: 82/100
- Layout match: 25/30 (compact but hides options)
- Components match: 35/40 (requires external dependency)
- Quality: 14/20 (Spectrum UI lower quality)
- Context match: 8/10 (good for internal tools)

---

## Solution 3: Checkbox Cards (Uniform Pattern)

**ARCHIE References**:
- `shadcn/ui Checkbox`
- `shadcn/ui Card`
- `shadcn/ui Badge`

### Design Rationale
- Uniform pattern for both selections (cards + checkboxes)
- Rich metadata display for both council and chairman
- Simpler mental model (one pattern vs toggle + radio)

### Layout Structure

```
┌─────────────────────────────────────┐
│ Settings                            │
├─────────────────────────────────────┤
│                                     │
│ Council Models (1-3)                │
│ ┌───────────────────────────────┐  │
│ │ ☑ GPT-4 Turbo                 │  │ ← Checkbox Card
│ │   OpenAI | Medium             │  │
│ └───────────────────────────────┘  │
│ ┌───────────────────────────────┐  │
│ │ ☑ Claude Opus                 │  │
│ │   Anthropic | High            │  │
│ └───────────────────────────────┘  │
│ ┌───────────────────────────────┐  │
│ │ ☐ Gemini Flash (disabled)     │  │ ← Disabled
│ │   Google | Low                │  │   (max 3 reached)
│ └───────────────────────────────┘  │
│                                     │
│ Chairman Model                      │
│ ┌───────────────────────────────┐  │
│ │ ☑ GPT-4 Turbo                 │  │ ← Checkbox Card
│ │   OpenAI | Medium             │  │   (single-select)
│ └───────────────────────────────┘  │
│ ┌───────────────────────────────┐  │
│ │ ☐ Claude Opus                 │  │
│ │   Anthropic | High            │  │
│ └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Code Snippet

```tsx
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';

export function ModelSelector({ models, config, onChange }) {
  const toggleCouncilModel = (modelId: string) => {
    const current = config.councilModels;
    const updated = current.includes(modelId)
      ? current.filter(id => id !== modelId)
      : [...current, modelId];

    if (updated.length >= 1 && updated.length <= 3) {
      onChange({ ...config, councilModels: updated });
    }
  };

  return (
    <div className="space-y-6">
      {/* Council Models - Multi-Select Checkboxes */}
      <div>
        <Label>Council Models (select 1-3)</Label>
        <div className="space-y-2 mt-2">
          {models.filter(m => m.available).map(model => {
            const isSelected = config.councilModels.includes(model.id);
            const isDisabled =
              !isSelected && config.councilModels.length >= 3;

            return (
              <Card
                key={model.id}
                className={cn(
                  "cursor-pointer transition-colors",
                  isSelected && "border-primary bg-primary/5",
                  isDisabled && "opacity-50 cursor-not-allowed"
                )}
                onClick={() => !isDisabled && toggleCouncilModel(model.id)}
              >
                <CardContent className="p-3">
                  <div className="flex items-start gap-3">
                    <Checkbox
                      checked={isSelected}
                      disabled={isDisabled}
                      onCheckedChange={() => toggleCouncilModel(model.id)}
                    />
                    <div className="flex-1">
                      <div className="font-medium">{model.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {model.provider} | {model.costTier}
                      </div>
                      <div className="flex gap-1 mt-1">
                        {model.capabilities.slice(0, 2).map(cap => (
                          <Badge
                            key={cap}
                            variant="outline"
                            className="text-[10px]"
                          >
                            {cap}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Chairman Model - Single-Select Checkboxes */}
      <div>
        <Label>Chairman Model</Label>
        <div className="space-y-2 mt-2">
          {models.filter(m => m.available).map(model => (
            <Card
              key={model.id}
              className={cn(
                "cursor-pointer transition-colors",
                config.chairmanModel === model.id &&
                  "border-primary bg-primary/5"
              )}
              onClick={() =>
                onChange({ ...config, chairmanModel: model.id })
              }
            >
              <CardContent className="p-3">
                <div className="flex items-start gap-3">
                  <Checkbox
                    checked={config.chairmanModel === model.id}
                    onCheckedChange={() =>
                      onChange({ ...config, chairmanModel: model.id })
                    }
                  />
                  <div className="flex-1">
                    <div className="font-medium">{model.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {model.provider} | {model.costTier}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
```

### Pros
- Uniform pattern (easier to understand)
- Rich metadata for both selections
- All shadcn-native
- Visually clear (cards + checkboxes)

### Cons
- Uses checkboxes for single-select (non-standard pattern)
- More vertical space required (card per model)
- Scrolling required with 8+ models

### ARCHIE Score: 86/100
- Layout match: 26/30 (good but verbose)
- Components match: 40/40 (perfect match)
- Quality: 18/20 (shadcn quality)
- Context match: 7/10 (uniform pattern less intuitive)

---

## Solution 4: Compact List + Switch (Mobile-Optimized)

**ARCHIE References**:
- `shadcn/ui Switch`
- `shadcn/ui RadioGroup`
- Minimal card usage

### Design Rationale
- Optimized for narrow screens (260px sidebar)
- Switch provides clear on/off state
- Very compact vertical layout

### Layout Structure

```
┌─────────────────────────────────────┐
│ Settings                            │
├─────────────────────────────────────┤
│                                     │
│ Council Models (1-3)                │
│ ┌───────────────────────────────┐  │
│ │ GPT-4 Turbo        [●─────]   │  │ ← Switch ON
│ │ OpenAI · Medium               │  │
│ ├───────────────────────────────┤  │
│ │ Claude Opus        [●─────]   │  │ ← Switch ON
│ │ Anthropic · High              │  │
│ ├───────────────────────────────┤  │
│ │ Gemini Flash       [─────○]   │  │ ← Switch OFF
│ │ Google · Low                  │  │   (disabled)
│ └───────────────────────────────┘  │
│                                     │
│ Chairman Model                      │
│ ○ GPT-4 Turbo (OpenAI)              │ ← Radio button
│ ● Claude Opus (Anthropic)           │
│ ○ Gemini Pro (Google)               │
│                                     │
└─────────────────────────────────────┘
```

### Code Snippet

```tsx
import { Switch } from '@/components/ui/switch';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';

export function ModelSelector({ models, config, onChange }) {
  return (
    <div className="space-y-6">
      {/* Council Models - Switch List */}
      <div>
        <Label className="text-sm font-medium">
          Council Models (1-3)
        </Label>
        <div className="mt-2 border rounded-md divide-y">
          {models.filter(m => m.available).map(model => {
            const isSelected = config.councilModels.includes(model.id);
            const isDisabled =
              !isSelected && config.councilModels.length >= 3;

            return (
              <div
                key={model.id}
                className="flex items-center justify-between p-3"
              >
                <div className="flex-1 pr-3">
                  <div className="text-sm font-medium">{model.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {model.provider} · {model.costTier}
                  </div>
                </div>
                <Switch
                  checked={isSelected}
                  disabled={isDisabled}
                  onCheckedChange={() => {
                    const updated = isSelected
                      ? config.councilModels.filter(id => id !== model.id)
                      : [...config.councilModels, model.id];

                    if (updated.length >= 1 && updated.length <= 3) {
                      onChange({ ...config, councilModels: updated });
                    }
                  }}
                />
              </div>
            );
          })}
        </div>
      </div>

      {/* Chairman Model - Radio List */}
      <div>
        <Label className="text-sm font-medium">Chairman Model</Label>
        <RadioGroup
          value={config.chairmanModel}
          onValueChange={(value) =>
            onChange({ ...config, chairmanModel: value })
          }
          className="mt-2 space-y-2"
        >
          {models.filter(m => m.available).map(model => (
            <div
              key={model.id}
              className="flex items-center space-x-2"
            >
              <RadioGroupItem value={model.id} id={model.id} />
              <Label
                htmlFor={model.id}
                className="flex-1 text-sm cursor-pointer"
              >
                <span className="font-medium">{model.name}</span>
                <span className="text-muted-foreground ml-1">
                  ({model.provider})
                </span>
              </Label>
            </div>
          ))}
        </RadioGroup>
      </div>
    </div>
  );
}
```

### Pros
- Most compact design (fits 260px perfectly)
- Clear on/off states (switches)
- All shadcn-native
- Minimal scrolling needed

### Cons
- Less metadata visible (only provider + cost tier)
- Switches less common for multi-select
- No capability badges shown

### ARCHIE Score: 88/100
- Layout match: 28/30 (excellent compactness)
- Components match: 38/40 (slight pattern mismatch)
- Quality: 18/20 (shadcn quality)
- Context match: 9/10 (perfect for narrow sidebar)

---

## Solution 5: Badge Selector + Dropdown (Tag-Based)

**ARCHIE References**:
- `shadcn/ui Badge` (interactive variant)
- `shadcn/ui Select` (for chairman)

### Design Rationale
- Tag/badge-based multi-select (familiar pattern)
- Compact horizontal layout
- Dropdown for chairman (space-efficient)

### Layout Structure

```
┌─────────────────────────────────────┐
│ Settings                            │
├─────────────────────────────────────┤
│                                     │
│ Council Models (1-3)                │
│ ┌───────────────────────────────┐  │
│ │ Available models:             │  │
│ │ [GPT-4×] [Claude×] [Gemini]   │  │ ← Interactive badges
│ │ [Llama] [Mistral]             │  │   (selected have ×)
│ └───────────────────────────────┘  │
│                                     │
│ Selected: GPT-4, Claude (2/3)       │ ← Counter
│                                     │
│ Chairman Model                      │
│ ┌───────────────────────────────┐  │
│ │ Claude Opus (Anthropic)    ▼  │  │ ← Dropdown
│ └───────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

### Code Snippet

```tsx
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { X } from 'lucide-react';

export function ModelSelector({ models, config, onChange }) {
  const toggleCouncilModel = (modelId: string) => {
    const current = config.councilModels;
    const updated = current.includes(modelId)
      ? current.filter(id => id !== modelId)
      : [...current, modelId];

    if (updated.length >= 1 && updated.length <= 3) {
      onChange({ ...config, councilModels: updated });
    }
  };

  return (
    <div className="space-y-6">
      {/* Council Models - Badge Selector */}
      <div>
        <Label>Council Models (select 1-3)</Label>
        <div className="flex flex-wrap gap-2 mt-2 p-3 border rounded-md min-h-[80px]">
          {models.filter(m => m.available).map(model => {
            const isSelected = config.councilModels.includes(model.id);
            const isDisabled =
              !isSelected && config.councilModels.length >= 3;

            return (
              <Badge
                key={model.id}
                variant={isSelected ? "default" : "outline"}
                className={cn(
                  "cursor-pointer transition-colors px-3 py-1",
                  isDisabled && "opacity-50 cursor-not-allowed"
                )}
                onClick={() => !isDisabled && toggleCouncilModel(model.id)}
              >
                {model.name}
                {isSelected && (
                  <X className="ml-1 h-3 w-3" />
                )}
              </Badge>
            );
          })}
        </div>
        <div className="text-xs text-muted-foreground mt-1">
          Selected: {config.councilModels.map(id =>
            models.find(m => m.id === id)?.name
          ).join(', ')} ({config.councilModels.length}/3)
        </div>
      </div>

      {/* Chairman Model - Dropdown */}
      <div>
        <Label>Chairman Model</Label>
        <Select
          value={config.chairmanModel}
          onValueChange={(value) =>
            onChange({ ...config, chairmanModel: value })
          }
        >
          <SelectTrigger className="mt-2">
            <SelectValue placeholder="Select chairman..." />
          </SelectTrigger>
          <SelectContent>
            {models.filter(m => m.available).map(model => (
              <SelectItem key={model.id} value={model.id}>
                <div className="flex flex-col">
                  <span className="font-medium">{model.name}</span>
                  <span className="text-xs text-muted-foreground">
                    {model.provider} | {model.costTier}
                  </span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
```

### Pros
- Very compact horizontal layout
- Familiar tag-selection pattern
- All shadcn-native
- Clear counter shows progress (2/3)

### Cons
- No metadata visible for council models
- Badge overflow on very narrow screens
- Less accessible than dedicated form controls

### ARCHIE Score: 78/100
- Layout match: 24/30 (compact but lacks metadata)
- Components match: 38/40 (good match)
- Quality: 16/20 (badges less accessible)
- Context match: 7/10 (tag pattern less common in settings)

---

## Recommendation Matrix

| Solution | Compactness | Metadata Richness | shadcn-Native | Accessibility | Mobile-Friendly | ARCHIE Score |
|----------|-------------|-------------------|---------------|---------------|-----------------|--------------|
| **1: Toggle + Radio Cards** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **94/100** |
| 2: Multi-Selector + Cards | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 82/100 |
| 3: Checkbox Cards | ⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐ | ⭐⭐ | 86/100 |
| 4: Switch + Radio List | ⭐⭐⭐⭐⭐ | ⭐⭐ | ✅ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 88/100 |
| 5: Badge + Dropdown | ⭐⭐⭐⭐ | ⭐ | ✅ | ⭐⭐⭐ | ⭐⭐⭐ | 78/100 |

---

## Final Recommendation

**Solution 1: Toggle Group + Radio Cards** is recommended:

### Why This Solution?

1. **Best balance**: Compact council selection (3-column grid) + rich chairman metadata (cards)
2. **100% shadcn-native**: Zero external dependencies, aligns with project standards
3. **Excellent accessibility**: Built on Radix primitives with proper ARIA labels
4. **Clear visual distinction**: Toggle groups clearly communicate "multi-select", radio cards clearly communicate "single-select"
5. **Validation-friendly**: Easy to disable toggle items when max (3) reached
6. **Fits constraints**: Works perfectly in 260px sidebar, responsive on mobile
7. **Highest ARCHIE score**: 94/100 (best pattern match from catalogue)

### Alternative Use Cases

- **Solution 4 (Switch + Radio)**: Consider if model list grows to 15+ items (more compact)
- **Solution 2 (Multi-Selector)**: Consider if search/filter becomes critical requirement
- **Solution 3 (Checkbox Cards)**: Consider if chairman needs same metadata richness as council

### Comparison with Existing Design

The existing design spec (`model-selection-ux-design.md`) uses:
- Provider-grouped checkboxes for council models
- Dropdown for chairman model
- Collapsible sidebar section

**ARCHIE Solution 1 differs**:
- Toggle group (more visual feedback than checkboxes)
- Radio cards (richer metadata than dropdown)
- Same collapsible pattern (compatible)

**Integration Strategy**:
- Can replace existing checkbox groups with toggle groups (minor refactor)
- Can replace dropdown with radio cards (enhances UX)
- Keep collapsible wrapper (proven pattern)

---

## ARCHIE Component References

All components used are from the shadcn/ui library (already installed in project):

- `ToggleGroup` + `ToggleGroupItem` - `/components/ui/toggle-group`
- `RadioGroup` + `RadioGroupItem` - `/components/ui/radio-group`
- `Card` + `CardHeader` + `CardContent` - `/components/ui/card`
- `Badge` - `/components/ui/badge`
- `Label` - `/components/ui/label`
- `Button` - `/components/ui/button`
- `Switch` - `/components/ui/switch` (Solution 4)
- `Select` - `/components/ui/select` (Solution 5)
- `Checkbox` - `/components/ui/checkbox` (Solution 3)

**Quality Scores** (ARCHIE catalogue):
- Toggle Group pattern: 80/100 (animateui-demo-primitives-radix-toggle-group)
- Radio Group: 85/100 (shadcn standard)
- Card layouts: 90/100 (shadcn standard)
- Multi-Selector: 70/100 (spectrumui-multiple-selector - external dependency)

---

## Implementation Guidance

### Next Steps

1. **Review with team**: Compare with existing design spec, choose best approach
2. **Prototype**: Build Solution 1 in `/frontend/src/components/Settings.tsx`
3. **Test**: Validate with real model data, test accessibility
4. **Iterate**: A/B test with Solution 4 if compactness becomes priority

### File Structure (Recommended)

```
frontend/src/components/
  Settings/
    Settings.tsx              # Main settings modal/panel
    ModelSelector.tsx         # Solution 1 implementation
    CouncilToggleGroup.tsx    # Council models toggle group
    ChairmanRadioCards.tsx    # Chairman radio card list
```

### Integration with Existing Code

The existing `Settings.jsx` component can integrate Solution 1:

```tsx
import { ModelSelector } from './Settings/ModelSelector';

export function Settings({ isOpen, onClose }) {
  const [config, setConfig] = useState({
    councilModels: [],
    chairmanModel: null
  });

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Settings</DialogTitle>
        </DialogHeader>

        <ModelSelector
          models={availableModels}
          config={config}
          onChange={setConfig}
        />

        <DialogFooter>
          <Button onClick={() => saveConfig(config)}>
            Save Configuration
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

---

## Accessibility Notes

All recommended solutions use shadcn/ui components built on Radix primitives, ensuring:

- Keyboard navigation (Tab, Space, Enter, Arrow keys)
- Screen reader support (proper ARIA labels and roles)
- Focus management (visible focus indicators)
- Disabled state handling (proper aria-disabled attributes)

**Critical**: Ensure `Label` components use proper `htmlFor` attributes linking to form controls for screen reader compatibility.

---

## Responsive Behavior

**Desktop (260px sidebar)**:
- Toggle Group: 3-column grid for council models
- Radio Cards: Single column, compact padding

**Mobile (<640px)**:
- Settings component becomes full-screen modal
- Toggle Group: 2-column grid (better touch targets)
- Radio Cards: Same layout (full width already)

**Tablet (641-1024px)**:
- Sidebar expands to 320px (if space available)
- Toggle Group: Can expand to 4-column grid
- Radio Cards: Slightly larger padding

---

**Philosophy**: These solutions provide **guidance, not obligations**. Recommendations based on ARCHIE's 803-component catalogue analysis, but final implementation should adapt to project needs and team preferences.

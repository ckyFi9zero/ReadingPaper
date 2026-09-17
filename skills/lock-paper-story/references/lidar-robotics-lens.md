# LiDAR and robotics perception lens

Use this reference only for LiDAR, point-cloud, adverse-weather, autonomous-driving, or robotics perception manuscripts.

## Evidence fields

Record when available:

- sensor model, channels, returns, scan rate, range, and intensity calibration;
- weather type, intensity, real/simulated/controlled origin, and label source;
- task definition: noise classification, point removal, restoration, segmentation, detection, or downstream robustness;
- representation: point, voxel, pillar, range image, BEV, cylindrical, graph, temporal, or multimodal;
- supervision and annotation mechanism;
- dataset split by scene, sequence, time, location, sensor, and weather;
- baselines under matched inputs, data, backbone, and compute;
- point-level metrics, valid-point retention, distance-binned behavior, runtime, and downstream effect;
- single-frame/multi-frame and offline/real-time boundary.

## Common A/B/C distinctions

Do not classify by checklist alone. Apply the central-claim test.

- Split leakage between adjacent scans is normally A.
- No matched baseline is A only when comparative superiority is central.
- No cross-sensor test is normally B unless sensor independence is claimed.
- No downstream detector result is normally B or C unless downstream improvement is claimed.
- No real-weather test is A only when real-weather performance is central; otherwise narrow to simulated/controlled weather.
- No module ablation is A only when the abstract claims that module causes the gain; otherwise claim end-to-end effectiveness and mark mechanism as unisolated.
- No statistical repeat is A when effects are unstable or conclusions hinge on small differences; it may be B when effects are large and deterministic but uncertainty remains unquantified.

## Bounded gap patterns

Prefer:

```text
It remains unclear whether [specific information/design] improves [specific outcome]
under [data/sensor/weather condition] while preserving [safety-critical property].
```

Avoid:

```text
Existing methods cannot solve adverse-weather point-cloud denoising.
```

## Insight patterns

Accept an insight when it changes interpretation of the task and is supported by a stable contrast, for example:

```text
Weather noise is not always an isolated-outlier problem; under dense scattering,
contextual consistency may be more informative than local sparsity.
```

Do not require universal validity. Attach sensor, weather, dataset, and distance boundaries.

## Safety claim boundary

Point-level denoising improvement does not establish safer driving, better detection, fewer emergency stops, or more robust planning without corresponding downstream evidence. Preserve point-level claims unless downstream evaluation exists.


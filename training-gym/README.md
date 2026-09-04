# GLAW Training Gym

Deterministic, resettable environments for training and evaluating tool-using agents. The foundation separates world state, explicit transitions, tasks, observations, trajectories, evaluators, and rewards. Agents cannot mutate state outside a registered transition. The included synthetic Insurance Claims Gym demonstrates evidence-grounded policy, claim-line, and review workflows.

## Example

```ts
import { SpreadsheetGym } from './gyms/spreadsheet/index.ts';
import { Gym } from './sdk.ts';

const gym = new Gym(new SpreadsheetGym());
await gym.reset({ seed: 281192 });
await gym.step({ tool: 'spreadsheet.set_formula', arguments: { cell: 'C2', formula: '=A2-B2' } });
console.log(await gym.evaluate());
```

Binary policy/document parsers, browser drivers, isolated workers, and external model adapters are explicit extension points; they are not silently simulated by this package.

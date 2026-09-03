# GLAW Training Gym Architecture

The foundation is organized as Environment + Dataset + Task + Agent + Tool + State + Trajectory + Evaluator + Reward + Replay. World-state changes occur only through explicit transitions. Episodes are seeded, resettable, snapshotable, and replayable. Exact evaluators operate before any semantic judge. The acting agent never controls evaluation or hidden ground truth.

Phase 1 contains the typed contract, deterministic state manager, task validation/generation, trajectory recorder/export, evaluator, sandbox policy, and Spreadsheet Gym. Later adapters must implement the same contract for CRM, communication, legal, insurance, and construction domains.

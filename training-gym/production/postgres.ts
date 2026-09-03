import type { DurableEpisodeRecord, EpisodeRepository } from './persistence.ts';

export interface SqlClient { query<T = Record<string, unknown>>(text: string, values?: readonly unknown[]): Promise<{ rows: T[] }> }
type Row = { id:string; organization_id:string; experiment_id:string; task_id:string; status:DurableEpisodeRecord['status']; seed:number|string; version_pins:Record<string,string|number>; created_at:string; updated_at:string };
function mapRow(row: Row): DurableEpisodeRecord { return { id:row.id, organizationId:row.organization_id, experimentId:row.experiment_id, taskId:row.task_id, status:row.status, seed:Number(row.seed), versionPins:row.version_pins, createdAt:row.created_at, updatedAt:row.updated_at }; }

export class PostgresEpisodeRepository implements EpisodeRepository {
  private readonly db: SqlClient;
  constructor(db: SqlClient) { this.db = db; }
  async create(record: DurableEpisodeRecord, idempotencyKey: string): Promise<DurableEpisodeRecord> { const result = await this.db.query<Row>(`insert into gym_episodes (id, organization_id, experiment_id, task_id, status, seed, version_pins, idempotency_key) values ($1,$2,$3,$4,$5,$6,$7,$8) on conflict (idempotency_key) do update set id=id returning id, organization_id, experiment_id, task_id, status, seed, version_pins, created_at, updated_at`, [record.id,record.organizationId,record.experimentId,record.taskId,record.status,record.seed,JSON.stringify(record.versionPins),idempotencyKey]); const row = result.rows[0]; if (!row) throw new Error('Episode insert returned no row'); return mapRow(row); }
  async get(id: string, organizationId: string): Promise<DurableEpisodeRecord | undefined> { const result = await this.db.query<Row>('select id, organization_id, experiment_id, task_id, status, seed, version_pins, created_at, updated_at from gym_episodes where id=$1 and organization_id=$2', [id,organizationId]); return result.rows[0] ? mapRow(result.rows[0]) : undefined; }
  async transition(id: string, organizationId: string, transition: { to: DurableEpisodeRecord['status'] }): Promise<DurableEpisodeRecord> { const result = await this.db.query<Row>('update gym_episodes set status=$3, updated_at=now() where id=$1 and organization_id=$2 returning id, organization_id, experiment_id, task_id, status, seed, version_pins, created_at, updated_at', [id,organizationId,transition.to]); const row = result.rows[0]; if (!row) throw new Error('Episode not found'); return mapRow(row); }
}

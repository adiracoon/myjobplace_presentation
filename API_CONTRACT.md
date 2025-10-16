| Method | Path           | Description                       | Status           |
|-------:|----------------|-----------------------------------|------------------|
|   GET  | /health        | Service health                    | ✅ Implemented   |
|   GET  | /readyz        | Readiness check                   | ✅ Implemented   |
|   GET  | /jobs          | List jobs (filters & pagination)  | ✅ Implemented   |
|   GET  | /jobs/count    | Count jobs with filters           | ✅ Implemented   |
|  POST  | /jobs          | Create job (409 on duplicates)    | ✅ Implemented   |
|   PUT  | /jobs/{id}     | Update job (partial, 409 conflict)| ✅ Implemented   |
| DELETE | /jobs/{id}     | Soft delete (idempotent)          | ✅ Implemented   |

"""
\"\"\"Database models using SQLModel\"\"\"
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from pydantic import field_validator, model_validator, ConfigDict
class JobBase(SQLModel):
    \"\"\"Base model for Job (shared fields)\"\"\"
    title: str = Field(max_length=500, index=False)
    company: str = Field(max_length=200, index=False)
    url: Optional[str] = Field(default=None, max_length=2000)
    source: Optional[str] = Field(default=None, max_length=50)
    org: Optional[str] = Field(default=None, max_length=100)
    external_id: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=200)
    posted_at: Optional[datetime] = Field(default=None, index=True)
    updated_ext: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True, index=True)
    is_demo: bool = Field(default=False)
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    @model_validator(mode='after')
    def validate_source_external_id(self):
        \"\"\"Both source and external_id must be provided together\"\"\"
        if self.source and not self.external_id:
            raise ValueError('external_id required when source is provided')
        if self.external_id and not self.source:
            raise ValueError('source required when external_id is provided')
        return self
class Job(JobBase, table=True):
    \"\"\"Job table (includes ID and timestamps)\"\"\"
    __tablename__ = "job"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None, index=True)
class JobRead(JobBase):
    \"\"\"Job response model\"\"\"
    model_config = ConfigDict(from_attributes=True)
id: int
    created_at: datetime
    deleted_at: Optional[datetime] = None
class JobUpdate(SQLModel):
    \"\"\"Job update model (all fields optional)\"\"\"
    title: Optional[str] = Field(default=None, max_length=500)
    company: Optional[str] = Field(default=None, max_length=200)
    url: Optional[str] = Field(default=None, max_length=2000)
    source: Optional[str] = Field(default=None, max_length=50)
    org: Optional[str] = Field(default=None, max_length=100)
    external_id: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=200)
    posted_at: Optional[datetime] = None
    updated_ext: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_demo: Optional[bool] = None
class ImportCheckpoint(SQLModel, table=True):
    \"\"\"Track import runs per source+org\"\"\"
    __tablename__ = "import_checkpoint"
    source: str = Field(primary_key=True, max_length=50)
    org: str = Field(primary_key=True, max_length=100)
    last_run_at: datetime
    last_success_at: datetime
    jobs_imported: int = Field(default=0)
    jobs_updated: int = Field(default=0)
    jobs_failed: int = Field(default=0)
    status: str = Field(max_length=20)
"""
"""Database models using SQLModel (clean, fixed indentation, Pydantic v2)"""
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from pydantic import field_validator, model_validator, ConfigDict
class JobBase(SQLModel):
    """Base model for Job (shared fields)"""
    title: str = Field(max_length=500, index=False)
    company: str = Field(max_length=200, index=False)
    url: Optional[str] = Field(default=None, max_length=2000)
    source: Optional[str] = Field(default=None, max_length=50)
    org: Optional[str] = Field(default=None, max_length=100)
    external_id: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=200)
    posted_at: Optional[datetime] = Field(default=None, index=True)
    updated_ext: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True, index=True)
    is_demo: bool = Field(default=False)
    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v
    @model_validator(mode="after")
    def validate_source_external_id(self):
        """Both source and external_id must be provided together"""
        if self.source and not self.external_id:
            raise ValueError("external_id required when source is provided")
        if self.external_id and not self.source:
            raise ValueError("source required when external_id is provided")
        return self
class Job(JobBase, table=True):
    """Job table (includes ID and timestamps)"""
    __tablename__ = "job"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None, index=True)
class JobRead(JobBase):
    """Job response model (for FastAPI responses)"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    deleted_at: Optional[datetime] = None
class JobUpdate(SQLModel):
    """Job update model (all fields optional)"""
    title: Optional[str] = Field(default=None, max_length=500)
    company: Optional[str] = Field(default=None, max_length=200)
    url: Optional[str] = Field(default=None, max_length=2000)
    source: Optional[str] = Field(default=None, max_length=50)
    org: Optional[str] = Field(default=None, max_length=100)
    external_id: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=200)
    posted_at: Optional[datetime] = None
    updated_ext: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_demo: Optional[bool] = None
class ImportCheckpoint(SQLModel, table=True):
    """Track import runs per source+org"""
    __tablename__ = "import_checkpoint"
    source: str = Field(primary_key=True, max_length=50)
    org: str = Field(primary_key=True, max_length=100)
    last_run_at: datetime
    last_success_at: datetime
    jobs_imported: int = Field(default=0)
    jobs_updated: int = Field(default=0)
    jobs_failed: int = Field(default=0)
    status: str = Field(max_length=20)
